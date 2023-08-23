import json
from fastapi import APIRouter, HTTPException
from app.api.error.json_errors import InvalidAIGeneratedJSONError
from app.constant.jsonschema.visitor_json_schema import visitor_register_schema, companion_register_schema, \
    visitor_register_schema_old, companion_register_schema_old
from app.logic import visitor_logic
from app.logic.visitor_logic import SESSION_STORE, update_session_data, prune_sessions, remove_expired_sessions
from app.model.schema.visitor_schema import DetermineFunctionCallRequest, DetermineFunctionCallRequestOld
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
