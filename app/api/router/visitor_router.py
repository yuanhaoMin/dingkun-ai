import json
import logging
from fastapi import APIRouter
from app.logic import visitor_logic
from app.model.schema.visitor_schema import DetermineFunctionCallRequest, DetermineFunctionCallRequestSmart


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
    ai_message = ""
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

    final_result = {
        'session_id': request.sessionId,
        'data': result_str,
        'ai_message': ai_message
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
