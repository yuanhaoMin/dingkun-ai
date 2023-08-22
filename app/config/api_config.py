import os
from typing import List

current_key_index = 0


def get_openai_keys() -> List[str]:
    keys = os.environ.get("OPENAI_API_KEY", "")
    return keys.split(",")


def get_openai_key() -> str:
    global current_key_index
    keys = get_openai_keys()

    if not keys or not keys[0]:  # 这里检查keys列表是否为空，或者其第一个元素是否为空
        raise Exception("No OpenAI API keys are configured.")

    key = keys[current_key_index]
    current_key_index = (current_key_index + 1) % len(keys)

    return key