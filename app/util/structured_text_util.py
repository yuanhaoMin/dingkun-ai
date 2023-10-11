import json

from langchain.schema import SystemMessage, HumanMessage

from app.constant.function.helper_navigation import get_name_time_page_listRows_extract, \
    get_name_start_time_end_time_extract, get_name_extract
from app.util.openai_util import retrieve_langchain_chat_completion_llm
from app.util.time_util import get_current_datetime
from typing import Union


current_datetime = get_current_datetime()


def determine_extraction_function_based_on_missing_data(
    json_data: dict,
) -> Union[dict, None]:
    missing_keys_set = {key for key, value in json_data.items() if value is None}

    if not missing_keys_set:
        return None

    is_time_keys_missing = {"start_time", "end_time"}.issubset(missing_keys_set)
    is_page_listRows_missing = {"page", "listRows"}.issubset(missing_keys_set)

    if is_time_keys_missing and is_page_listRows_missing:
        return get_name_time_page_listRows_extract

    if is_time_keys_missing:
        return get_name_start_time_end_time_extract

    if "name" in missing_keys_set:
        return get_name_extract

    return None


def update_missing_json_values_with_llm(
    json_data: dict, question: str, function_descriptions: str
) -> Union[dict, str]:
    system_prompt = f"""Don't make assumptions about what values to plug into functions. Ask for clarification if a 
    user request is ambiguous. The current time is {current_datetime} """
    llm = retrieve_langchain_chat_completion_llm(model_name="gpt-3.5-turbo")
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]
    response = llm.predict_messages(
        messages, functions=function_descriptions, function_call={"name": "extracting"}
    )
    function_call = response.additional_kwargs.get("function_call")
    if function_call:
        arguments = json.loads(function_call["arguments"])
        for key, value in json_data.items():
            if value is None:
                json_data[key] = arguments.get(key)
    return json_data if function_call else response.content
