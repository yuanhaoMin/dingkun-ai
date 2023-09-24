import os
from app.model.conversation import Conversation
from app.model import session_manager
from app.config.milvus_db import MILVUS_COLLECTION, get_milvus_client
from app.util.openai_util import chat_completion_no_functions
from langchain.embeddings import OpenAIEmbeddings


def get_scenarios() -> dict:
    return {
        "general": "询问公司的规章制度、咨询文档、一般聊天",
        "page_navigation": "跳转页面或查询页面相关信息、事故发生前一刻的人员分布图、人员的历史轨迹、人员的最终位置、人员的详细信息、特定人员实时轨迹、在线人员列表、在线车辆列表",
    }


def get_scenario_file_path() -> str:
    return os.path.join(
        os.getcwd(), "app", "constant", "helper_scenarios_embeddings.parquet"
    )


def chat(session_id: str, user_message: str) -> str:
    conversation: Conversation = (
        session_manager.retrieve_or_create_session_conversation(session_id=session_id)
    )
    embedded_user_message = OpenAIEmbeddings().embed_query(user_message)
    relevant_text = _get_relevant_text(
        embedded_user_message=embedded_user_message,
        milvus_collection_name=MILVUS_COLLECTION,
        max_docs=5,
        max_distance=0.35,
    )
    user_message_with_hint = f"""Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
If you find the answer in context, Provide the source.
Context: 
```
{relevant_text}
```
Question: {user_message}
Reply in 中文"""
    ai_message = chat_completion_no_functions(
        [{"role": "user", "content": user_message_with_hint}]
    )
    # Do not save the hint to the conversation, it serves only for document retrieval
    conversation.messages.append(
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": ai_message},
    )
    return ai_message


def _get_relevant_text(
    embedded_user_message: list[float],
    milvus_collection_name: str,
    max_docs: int,
    max_distance: float,
) -> str:
    response = get_milvus_client().search(
        collection_name=milvus_collection_name,
        data=embedded_user_message,
        limit=5,
        output_fields=["text", "distance"],
    )
    # Filter out documents with a distance < max_distance
    filtered_docs = [doc for doc in response if doc["distance"] < max_distance]
    # Select up to max_docs of the filtered documents
    selected_docs = filtered_docs[: max_docs - 1]
    return "\n".join([doc["entity"]["text"] for doc in selected_docs])
