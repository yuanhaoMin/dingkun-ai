import json
import re
from typing import Any, Dict, Union


def add_quotes_to_property_names(json_string: str) -> str:
    """
    Add quotes to property names in a JSON string.
    Args:
        json_string (str): The JSON string.
    Returns:
        str: The JSON string with quotes added to property names.
    """

    def replace_func(match):
        return f'"{match.group(1)}":'

    property_name_pattern = re.compile(r"(\w+):")
    corrected_json_string = property_name_pattern.sub(replace_func, json_string)

    try:
        json.loads(corrected_json_string)
        return corrected_json_string
    except json.JSONDecodeError as e:
        raise e


def balance_braces(json_string: str) -> str:
    """
    Balance the braces in a JSON string.
    Args:
        json_string (str): The JSON string.
    Returns:
        str: The JSON string with braces balanced.
    """

    open_braces_count = json_string.count("{")
    close_braces_count = json_string.count("}")

    while open_braces_count > close_braces_count:
        json_string += "}"
        close_braces_count += 1

    while close_braces_count > open_braces_count:
        json_string = json_string.rstrip("}")
        close_braces_count -= 1

    try:
        json.loads(json_string)
        return json_string
    except json.JSONDecodeError as e:
        raise e


def dump_json(data, file_path, **kwargs):
    with open(file=file_path, mode="w", encoding="utf-8") as fp:
        json.dump(data, fp, **kwargs)


def extract_char_position(error_message: str) -> int:
    """Extract the character position from the JSONDecodeError message.
    Args:
        error_message (str): The error message from the JSONDecodeError
          exception.
    Returns:
        int: The character position.
    """
    import re

    char_pattern = re.compile(r"\(char (\d+)\)")
    if match := char_pattern.search(error_message):
        return int(match[1])
    else:
        raise ValueError("Character position not found in the error message.")


def fix_invalid_escape(json_str: str, error_message: str) -> str:
    while error_message.startswith("Invalid \\escape"):
        bad_escape_location = extract_char_position(error_message)
        json_str = json_str[:bad_escape_location] + json_str[bad_escape_location + 1 :]
        try:
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError as e:
            error_message = str(e)
    return json_str


def load_json(file_path, **kwargs):
    with open(file=file_path, mode="r", encoding="utf-8") as fp:
        return json.load(fp, **kwargs)


def correct_json(json_str: str) -> str:
    """
    Correct common JSON errors.
    Args:
        json_str (str): The JSON string.
    """

    try:
        json.loads(json_str)
        return json_str
    except json.JSONDecodeError as e:
        error_message = str(e)
        if error_message.startswith("Invalid \\escape"):
            json_str = fix_invalid_escape(json_str, error_message)
        if error_message.startswith(
            "Expecting property name enclosed in double quotes"
        ):
            json_str = add_quotes_to_property_names(json_str)
            try:
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError as e:
                error_message = str(e)
        if balanced_str := balance_braces(json_str):
            return balanced_str
    return json_str


def fix_and_parse_json(json_str: str) -> Union[str, Dict[Any, Any], list]:
    """Fix and parse JSON string"""
    json_str = json_str.replace("\t", "")

    # 尝试检测是否有多个 JSON 对象
    trimmed_json_str = json_str.strip()
    if trimmed_json_str.count("{") > 1 and trimmed_json_str[0] != "[":
        try:
            fixed_multiple_objects = "[" + trimmed_json_str + "]"
            return json.loads(fixed_multiple_objects)
        except json.JSONDecodeError:
            pass  # 继续尝试其他修复方式

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as _:
        json_str = correct_json(json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as _:
            pass

    try:
        brace_index = json_str.index("{")
        json_str = json_str[brace_index:]
        last_brace_index = json_str.rindex("}")
        json_str = json_str[: last_brace_index + 1]
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise e

json_str = '''
[
    {
        "visitor_information": {
            "phone": "132412415",
            "name": "张三",
            "id_number": "null",
            "license_plate": "null"
        },
        "visit_details": {
            "visited_department": "领导部门",
            "visited_person": "黄灿",
            "visited_person_phone": "null",
            "appointment_time": "2023-08-30 下午",
            "visit_unit": "null",
            "visit_reason": "null"
        },
        "companion_information": {
            "name": [
                "小李",
                "王丽"
            ],
            "phone": [
                "null",
                "null"
            ],
            "id_number": [
                "null",
                "null"
            ]
        }
    }
]
'''
#
fixed_json = fix_and_parse_json(json_str)
print(fixed_json)