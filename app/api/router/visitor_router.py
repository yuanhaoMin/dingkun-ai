import logging
import json
from fastapi import APIRouter
from app.logic import visitor_logic
from app.model.schema.visitor_schema import DetermineFunctionCallRequestSmart
from app.util.chinese_phonetic_util import PyEditDistance

router = APIRouter(
    prefix="/visitor",
    tags=["visitor"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/smart-registration/function-call")
def smart_determine_registration_function_call(request: DetermineFunctionCallRequestSmart):
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

    result_str = visitor_logic.smart_determine_companion_registration_function_call(
        request.sessionId,
        request.text,
        department_names
    )

    pyedit = PyEditDistance(department_persons_dict)

    for entry in result_str:
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
                entry['departmentCode'] = department_codes.get(closest_department)
                entry['id'] = None
            elif relationship == "受访部门不存在，受访人存在":
                entry['contactPerson'] = closest_person
                entry['departmentCode'] = None
                entry['id'] = person_ids.get(closest_person)
            elif relationship == "受访部门存在，受访人不对应":
                entry['contactOrg'] = closest_department
                entry['contactPerson'] = closest_person
                entry['departmentCode'] = department_codes.get(closest_department)
                entry['id'] = person_ids.get(closest_person)
            else:
                entry['departmentCode'] = None
                entry['id'] = None

        final_result = {
            'sessionId': request.sessionId,
            'data': result_str
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
