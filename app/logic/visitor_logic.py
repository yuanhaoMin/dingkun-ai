from app.logic.conversation_training_logic import HistoryBasedTrainingManager
from app.util.openai_util import completion
from app.util.text_util import create_prompt_from_template_file
from datetime import datetime, timedelta
from collections import OrderedDict
from typing import List
import logging

SESSION_STORE = OrderedDict()
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


def determine_registration_function_call_old(text: str, department_names: List[str]) -> str:
    if not department_names:
        department_names = []
    departments_str = ",".join(department_names)
    replacements = {"current_date:": current_date,
                    "day_of_week:": day_of_week,
                    "departments:": departments_str
                    }
    prompt = create_prompt_from_template_file(
        filename="visitor_register_prompts_old", replacements=replacements
    )
    messages = [{"role": "system", "content": prompt}]
    messages.extend(HistoryBasedTrainingManager.get_visitor_register_messages_old())
    messages.append({"role": "user", "content": text})
    return completion(messages)


def determine_companion_registration_function_call_old(text: str) -> str:
    prompt = create_prompt_from_template_file(
        filename="visitor_companion_register_prompts_old", replacements=None
    )
    messages = [{"role": "system", "content": prompt}]
    messages.extend(HistoryBasedTrainingManager.get_visitor_companion_register_messages_old())
    messages.append({"role": "user", "content": text})
    return completion(messages)


logging.basicConfig(level=logging.INFO)
TEMPLATE = {
    "appointmentTime": None,
    "companyName": None,
    "contactOrg": None,
    "contactPerson": None,
    "idCard": None,
    "plateNumber": None,
    "remark": None,
    "useName": None,
    "usePhone": None,
    "visitingReason": None
}


def update_session_data(session_id, new_data):
    logging.info(f"Updating session {session_id} with data: {new_data}")

    old_data = SESSION_STORE.get(session_id, TEMPLATE.copy())
    logging.info(f"Old data: {old_data}")

    for key, value in new_data.items():
        if value is not None:
            old_data[key] = value

    old_data["timestamp"] = datetime.now()

    SESSION_STORE[session_id] = old_data

    if not old_data.get("appointmentTime"):
        old_data["appointmentTime"] = datetime.now().strftime("%Y-%m-%d")

    logging.info(f"Final updated data: {old_data}")

    return old_data


def prune_sessions():
    # 每次添加新的 sessionId 或更新数据时，检查长度，并移除最旧的直到满足条件
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
