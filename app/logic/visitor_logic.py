import json

from app.logic.conversation_training_logic import HistoryBasedTrainingManager
from app.util.json_util import fix_and_parse_json
from app.util.openai_util import completion, Conversation
from app.util.text_util import create_prompt_from_template_file
from datetime import datetime, timedelta
from collections import OrderedDict
from typing import List
import logging

from app.util.time_utll import get_current_date_and_day

SESSION_STORE = OrderedDict()
MAX_ATTEMPTS = 3
MAX_SESSION_COUNT = 1000


def determine_registration_function_call(text: str) -> str:
    current_date, day_of_week = get_current_date_and_day()
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


def smart_determine_companion_registration_function_call(sessionId: str, text: str, department_names: List[str],history_data=None) -> str:
    if not department_names:
        department_names = []
    departments_str = ",".join(department_names)
    current_date, day_of_week = get_current_date_and_day()
    replacements = {"current_date:": current_date,
                    "day_of_week:": day_of_week,
                    "departments:": departments_str
                    }
    prompt = create_prompt_from_template_file(
        filename="visitor_register_smart_prompts", replacements=replacements
    )

    if history_data:
        parsed_history_data = json.loads(history_data)
        if contains_non_null_values(parsed_history_data):
            text = f"Current situation: {history_data}. " + text

    if sessionId not in SESSION_STORE:
        conversation = Conversation(prompt, num_of_round=5)
        SESSION_STORE[sessionId] = {
            "conversation": conversation,
            "timestamp": datetime.now(),
            "previous_response": None
        }
    else:
        conversation = SESSION_STORE[sessionId]["conversation"]
        SESSION_STORE[sessionId]["timestamp"] = datetime.now()

    attempts = 0
    while attempts < MAX_ATTEMPTS:
        response = conversation.ask(text + '''(Ignore the irrelevant remarks made by the user, only return the specified 
        JSON array, and it must be related to the context. Even if there are no accompanying personnel, the complete 
        JSON array must be returned. That is, both objects must exist. The "remark" field is used to specify the 
        specific xxx task the visitor is coming to do..
        ''')
        # Only for debugging purpose
        # conversation.save_messages_to_file()
        remove_expired_sessions()
        prune_sessions()
        try:
            fixed_response = fix_and_parse_json(response)

            # 合并之前的数据，如果有的话
            if SESSION_STORE[sessionId].get("previous_response"):
                fixed_response = merge_previous_data(SESSION_STORE[sessionId]["previous_response"], fixed_response)

            # 保存这次的响应作为下一次的"之前的响应"
            SESSION_STORE[sessionId]["previous_response"] = fixed_response

            return fixed_response
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON. AI's response was: {response}")
            # 如果失败，捕获异常并告知 AI
            text = "Please check your JSON format and only reply with valid JSON data."
            conversation.ask(text)
            attempts += 1

    # 超过最大尝试次数，返回 None
    return {}


def merge_previous_data(previous: list, current: list) -> list:
    for i in range(len(previous)):
        prev_dict = previous[i]
        curr_dict = current[i]
        for key in prev_dict.keys():
            if key not in curr_dict:
                continue
            if isinstance(prev_dict[key], dict) and isinstance(curr_dict[key], dict):
                merge_previous_data([prev_dict[key]], [curr_dict[key]])  # 转为列表以复用这个函数
            else:
                if prev_dict[key] is not None and curr_dict[key] is None:
                    curr_dict[key] = prev_dict[key]
    return current

def contains_non_null_values(data):
    """检查数据中是否存在非null的值"""
    if isinstance(data,
dict):
        for key, value in data.items():
            if value is not None:
                return True
            if isinstance(value, (dict, list)) and contains_non_null_values(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if contains_non_null_values(item):
                return True
    return False