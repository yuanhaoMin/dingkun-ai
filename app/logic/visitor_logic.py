import json

from app.logic.conversation_training_logic import HistoryBasedTrainingManager
from app.util.json_util import fix_and_parse_json
from app.util.openai_util import completion, Conversation
from app.util.text_util import create_prompt_from_template_file
from datetime import datetime, timedelta
from collections import OrderedDict
from typing import List
import logging

SESSION_STORE = OrderedDict()
MAX_ATTEMPTS = 3
MAX_SESSION_COUNT = 1000
current_date = datetime.now().strftime("%Y-%m-%d")
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today = datetime.today().date()
day_of_week = days[today.weekday()]


def determine_registration_function_call(text: str) -> str:
    replacements = {"current_date:": current_date,
                    "day_of_week:": day_of_week}
    prompt = create_prompt_from_template_file(
        filename="visitor_register_prompts", replacements=replacements
    )
    messages = [{"role": "system", "content": prompt}]
    messages.extend(HistoryBasedTrainingManager.get_visitor_register_messages())
    messages.append({"role": "user", "content": text})
    return completion(messages)


def determine_companion_registration_function_call(text: str) -> str:
    prompt = create_prompt_from_template_file(
        filename="visitor_companion_register_prompts", replacements=None
    )
    messages = [{"role": "system", "content": prompt}]
    messages.extend(HistoryBasedTrainingManager.get_visitor_companion_register_messages())
    messages.append({"role": "user", "content": text})
    return completion(messages)


# logging.basicConfig(level=logging.INFO)
# TEMPLATE = {
#     "appointmentTime": None,
#     "companyName": None,
#     "contactOrg": None,
#     "contactPerson": None,
#     "idCard": None,
#     "plateNumber": None,
#     "remark": None,
#     "useName": None,
#     "usePhone": None,
#     "visitingReason": None
# }
#
#
# def update_session_data(session_id, new_data):
#     logging.info(f"Updating session {session_id} with data: {new_data}")
#
#     old_data = SESSION_STORE.get(session_id, TEMPLATE.copy())
#     logging.info(f"Old data: {old_data}")
#
#     for key, value in new_data.items():
#         if value is not None:
#             old_data[key] = value
#
#     old_data["timestamp"] = datetime.now()
#
#     SESSION_STORE[session_id] = old_data
#
#     if not old_data.get("appointmentTime"):
#         old_data["appointmentTime"] = datetime.now().strftime("%Y-%m-%d")
#
#     logging.info(f"Final updated data: {old_data}")
#
#     return old_data


def prune_sessions():
    # 每次添加新的 sessionId 或更新数据时，检查长度，并移除最旧直到满足条件
    while len(SESSION_STORE) > MAX_SESSION_COUNT:
        SESSION_STORE.popitem(last=False)


def remove_expired_sessions():
    expiration_time = datetime.now() - timedelta(minutes=5)
    expired_keys = [key for key, value in SESSION_STORE.items() if
                    value.get('timestamp') and value.get('timestamp') < expiration_time]

    for key, value in SESSION_STORE.items():
        if not value.get('timestamp'):
            logging.warning(f"Session {key} lacks a timestamp!")

    for key in expired_keys:
        SESSION_STORE.pop(key)


def smart_determine_companion_registration_function_call(sessionId: str, text: str, department_names: List[str]) -> str:
    if not department_names:
        department_names = []
    departments_str = ",".join(department_names)
    replacements = {"current_date:": current_date,
                    "day_of_week:": day_of_week,
                    "departments:": departments_str
                    }
    prompt = create_prompt_from_template_file(
        filename="visitor_register_smart_prompts", replacements=replacements
    )

    if sessionId not in SESSION_STORE:
        conversation = Conversation(prompt, num_of_round=5)
        SESSION_STORE[sessionId] = {
            "conversation": conversation,
            "timestamp": datetime.now()
        }
    else:
        conversation = SESSION_STORE[sessionId]["conversation"]
        SESSION_STORE[sessionId]["timestamp"] = datetime.now()

    attempts = 0
    while attempts < MAX_ATTEMPTS:
        response = conversation.ask(text+'''(Ignore the irrelevant remarks made by the user, only return the specified 
        JSON array, and it must be related to the context. Even if there are no accompanying personnel, the complete 
        JSON array must be returned. That is, both objects must exist. Additionally, always retain the previously entered 
        JSON data unless the user explicitly requests a change in a specific item.
        ''')
        conversation.save_messages_to_file()
        remove_expired_sessions()
        prune_sessions()
        try:
            # 尝试修复和解析 JSON
            fixed_response = fix_and_parse_json(response)
            return fixed_response  # 如果成功，直接返回修复后的 JSON
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON. AI's response was: {response}")
            # 如果失败，捕获异常并告知 AI
            text = "Please check your JSON format and only reply with valid JSON data."
            conversation.ask(text)
            attempts += 1

    # 超过最大尝试次数，返回 None
    return {}
