import json

from app.db.SessionManager import SessionManager
from app.util.json_util import fix_and_parse_json
from app.util.openai_util import completion, Conversation
from app.util.text_util import create_prompt_from_template_file
from datetime import datetime, timedelta
from typing import List
import logging
from app.util.time_utll import get_current_date_and_day

MAX_ATTEMPTS = 3

session_manager = SessionManager()


def determine_registration_function_call(sessionId: str, text: str, department_names: List[str],
                                         history_data=None) -> str:
    if not department_names:
        department_names = []
    current_date, day_of_week = get_current_date_and_day()
    departments_str = ",".join(department_names)
    replacements = {"current_date:": current_date,
                    "day_of_week:": day_of_week,
                    "departments:": departments_str
                    }
    prompt = create_prompt_from_template_file(
        filename="visitor_register_prompts", replacements=replacements
    )
    if history_data:
        parsed_history_data = json.loads(history_data)
        if contains_non_null_values(parsed_history_data):
            text = f"Current situation: {history_data}. " + text

    session = session_manager.get_session(sessionId)
    if not session:
        conversation = Conversation(prompt, num_of_round=5)
        session_manager.add_or_update_session(sessionId, conversation)
        session = session_manager.get_session(sessionId)
    else:
        conversation = session["conversation"]

    attempts = 0
    while attempts < MAX_ATTEMPTS:
        response = conversation.ask(text + '''(Only return the specified JSON array relevant to the context, even if 
        user requests do not align with the pre-defined scenario. Even without accompanying personnel, return the 
        complete array with both objects. Retain the previously entered JSON unless explicitly changed by the user. 
        Ensure: 1. Proper bracket pairing: Each '{' matches with '}', and each '[' with ']'. 2. Correct comma 
        placement: Ensure no trailing comma after the last element or key-value pair.) '''
                                    )
        conversation.save_messages_to_file()
        session_manager.remove_expired_sessions()
        session_manager.prune_sessions()
        try:
            # 尝试修复和解析 JSON
            fixed_response = fix_and_parse_json(response)
            # 保存这次的响应作为下一次的"之前的响应"
            session["previous_response"] = fixed_response

            return fixed_response  # 如果成功，直接返回修复后的 JSON
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON. AI's response was: {response}")
            # 如果失败，捕获异常并告知 AI
            text = "Please check your JSON format and only reply with valid JSON data."
            conversation.ask(text)
            attempts += 1

    # 超过最大尝试次数，返回 None
    return {}


def contains_non_null_values(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if contains_non_null_values(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if contains_non_null_values(item):
                return True
    else:
        if data is not None:
            return True
    return False
