import json

from fastapi import APIRouter

from app.api.error.json_errors import InvalidAIGeneratedJSONError
from app.constant.jsonschema.visitor_json_schema import visitor_register_schema, companion_register_schema
from app.logic import visitor_logic
from app.model.schema.visitor_schema import DetermineFunctionCallRequest
from app.util.data_validator import validate_json

router = APIRouter(
    prefix="/visitor",
    tags=["visitor"],
)


@router.post("/registration/function-call")
async def determine_registration_function_call(request: DetermineFunctionCallRequest):
    result_str = visitor_logic.determine_registration_function_call(request.text)

    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        raise InvalidAIGeneratedJSONError(detail="Failed to parse JSON from function result.")

    valid, errors = validate_json(result, visitor_register_schema)
    if not valid:
        raise InvalidAIGeneratedJSONError(detail=", ".join(errors))

    return result


@router.post("/companion/registration/function-call")
async def determine_companion_registration_function_call(request: DetermineFunctionCallRequest):
    result_str = visitor_logic.determine_companion_registration_function_call(request.text)

    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        raise InvalidAIGeneratedJSONError(detail="Failed to parse JSON from function result.")

    valid, errors = validate_json(result, companion_register_schema)
    if not valid:
        raise InvalidAIGeneratedJSONError(detail=", ".join(errors))

    return result
