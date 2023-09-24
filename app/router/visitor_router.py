import json
import logging
from fastapi import APIRouter
from app.logic import visitor_logic
from app.model.pydantic_schema.visitor_schemas import (
    DetermineFunctionCallRequestSmart,
    DetermineFunctionCallResponse,
)


router = APIRouter(
    prefix="/visitor",
    tags=["visitor"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/registration/function-call")
def determine_registration_function_call(request: DetermineFunctionCallRequestSmart):
    department_names = []
    department_persons_dict = {}
    if request.departmentsJson is not None:
        try:
            # 解析 departmentsJson
            departments_data = json.loads(request.departmentsJson)
            department_codes = {
                department["name"]: department["departmentCode"]
                for department in departments_data
            }
            person_ids = {
                person["personName"]: person["id"]
                for department in departments_data
                for person in department["persons"]
            }

            for department in departments_data:
                handle_department(department, department_names, department_persons_dict)
                subdepartments = department.get("subdepartments", [])
                for subdepartment in subdepartments:
                    handle_department(
                        subdepartment, department_names, department_persons_dict
                    )
        except json.JSONDecodeError:
            logger.warning("Error: Failed to parse departmentsJson!")

    function_call = visitor_logic.determine_registration_function_call(
        request.sessionId, request.text, department_names, request.historyData
    )
    return DetermineFunctionCallResponse(
        sessionId=request.sessionId, data=function_call
    )


def handle_department(department, department_names, department_persons_dict):
    department_name = department.get("name")
    if department_name:
        department_names.append(department_name)

    persons = department.get("persons", [])
    person_names = [person["personName"] for person in persons]
    if person_names:
        department_persons_dict[department_name] = person_names
