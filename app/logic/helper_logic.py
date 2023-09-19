import logging
import os
import pandas as pd
from app.agent.Agent import AutoProcessor
from app.config.api_config import get_milvus_collection
from app.config.api_config import get_openai_key
from app.db.SessionManager import SessionManager
from app.model.schema.helper_schema import DialogRequest
from app.util.file_processing_util import process_and_store_file_to_database
from app.util.time_utll import get_current_date_and_day
from fastapi import UploadFile
from langchain.chat_models import ChatOpenAI
from openai.embeddings_utils import cosine_similarity, get_embedding
from typing import Any


logging.basicConfig(level=logging.DEBUG)

session_manager = SessionManager()

current_date, day_of_week = get_current_date_and_day()

function_csv = [
    {
        "name": "query_csv",
        "description": "Provide data analysis services, especially when detecting .csv files or explicit data "
                       "analysis requests.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the data file.如果你不知道具体请询问用户。"
                },
                "query": {
                    "type": "string",
                    "description": "Query or request related to data analysis in chinese."
                }
            },
            "required": ["file_path", "query"]
        }
    }
]


def create_csv_processor():
    model = 'gpt-3.5-turbo-0613'
    llm = ChatOpenAI(model=model, openai_api_key=get_openai_key())
    function_descriptions = function_csv
    system_prompt = """
        你是名为“定坤”的智能客服助理。你的主要功能是从用户的信息中发现需求去调用执行数据分析服务。始终确保你的回答是准确、及时和有帮助的。
        你是一个热心、礼貌和诚实的助理。始终尽可能地提供有帮助的回答，同时要确保安全。你的回答不应包括任何有害、不道德、种族主义、性别歧视、有毒、危险或非法的内容。请确保你的回应在社交上是无偏见的，并且本质上是积极的。
        如果一个问题没有任何意义，或者在事实上并不连贯，请解释原因，而不是回答不正确的内容。如果你不知道某个问题的答案，或者用户的请求与你的功能不匹配，请明确告知并提供适当的建议，而不是分享虚假信息不要假设要插入函数的值是什么。如果值没有明确指定，请寻求澄清。
        """
    processor = AutoProcessor(system_prompt, model, llm, function_descriptions)
    return processor


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(CURRENT_DIR, "..", "constant", "situations_embeddings.parquet")


def generate_and_save_embeddings():
    # 为三种情况创建代表性的句子或短语
    situations = {
        "general_query": get_embedding("询问规则制度、咨询文档、一般聊天、公司规章制度", engine='text-embedding-ada-002', api_key=get_openai_key() ),
        "data_analysis": get_embedding("数据文档分析", engine='text-embedding-ada-002', api_key=get_openai_key()),
        "page_navigation": get_embedding("跳转页面或查询页面相关信息", engine='text-embedding-ada-002', api_key=get_openai_key())
    }

    # 使用pandas保存向量到parquet文件
    df = pd.DataFrame(list(situations.items()), columns=['Situation', 'Embedding'])
    df.to_parquet(FILE_PATH, index=False)


# 检查是否已有文件，如果没有则生成并保存
if not os.path.exists(FILE_PATH):
    generate_and_save_embeddings()


# 从parquet文件加载向量
def load_situations_embeddings():
    df = pd.read_parquet(FILE_PATH)
    return dict(zip(df['Situation'], df['Embedding']))


def judge_message_category(message):
    situations = load_situations_embeddings()
    message_embedding = get_embedding(message, engine='text-embedding-ada-002')
    max_similarity = -1
    best_match = None

    for situation, embedding in situations.items():
        similarity = cosine_similarity(message_embedding, embedding)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = situation
    return best_match


def handle_upload_business_file(user_id: str, file: UploadFile):
    collection_name = get_milvus_collection()
    process_and_store_file_to_database(file, user_id, collection_name)
    return f"{file.filename} 已经成功加入了知识库."


def handle_upload_data_file(user_id: str, session_id: str, file: UploadFile) -> Any:
    folder_path = os.path.join(os.getcwd(), "data")

    # 清理 data 文件夹中的文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}. Error: {e}")

    file_path = os.path.join(folder_path, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    session_data = session_manager.get_session(session_id)

    # 如果session中没有processor，则创建一个新的
    if not session_data or "processor" not in session_data:
        processor = create_csv_processor()
        session_manager.add_or_update_session(session_id, {"processor": processor})
    else:
        processor = session_data["processor"]

    # 更新processor的function_descriptions为适合数据分析的描述
    function_descriptions = function_csv
    processor.update_function_descriptions(function_descriptions)

    user_input = f"用户传入了{file.filename}文件，接下来使用中文回复，再没有明确要求时不要轻易调用函数"
    return processor.process(user_input)


def handle_dialog(request: DialogRequest):
    session_data = session_manager.get_session(request.session_id)

    # 如果session中没有processor，则创建一个新的
    if not session_data or "processor" not in session_data:
        processor = create_documentation_processor()  # 默认创建文档处理器
        session_manager.add_or_update_session(request.session_id, {"processor": processor})
    else:
        processor = session_data["processor"]

    # 判断消息属于哪种情况并更新function_descriptions
    category = judge_message_category(request.query)
    if category == "data_analysis":
        function_descriptions = function_csv
    elif category == "page_navigation":
        function_descriptions = function_navigation
    else:
        function_descriptions = function_create_documentation
    processor.update_function_descriptions(function_descriptions)

    # 处理用户输入
    return processor.process(request.query)


function_navigation = [
    {
        "name": "navigate_to_page",
        "description": "Help users navigate to the desired page.",
        "parameters": {
            "type": "object",
            "properties": {
                "page_name": {
                    "type": "string",
                    "description": "Name of the page user wants to navigate to."
                }
            },
            "required": ["page_name"]
        }
    }
]


def create_navigation_processor():
    model = 'gpt-3.5-turbo-0613'
    llm = ChatOpenAI(model=model, openai_api_key=get_openai_key())
    function_descriptions = function_navigation
    system_prompt = """
        你是名为“导航助手”的智能客服助理。你的主要功能是帮助用户导航到他们想要的页面。
        """
    processor = AutoProcessor(system_prompt, model, llm, function_descriptions)
    return processor


function_create_documentation = [
    {
        "name": "answer_documentation",
        "description": "Answer questions related to company's documentation, rules, and regulations.",
        "parameters": {
            "type": "object",
            "properties": {
                "document_name": {
                    "type": "string",
                    "description": "Name of the document or rule user is asking about."
                },
                "query": {
                    "type": "string",
                    "description": "Specific question about the document or rule."
                }
            },
            "required": ["document_name", "query"]
        }
    }
]


def create_documentation_processor():
    model = 'gpt-3.5-turbo-0613'
    llm = ChatOpenAI(model=model, openai_api_key=get_openai_key())
    function_descriptions = [
        {
            "name": "answer_documentation",
            "description": "Answer questions related to company's documentation, rules, and regulations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_name": {
                        "type": "string",
                        "description": "Name of the document or rule user is asking about."
                    },
                    "query": {
                        "type": "string",
                        "description": "Specific question about the document or rule."
                    }
                },
                "required": ["document_name", "query"]
            }
        }
    ]
    system_prompt = """
        你是名为“文档助手”的智能客服助理。你的主要功能是回答与公司的文档、规章和制度相关的问题。
        """
    processor = AutoProcessor(system_prompt, model, llm, function_descriptions)
    return processor


