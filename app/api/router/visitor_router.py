import json
import logging
from fastapi import APIRouter
from app.util.chinese_phonetic_util import PyEditDistance
from app.api.error.json_errors import InvalidAIGeneratedJSONError
from app.constant.jsonschema.visitor_json_schema import visitor_register_schema, companion_register_schema
from app.logic import visitor_logic
from app.model.schema.visitor_schema import DetermineFunctionCallRequest, DetermineFunctionCallRequestSmart
from app.util.data_validator import validate_json

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
        department_names
    )

    return result_str


@router.post("/companion/registration/function-call")
def determine_companion_registration_function_call(request: DetermineFunctionCallRequest):
    result_str = visitor_logic.determine_companion_registration_function_call(request.text)

    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        raise InvalidAIGeneratedJSONError(detail="Failed to parse JSON from function result.")

    valid, errors = validate_json(result, companion_register_schema)
    if not valid:
        raise InvalidAIGeneratedJSONError(detail=", ".join(errors))

    return result


def handle_department(department, department_names, department_persons_dict):
    department_name = department.get("name")
    if department_name:
        department_names.append(department_name)

    persons = department.get("persons", [])
    person_names = [person["personName"] for person in persons]
    if person_names:
        department_persons_dict[department_name] = person_names
