import logging
import os
import pandas as pd
from app.agent.Agent import AutoProcessor
from app.agent.helper_agent import navigate_to_page, answer_documentation
from app.config.api_config import get_milvus_collection
from app.config.api_config import get_openai_key
from app.db.SessionManager import SessionManager
from app.knowledge.helper_dict import function_create_documentation, function_csv, \
    csv_system_prompt, documentation_system_prompt
from app.model.schema.helper_schema import DialogRequest
from app.util.file_processing_util import process_and_store_file_to_database
from app.util.time_utll import get_current_date_and_day
from fastapi import UploadFile
from openai.embeddings_utils import cosine_similarity, get_embedding
from typing import Any

logging.basicConfig(level=logging.DEBUG)

session_manager = SessionManager()

current_date, day_of_week = get_current_date_and_day()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(CURRENT_DIR, "..", "constant", "situations_embeddings.parquet")

# 定义常量
GENERAL_QUERY_TEXT = "询问公司的规章制度、咨询文档、一般聊天"
DATA_ANALYSIS_TEXT = "数据文件统计、.csv文件、数据分析服务文件中的数据、感谢您提供了表.csv文件"
PAGE_NAVIGATION_TEXT = "跳转页面或查询页面相关信息、事故发生前一刻的人员分布图、人员的历史轨迹、人员的最终位置、人员的详细信息、特定人员实时轨迹、在线人员列表、在线车辆列表"


def generate_and_save_embeddings():
    situations = {
        "general_query": [GENERAL_QUERY_TEXT,
                          get_embedding(GENERAL_QUERY_TEXT, engine='text-embedding-ada-002', api_key=get_openai_key())],
        "data_analysis": [DATA_ANALYSIS_TEXT,
                          get_embedding(DATA_ANALYSIS_TEXT, engine='text-embedding-ada-002', api_key=get_openai_key())],
        "page_navigation": [PAGE_NAVIGATION_TEXT, get_embedding(PAGE_NAVIGATION_TEXT, engine='text-embedding-ada-002',
                                                                api_key=get_openai_key())]
    }

    # 使用pandas保存文本和向量到parquet文件前，先将列表转为字符串
    df = pd.DataFrame(list(situations.items()), columns=['Situation', 'TextAndEmbedding'])
    df['TextAndEmbedding'] = df['TextAndEmbedding'].astype(str)
    df.to_parquet(FILE_PATH, index=False)


# 检查是否已有文件，如果没有则生成并保存
if not os.path.exists(FILE_PATH):
    generate_and_save_embeddings()


# 从parquet文件加载向量
def load_situations_embeddings():
    df = pd.read_parquet(FILE_PATH)
    df['TextAndEmbedding'] = df['TextAndEmbedding'].apply(eval)  # 将字符串转回为列表
    situations_dict = dict(zip(df['Situation'], df['TextAndEmbedding']))

    # 检查文本与常量是否匹配
    for situation, (text, embedding) in situations_dict.items():
        if situation == "general_query":
            assert text == GENERAL_QUERY_TEXT, "Text does not match the expected text for general_query"
        elif situation == "data_analysis":
            assert text == DATA_ANALYSIS_TEXT, "Text does not match the expected text for data_analysis"
        elif situation == "page_navigation":
            assert text == PAGE_NAVIGATION_TEXT, "Text does not match the expected text for page_navigation"

    # 返回仅embedding的字典
    return {k: v[1] for k, v in situations_dict.items()}


def judge_message_category(message):
    situations = load_situations_embeddings()
    message_embedding = get_embedding(message, engine='text-embedding-ada-002', api_key=get_openai_key())
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
        session_manager.add_or_update_session(session_id, processor)
    else:
        processor = session_data["conversation"]

    # 更新processor的function_descriptions为适合数据分析的描述
    function_descriptions = function_csv
    processor.update_function_descriptions(function_descriptions)

    user_input = f"用户传入了'{file.filename}'文件，接下来使用中文回复，再没有明确要求时不要轻易调用函数"
    return processor.process(user_input)


def handle_dialog(request: DialogRequest):
    session_data = session_manager.get_session(request.session_id)
    # 如果session中没有processor，则创建一个新的
    if not session_data or not session_data["conversation"]:
        processor = create_documentation_processor()  # 默认创建文档处理器
        session_manager.add_or_update_session(request.session_id, processor)
    else:
        processor = session_data["conversation"]

    # 判断消息属于哪种情况并更新function_descriptions
    category = judge_message_category(processor.get_first_k_messages_str_excluding_sys(1) + request.query)
    print('判断结果是' + category)
    if category == "data_analysis":
        function_descriptions = function_csv
        system_prompt = csv_system_prompt
        processor.update_role("csv")
    elif category == "page_navigation":
        result = navigate_to_page(request.query)
        return result
    else:
        result = answer_documentation(request.query)
        return result
    if processor.function_descriptions != function_descriptions or processor.system_prompt != system_prompt:
        processor.clear_messages()
    processor.update_function_descriptions(function_descriptions)
    processor.update_system_prompt(system_prompt)

    raw_result = processor.process(request.query)

    if 'order' in raw_result:
        processor.clear_messages()

    return raw_result


def create_documentation_processor():
    function_descriptions = function_csv
    system_prompt = csv_system_prompt
    processor = AutoProcessor(system_prompt, function_descriptions)
    processor.update_role("documentation")
    return processor


def create_csv_processor():
    function_descriptions = function_csv
    system_prompt = csv_system_prompt
    processor = AutoProcessor(system_prompt, function_descriptions)
    processor.update_role("csv")
    return processor
