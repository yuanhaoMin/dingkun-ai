from fastapi import APIRouter
import logging

from app.knowledge.helper_dict import functions
from app.model.schema.helper_schema import DialogRequest, FileUploadRequest
from app.util.openai_util import chat_completion_request
from app.util.text_util import create_prompt_from_template_file
from app.util.time_utll import get_current_date_and_day

router = APIRouter(
    prefix="/helper",
    tags=["helper"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

current_date, day_of_week = get_current_date_and_day()


@router.post("/upload-business-file/")
def upload_business_file(request: FileUploadRequest):
    # 上传企业文件的逻辑
    logger.info(
        f"Received business file '{request.file.filename}' from session '{request.session_id}' with role '{request.role}'")
    return {"filename": request.file.filename, "session_id": request.session_id, "role": request.role}


@router.post("/upload-data-file/")
def upload_data_file(request: FileUploadRequest):
    # 上传数据文件的逻辑
    logger.info(
        f"Received data file '{request.file.filename}' from session '{request.session_id}' with role '{request.role}'")
    return {"filename": request.file.filename, "session_id": request.session_id, "role": request.role}


@router.post("/dialog/")
def dialog(request: DialogRequest):
    logger.info(
        f"Received dialog request from session '{request.session_id}' with role '{request.role}' and query '{request.query}'"
    )
    replacements = {
        "current_date": current_date,  # 使用Python的date.today()获取今天的日期
        "day_of_week": day_of_week,  # 使用strftime获取当前的星期
    }
    prompt = create_prompt_from_template_file(
        filename="smart_helper_forwarding_prompts", replacements=replacements
    )
    # 初始化消息列表
    messages = [{"role": 'user', "content": prompt}, {"role": 'user', "content": request.query}]

    # 使用chat_completion_request函数与AI模型进行交互
    chat_response = chat_completion_request(messages, functions)
    # 解析模型的响应
    ai_response = chat_response.json()["choices"][0]["message"]

    # 根据模型的响应类型（是否包含函数调用）生成最终响应
    if "function_call" in ai_response:
        # 如果模型生成了函数调用，您可以在此处执行相应的操作
        # 例如，调用相应的服务或API
        response_content = f"Function {ai_response['function_call']['name']} called with arguments {ai_response['function_call']['arguments']}"
    else:
        response_content = ai_response["content"]

    return {"session_id": request.session_id, "role": "assistant", "response": response_content}
