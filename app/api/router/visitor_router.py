import json
import re
from fastapi import APIRouter, HTTPException
from app.api.error.json_errors import InvalidAIGeneratedJSONError
from app.constant.jsonschema.visitor_json_schema import visitor_register_schema, companion_register_schema, \
    visitor_register_schema_old, companion_register_schema_old
from app.logic import visitor_logic
from app.logic.visitor_logic import SESSION_STORE, update_session_data, prune_sessions, remove_expired_sessions
from app.model.schema.visitor_schema import DetermineFunctionCallRequest, DetermineFunctionCallRequestOld, \
    DetermineFunctionCallRequestSmart
from app.util.chinese_phonetic_util import PyEditDistance
from app.util.data_validator import validate_json
import logging

router = APIRouter(
    prefix="/visitor",
    tags=["visitor"],
)

logging.basicConfig(level=logging.INFO)


# @router.post("/registration/function-call")
# def determine_registration_function_call(request: DetermineFunctionCallRequest):
#     result_str = visitor_logic.determine_registration_function_call(request.text)
#
#     try:
#         result = json.loads(result_str)
#     except json.JSONDecodeError:
#         raise InvalidAIGeneratedJSONError(detail="Failed to parse JSON from function result.")
#
#     valid, errors = validate_json(result, visitor_register_schema)
#     if not valid:
#         raise InvalidAIGeneratedJSONError(detail=", ".join(errors))
#
#     return result
#
#
# @router.post("/companion/registration/function-call")
# def determine_companion_registration_function_call(request: DetermineFunctionCallRequest):
#     result_str = visitor_logic.determine_companion_registration_function_call(request.text)
#
#     try:
#         result = json.loads(result_str)
#     except json.JSONDecodeError:
#         raise InvalidAIGeneratedJSONError(detail="Failed to parse JSON from function result.")
#
#     valid, errors = validate_json(result, companion_register_schema)
#     if not valid:
#         raise InvalidAIGeneratedJSONError(detail=", ".join(errors))
#
#     return result

@router.post("/registration/function-call")
def determine_registration_function_call(request: DetermineFunctionCallRequestOld):
    department_names_list = request.departmentNames
    result_str = visitor_logic.determine_registration_function_call_old(request.text, department_names_list)
    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        raise InvalidAIGeneratedJSONError(detail="Failed to parse JSON from function result.")

    valid, errors = validate_json(result, visitor_register_schema_old)
    if not valid:
        raise InvalidAIGeneratedJSONError(detail=", ".join(errors))

    session_id = request.sessionId
    logging.info(f"Received request with sessionId: {session_id}")
    logging.info(f"Initial data: {result}")

    # 移除过期的 sessions
    remove_expired_sessions()

    # 更新 session 数据
    updated_data = update_session_data(session_id, result)
    logging.info(f"Updated data after session update: {updated_data}")
    # 检查并移除多余的 sessions
    prune_sessions()
    result = {k: v for k, v in updated_data.items() if k != "timestamp"}
    return result


@router.post("/companion/registration/function-call")
def determine_companion_registration_function_call(request: DetermineFunctionCallRequestOld):
    result_str = visitor_logic.determine_companion_registration_function_call_old(request.text)

    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        raise InvalidAIGeneratedJSONError(detail="Failed to parse JSON from function result.")

    valid, errors = validate_json(result, companion_register_schema_old)
    if not valid:
        raise InvalidAIGeneratedJSONError(detail=", ".join(errors))

    return result


@router.post("/smart-registration/function-call")
def smart_determine_registration_function_call(request: DetermineFunctionCallRequestSmart):
    # 解析departmentsJson字段以获取部门名称和部门-人员关系
    try:
        # 解析 departmentsJson
        departments_data = json.loads(request.departmentsJson)
        department_codes = {department['name']: department['departmentCode'] for department in
                            departments_data}
        person_ids = {person['personName']: person['id'] for department in departments_data for person in
                      department['persons']}
    except json.JSONDecodeError:
        print("Error: Failed to parse departmentsJson!")
        return {}

    department_names = []
    department_persons_dict = {}

    for department in departments_data:
        department_name = department.get("name")
        if department_name:
            department_names.append(department_name)

        persons = department.get("persons", [])
        person_names = [person["personName"] for person in persons]
        if person_names:
            department_persons_dict[department_name] = person_names

        subdepartments = department.get("subdepartments", [])
        for subdepartment in subdepartments:
            subdepartment_name = subdepartment.get("name")
            if subdepartment_name:
                department_names.append(subdepartment_name)
            persons = subdepartment.get("persons", [])
            person_names = [person["personName"] for person in persons]
            if person_names:
                department_persons_dict[subdepartment_name] = person_names

    result_str = visitor_logic.smart_determine_companion_registration_function_call(
        request.sessionId,
        request.text,
        department_names
    )

    result = json.loads(result_str)

    pyedit = PyEditDistance(department_persons_dict)

    for entry in result:
        contact_person = entry.get('contactPerson')
        contact_org = entry.get('contactOrg')

        if contact_person and contact_org:
            relationship, closest_department, _, closest_person, _ = pyedit.get_relationship(contact_org,
                                                                                             contact_person)

            if relationship == "受访部门存在，受访人存在":
                entry['contactOrg'] = closest_department
                entry['contactPerson'] = closest_person
                entry['departmentCode'] = department_codes.get(closest_department)
                entry['id'] = person_ids.get(closest_person)
            elif relationship == "受访部门存在，受访人不存在":
                entry['contactOrg'] = closest_department
                # entry['contactPerson'] = None
                entry['departmentCode'] = department_codes.get(closest_department)
                entry['id'] = None
            elif relationship == "受访部门不存在，受访人存在":
                # entry['contactOrg'] = None
                entry['contactPerson'] = closest_person
                entry['message'] = "受访部门不存在，受访人存在"
                entry['departmentCode'] = None
                entry['id'] = person_ids.get(closest_person)
            elif relationship == "受访部门存在，受访人不对应":
                entry['contactOrg'] = closest_department
                entry['contactPerson'] = closest_person
                entry['departmentCode'] = department_codes.get(closest_department)
                entry['id'] = person_ids.get(closest_person)
            else:
                # entry['contactOrg'] = None
                # entry['contactPerson'] = None
                entry['departmentCode'] = None
                entry['id'] = None

        final_result = {
            'sessionId': request.sessionId,
            'data': result
        }
    print("final_result:", final_result)
    return final_result
