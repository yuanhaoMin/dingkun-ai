import json
import os

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from app.config.environment import (
    get_milvus_collection,
    get_milvus_token,
    get_milvus_uri,
)
from app.constant.schema.helper_schemas import name_time_start_time_end, name_extract
from app.util.openai_util import chat_completion_no_functions
from app.util.file_util import create_prompt_from_template_file
from app.util.time_utll import get_current_date_and_day
from langchain.embeddings import OpenAIEmbeddings
from pymilvus import MilvusClient

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def navigate_to_page(description: str):
    client = MilvusClient(uri=get_milvus_uri(), token=get_milvus_token())
    embedding_model = OpenAIEmbeddings()

    # 获取question的向量表示
    vector = embedding_model.embed_query(description)

    # 使用MilvusClient的search方法查询相似的文本
    results = client.search(
        collection_name="navigation",
        data=[vector],
        limit=1,
        output_fields=["*"],  # 取回所有字段
    )

    # 从results中提取相关的信息
    extracted_data = []
    for hit in results[0]:
        # 移除"id"和"vector"字段
        entity_data = hit["entity"]
        entity_data.pop("id", None)
        entity_data.pop("text", None)
        entity_data.pop("link", None)
        entity_data.pop("vector", None)

        extracted_data.append(entity_data)

    return process_or_return(extracted_data, description)


def process_or_return(json_data: list, question: str) -> list:
    # 确定使用哪个function_descriptions
    function_descriptions = determine_function_descriptions(json_data)
    if not function_descriptions:  # 如果function_descriptions为空或None，则直接返回json_data
        return json_data

    system_prompt = """Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
        please reply in Chinese.要告诉用户缺失的值。"""
    model = "gpt-3.5-turbo-0613"
    llm = ChatOpenAI(model=model)
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]
    response = llm.predict_messages(messages, functions=function_descriptions)

    function_call = response.additional_kwargs.get("function_call")
    if function_call:
        # 解析 function_call 中的参数
        arguments = json.loads(function_call["arguments"])

        # 根据缺失的 JSON 数据来确定哪些参数需要填补
        for item in json_data:
            for key, value in item.items():
                if not value:  # 如果某个字段缺失值
                    item[key] = arguments.get(key)

        return json_data
    # 如果没有 function_call，则返回 response.content
    return response.content


def determine_function_descriptions(json_data: list) -> list:
    # 根据json_data中的缺失值来决定使用哪个function_descriptions
    missing_keys = [
        key for item in json_data for key, value in item.items() if not value
    ]

    # 使用set来确保key的唯一性
    missing_keys_set = set(missing_keys)

    if not missing_keys_set:  # 如果没有缺失的键，返回None
        return None

    if "time_start" in missing_keys_set or "time_end" in missing_keys_set:
        return name_time_start_time_end
    else:
        return name_extract
