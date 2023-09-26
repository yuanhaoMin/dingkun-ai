import json
import logging
from fastapi import APIRouter
from app.logic import visitor_logic
from app.model.pydantic_schema.visitor_schemas import (
    DetermineFunctionCallRequestSmart,
    DetermineFunctionCallResponse,
)
from app.util.chinese_phonetic_util import PyEditDistance

router = APIRouter(
    prefix="/visitor",
    tags=["visitor"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/registration/function-call")
def determine_registration_function_call(request: DetermineFunctionCallRequestSmart):
    department_codes = {}
    person_ids = {}
    department_names = []
    department_persons_dict = {}
    if request.departmentsJson is not None:
        try:
            # 解析 departmentsJson
            departments_data = json.loads(request.departmentsJson)
            department_codes = {department['name']: department['departmentCode'] for department in
                                departments_data}
            person_ids = {person['personName']: person['id'] for department in departments_data for person in
                          department['persons']}

            for department in departments_data:
                handle_department(department, department_names, department_persons_dict)
                subdepartments = department.get("subdepartments", [])
                for subdepartment in subdepartments:
                    handle_department(subdepartment, department_names, department_persons_dict)
        except json.JSONDecodeError:
            logger.warning("Error: Failed to parse departmentsJson!")

    result_str = visitor_logic.determine_registration_function_call(
        request.sessionId,
        request.text,
        department_names,
        request.historyData
    )
    pyedit = PyEditDistance(department_persons_dict)
    optimized_data = optimize_entry(result_str, pyedit, department_codes, person_ids)
    final_result = {
        'session_id': request.sessionId,
        'data': optimized_data,
    }

    return final_result


def handle_department(department, department_names, department_persons_dict):
    department_name = department.get("name")
    if department_name:
        department_names.append(department_name)

    persons = department.get("persons", [])
    person_names = [person["personName"] for person in persons]
    if person_names:
        department_persons_dict[department_name] = person_names


def optimize_entry(entry, pyedit, department_codes, person_ids):
    visitor_information = entry.get('visitor_information', {})
    visit_details = entry.get('visit_details', {})

    name = visitor_information.get('name') or ""
    visited_department = visit_details.get('visited_department') or ""

    if not name and not visited_department:
        # 两者都没有，不做处理
        return entry

    if name and visited_department:
        # 部门和名字都做最近处理的优化
        relationship, closest_department, _, closest_person, _ = pyedit.get_relationship(visited_department, name)

        # 部门和人员都有
        if relationship == "受访部门存在，受访人存在":
            entry['visit_details']['visited_department'] = closest_department
            entry['visitor_information']['name'] = closest_person
            entry['departmentCode'] = department_codes.get(closest_department)
            entry['id'] = person_ids.get(closest_person)
        elif relationship == "受访部门存在，受访人不存在":
            entry['visit_details']['visited_department'] = closest_department
            entry['departmentCode'] = department_codes.get(closest_department)
        elif relationship == "受访部门不存在，受访人存在":
            entry['visitor_information']['name'] = closest_person
            entry['id'] = person_ids.get(closest_person)
        elif relationship == "受访部门存在，受访人不对应":
            entry['visit_details']['visited_department'] = closest_department
            entry['visitor_information']['name'] = closest_person
            entry['departmentCode'] = department_codes.get(closest_department)
            entry['id'] = person_ids.get(closest_person)
        elif relationship == "受访部门自动关联，受访人存在":
            entry['visit_details']['visited_department'] = closest_department  # 这里使用自动关联的 closest_department
            entry['visitor_information']['name'] = closest_person
            entry['departmentCode'] = department_codes.get(closest_department)
            entry['id'] = person_ids.get(closest_person)
        else:
            entry['departmentCode'] = None
            entry['id'] = None

    elif visited_department:
        relationship, closest_department, _, closest_person, _ = pyedit.get_relationship(visited_department, '')
        # 只有部门
        entry['visit_details']['visited_department'] = closest_department
        entry['departmentCode'] = department_codes.get(closest_department)

    elif name:
        relationship, closest_department, _, closest_person, _ = pyedit.get_relationship('', name)
        # 只有名字
        entry['visitor_information']['name'] = closest_person
        entry['id'] = person_ids.get(closest_person)

    return entry

