import json
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
        response = conversation.ask(text + '''(Only return the specified JSON array relevant to the context, even if 
        user requests do not align with the pre-defined scenario. Even without accompanying personnel, return the 
        complete array with both objects. Retain the previously entered JSON unless explicitly changed by the user. 
        Ensure: 1. Proper bracket pairing: Each '{' matches with '}', and each '[' with ']'. 2. Correct comma 
        placement: Ensure no trailing comma after the last element or key-value pair.) '''
                                    )
        conversation.save_messages_to_file()
        remove_expired_sessions()
        prune_sessions()
        try:
            # 尝试修复和解析 JSON
            fixed_response = fix_and_parse_json(response)
            # 合并之前的数据，如果有的话
            if SESSION_STORE[sessionId].get("previous_response"):
                fixed_response = merge_previous_data(SESSION_STORE[sessionId]["previous_response"], fixed_response)

            # 保存这次的响应作为下一次的"之前的响应"
            SESSION_STORE[sessionId]["previous_response"] = fixed_response

            return fixed_response  # 如果成功，直接返回修复后的 JSON
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON. AI's response was: {response}")
            # 如果失败，捕获异常并告知 AI
            text = "Please check your JSON format and only reply with valid JSON data."
            conversation.ask(text)
            attempts += 1

    # 超过最大尝试次数，返回 None
    return {}


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


def merge_previous_data(previous: list, current: list) -> list:
    for i in range(len(previous)):
        prev_dict = previous[i]
        curr_dict = current[i]
        for key in prev_dict.keys():
            if key not in curr_dict:
                continue
            if isinstance(prev_dict[key], dict) and isinstance(curr_dict[key], dict):
                merge_previous_data([prev_dict[key]], [curr_dict[key]])  # 转为列表以复用这个函数
            elif isinstance(prev_dict[key], list) and isinstance(curr_dict[key], list):  # 新增的列表合并逻辑
                for j in range(min(len(prev_dict[key]), len(curr_dict[key]))):
                    if prev_dict[key][j] != "null" and curr_dict[key][j] == "null":
                        curr_dict[key][j] = prev_dict[key][j]
            else:
                # 修改这里的检查逻辑，考虑到 "null"
                if (prev_dict[key] is not None and prev_dict[key] != "null") and (
                        curr_dict[key] is None or curr_dict[key] == "null"):
                    curr_dict[key] = prev_dict[key]
    return current


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
