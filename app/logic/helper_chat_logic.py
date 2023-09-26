import json
import os
import textwrap

from app.constant.function.helper_navigation import name_time_start_time_end_extract, name_extract
from app.constant.path_constants import CONSTANT_DIRECTORY_PATH, DATA_DIRECTORY_PATH
from app.model.conversation import Conversation
from app.model.session_manager import SessionManager
from app.config.milvus_db import MILVUS_COLLECTION, get_milvus_client
from app.util.file_util import create_prompt_from_template_file
from app.util.openai_util import (
    chat_completion_no_functions,
    retrieve_langchain_chat_completion_llm,
    retrieve_langchain_completion_llm
)
from fastapi import HTTPException
from langchain.agents import create_csv_agent
from langchain.agents.agent_types import AgentType
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import SystemMessage, HumanMessage

_MAX_DISTANCE = 0.38
_MAX_RELEVANT_DOCS = 2


def get_scenarios() -> dict:
    return {
        "general": "询问公司的规章制度、咨询文档、一般聊天",
        "page_navigation": "跳转页面或查询页面相关信息、事故发生前一刻的人员分布图、人员的历史轨迹、人员的最终位置、人员的详细信息、特定人员实时轨迹、在线人员列表、在线车辆列表",
    }


def get_scenario_file_path() -> str:
    return os.path.join(CONSTANT_DIRECTORY_PATH, "helper_scenarios_embeddings.parquet")


def chat_with_data_file(filename: str, user_message: str) -> str:
    file_path = os.path.join(DATA_DIRECTORY_PATH, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"File {filename} not found.")
    agent = create_csv_agent(
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        llm=retrieve_langchain_completion_llm(model_name="text-davinci-003"),
        path=file_path,
        verbose=True,
    )
    return agent.run(user_message + "\nReply in 中文")


def chat(session_id: str, user_message: str) -> str:
    conversation = _manage_session(session_id)
    is_function_call, relevant_docs = _get_query_response(
        query=user_message,
        milvus_collection_name=MILVUS_COLLECTION,
        max_docs=_MAX_RELEVANT_DOCS,
        max_distance=_MAX_DISTANCE,
    )

    if is_function_call:
        return _handle_function_call(relevant_docs, user_message)
    else:
        return _handle_regular_chat(conversation, relevant_docs, user_message)


def _manage_session(session_id: str) -> Conversation:
    """Retrieve or create session conversation."""
    session_manager = SessionManager()
    return session_manager.retrieve_or_create_session_conversation(
        session_id=session_id,
        num_of_rounds=2,
        system_message=create_prompt_from_template_file(
            filename="helper_document_qa_prompt"
        ),
    )


def _get_query_response(
        query: str,
        milvus_collection_name: str,
        max_docs: int,
        max_distance: float,
) -> tuple[bool, dict]:
    embedded_user_message = OpenAIEmbeddings().embed_query(query)
    response = get_milvus_client().search(
        collection_name=milvus_collection_name,
        data=[embedded_user_message],
        limit=5,
        output_fields=["text", "distance", "action", "route", "target", "time_start", "name", "time_end"],
    )
    filtered_docs = [doc for doc in response[0] if doc["distance"] < max_distance]
    # The most relevant document is function call
    if filtered_docs and "route" in filtered_docs[0]["entity"]:
        return True, filtered_docs
    # Otherwise, return the most relevant documents
    else:
        return False, filtered_docs[: max_docs - 1]


def _handle_function_call(relevant_docs: list, user_message : str) -> dict:
    most_relevant_doc = relevant_docs[0]["entity"]
    function_descriptions = _determine_extraction_function_based_on_missing_data(most_relevant_doc)
    
    if not function_descriptions:
        return most_relevant_doc
    return _update_missing_json_values_with_llm(
        json_data=most_relevant_doc,
        question=user_message,
        function_descriptions=function_descriptions
    )


def _determine_extraction_function_based_on_missing_data(json_data: dict) -> list:
    # 根据json_data中的缺失值来决定使用哪个function_descriptions
    missing_keys = [key for key, value in json_data.items() if value is None]
    # 使用set来确保key的唯一性
    missing_keys_set = set(missing_keys)

    if not missing_keys_set:
        return None
    if "time_start" in missing_keys_set or "time_end" in missing_keys_set:
        return name_time_start_time_end_extract
    else:
        return name_extract


def _update_missing_json_values_with_llm(json_data: dict, question: str, function_descriptions: str) -> dict:
    system_prompt = '''Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
        please reply in Chinese.要告诉用户缺失的值。'''
    llm = retrieve_langchain_chat_completion_llm(model_name='gpt-3.5-turbo')
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]
    response = llm.predict_messages(messages, functions=function_descriptions, function_call={"name": "extracting"})
    function_call = response.additional_kwargs.get("function_call")
    if function_call:
        arguments = json.loads(function_call["arguments"])
        for key, value in json_data.items():
            if value is None:
                json_data[key] = arguments.get(key)
    return json_data if function_call else response.content


def _handle_regular_chat(conversation: Conversation, relevant_docs: list, user_message: str) -> str:
    relevant_text = "\n".join([doc["entity"]["text"] for doc in relevant_docs])
    user_message_with_hint = _construct_user_message_with_hint(
        user_message, relevant_text
    )

    ai_message = chat_completion_no_functions(
        [{"role": "user", "content": user_message_with_hint}]
    )

    conversation.messages.extend(
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_message},
        ]
    )
    conversation.prune_messages()
    return ai_message


def _construct_user_message_with_hint(user_message: str, relevant_text: str) -> str:
    return textwrap.dedent(
        f"""User Question: {user_message}
        Provided Document: 
        ```
        {relevant_text}
        ```
        If the answer is not present in the provided document, or if no document is given, just say that you don't know, don't try to make up an answer. Reply in 中文
        """
    )