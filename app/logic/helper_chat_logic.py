import os
import textwrap
from app.constant.path_constants import CONSTANT_DIRECTORY_PATH
from app.model.conversation import Conversation
from app.model.session_manager import SessionManager
from app.config.milvus_db import MILVUS_COLLECTION, get_milvus_client
from app.util.file_util import create_prompt_from_template_file
from app.util.openai_util import chat_completion_no_functions
from langchain.embeddings import OpenAIEmbeddings


def get_scenarios() -> dict:
    return {
        "general": "询问公司的规章制度、咨询文档、一般聊天",
        "page_navigation": "跳转页面或查询页面相关信息、事故发生前一刻的人员分布图、人员的历史轨迹、人员的最终位置、人员的详细信息、特定人员实时轨迹、在线人员列表、在线车辆列表",
    }


def get_scenario_file_path() -> str:
    return os.path.join(CONSTANT_DIRECTORY_PATH, "helper_scenarios_embeddings.parquet")


def chat(session_id: str, user_message: str) -> str:
    conversation = _manage_session(session_id)

    relevant_text = _get_relevant_text_from_query(
        query=user_message,
        milvus_collection_name=MILVUS_COLLECTION,
        max_docs=2,
        max_distance=0.38,
    )

    user_message_with_hint = _construct_user_message_with_hint(
        user_message, relevant_text
    )

    ai_message = chat_completion_no_functions(
        [{"role": "user", "content": user_message_with_hint}]
    )
    # Only save user message, not document hint
    conversation.messages.extend(
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_message},
        ]
    )
    conversation.prune_messages()

    return ai_message


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


def _get_relevant_text_from_query(
    query: str,
    milvus_collection_name: str,
    max_docs: int,
    max_distance: float,
) -> str:
    embedded_user_message = OpenAIEmbeddings().embed_query(query)
    response = get_milvus_client().search(
        collection_name=milvus_collection_name,
        data=[embedded_user_message],
        limit=5,
        output_fields=["text", "distance"],
    )
    # Filter out documents with a distance < max_distance
    filtered_docs = [doc for doc in response[0] if doc["distance"] < max_distance]
    # Select up to max_docs of the filtered documents
    selected_docs = filtered_docs[: max_docs - 1]
    return "\n".join([doc["entity"]["text"] for doc in selected_docs])


def _construct_user_message_with_hint(user_message: str, relevant_text: str) -> str:
    return textwrap.dedent(
        f"""User Question: {user_message}
        Provided Document: 
        ```
        {relevant_text}
        ```
        Remember answer based on the document above. Reply in 中文
        """
    )
