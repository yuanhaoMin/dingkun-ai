import json
import logging
from app.model.session_manager import SessionManager
from app.util.json_util import fix_and_parse_json
from app.util.file_util import create_prompt_from_template_file
from app.util.time_utll import get_current_date_and_day
from fastapi import HTTPException
from typing import List


def determine_registration_function_call(
    session_id: str, user_message: str, department_names: List[str], history_data=None
) -> str:
    # 测试中发现如果帮助中心和访客登记同时开启, 会话会混淆. 需要保证这里是临时会话
    temp_session_id = session_id + "_temp"
    session_manager = SessionManager()
    department_str = ",".join(department_names) if department_names else ""

    system_message = _prepare_system_message(department_str)

    if history_data:
        parsed_history_data = json.loads(history_data)
        if _contains_non_null_values(parsed_history_data):
            user_message = f"Current situation: {history_data}. " + user_message

    conversation = session_manager.retrieve_or_create_session_conversation(
        session_id=temp_session_id, system_message=system_message
    )

    for _ in range(3):  # 3 attempts
        ai_message = conversation.ask(
            user_message + """(Only return...Correct comma placement.) """
        )
        try:
            parsed_json = fix_and_parse_json(ai_message)
            session_manager.remove_session(temp_session_id)
            return parsed_json
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON. AI's response was: {ai_message}")
            conversation.ask(
                f"Failed to parse JSON with error: \n{e}\nPlease check your JSON format and only reply with valid JSON data"
            )
    raise HTTPException(
        status_code=500,
        detail="Failed to parse JSON after 3 attempts. Please check your JSON format and only reply with valid JSON data",
    )


def _prepare_system_message(departments_str: str) -> str:
    current_date, day_of_week = get_current_date_and_day()
    replacements = {
        "current_date:": current_date,
        "day_of_week:": day_of_week,
        "departments:": departments_str,
    }
    return create_prompt_from_template_file(
        filename="visitor_register_prompt", replacements=replacements
    )


def _contains_non_null_values(data: any) -> bool:
    if isinstance(data, dict):
        return any(_contains_non_null_values(value) for value in data.values())
    elif isinstance(data, list):
        return any(_contains_non_null_values(item) for item in data)
    else:
        return data is not None



