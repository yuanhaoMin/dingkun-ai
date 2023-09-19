import json
from fastapi import APIRouter, UploadFile,File
import logging

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage, ChatMessage

from app.knowledge.helper_dict import functions
from app.logic.helper_logic import document_answer_service
from app.model.schema.helper_schema import DialogRequest, FileUploadRequest
from app.util.file_processing_util import process_and_store_file_to_database
from app.util.openai_util import chat_completion_request, Conversation
from app.util.text_util import create_prompt_from_template_file
from app.util.time_utll import get_current_date_and_day


SESSIONS = {}
router = APIRouter(
    prefix="/helper",
    tags=["helper"],
)

FUNCTION_MAP = {
    "document_answer_service": document_answer_service,
    # ... 其他函数映射
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

current_date, day_of_week = get_current_date_and_day()


@router.post("/upload-business-file/")
def upload_business_file(request: FileUploadRequest):
    collection_name = "dingkun"
    process_and_store_file_to_database(request.file, collection_name)
    return {"message": f"{request.file.filename} has been successfully uploaded to the knowledge base."}


@router.post("/upload-data-file/")
def upload_data_file(request: FileUploadRequest):
    # 上传数据文件的逻辑
    logger.info(
        f"Received data file '{request.file.filename}' from session '{request.session_id}' with role '{request.role}'")
    return {"filename": request.file.filename, "session_id": request.session_id, "role": request.role}


# @router.post("/dialog/")
# def dialog(request: DialogRequest):
#     logger.info(
#         f"Received dialog request from session '{request.session_id}' with role '{request.role}' and query '{request.query}'"
#     )
#
#     # 获取或创建session的消息历史
#     if request.session_id not in SESSIONS:
#         prompt = create_prompt_from_template_file(
#             filename="smart_helper_forwarding_prompts",
#             replacements={
#                 "current_date": current_date,  # 使用Python的date.today()获取今天的日期
#                 "day_of_week": day_of_week,  # 使用strftime获取当前的星期
#             }
#         )
#         SESSIONS[request.session_id] = [SystemMessage(content=prompt)]
#     messages = SESSIONS[request.session_id]
#
#     # 添加用户消息到消息历史
#     messages.append(HumanMessage(content=request.query))
#
#     model = 'gpt-3.5-turbo-0613'
#     llm = ChatOpenAI(model=model)
#     # 使用llm预测消息
#     response = llm.predict_messages(messages, functions=functions)
#
#     # 检查是否有函数调用的请求
#     function_call = response.additional_kwargs.get("function_call")
#     if function_call:
#         # 获取函数名和参数
#         function_name = function_call["name"]
#         arguments = json.loads(function_call["arguments"])
#
#         # 调用函数
#         the_function = globals().get(function_name)
#         if the_function:  # 确保函数存在
#             parameter_names = get_function_parameter_names(the_function)
#             parameter_values = [arguments[parameter_name] for parameter_name in parameter_names]
#             returned_value = the_function(*parameter_values)
#
#             # 更新消息列表，为下一次迭代做准备
#             messages.append(AIMessage(content=str(response.additional_kwargs)))
#             messages.append(
#                 ChatMessage(role='function', additional_kwargs={'name': function_name}, content=returned_value))
#             return {"response": returned_value}
#         else:
#             return {"response": f"ai产生幻觉 {function_name} 不存在。"}
#     else:
#         return {"response": response.content}
