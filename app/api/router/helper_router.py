from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import logging

from app.config.api_config import get_milvus_collection
from app.logic.helper_logic import handle_dialog, handle_upload_data_file
from app.model.schema.helper_schema import DialogRequest
from app.util.file_processing_util import process_and_store_file_to_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/helper",
    tags=["helper"],
)

ALLOWED_FILE_EXTENSIONS = ["doc", "docx", "txt", "pdf"]


def handle_upload_business_file(user_id: str, file: UploadFile):
    collection_name = get_milvus_collection()
    process_and_store_file_to_database(file, user_id, collection_name)
    return f"{file.filename} 已经成功加入了知识库."

@router.post("/upload-business-file/")
def upload_business_file(
        user_id: str = Form(...),
        file: UploadFile = File(...)
):
    file_extension = file.filename.split('.')[-1]
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Only {', '.join(ALLOWED_FILE_EXTENSIONS)} files are accepted.")

    response_message = handle_upload_business_file(user_id, file)

    # 返回统一格式的响应
    return {
        "status": "success",
        "data": {
            "message": response_message
        }
    }


@router.post("/upload-data-file/")
def upload_data_file(
        user_id: str = Form(...),
        session_id: str = Form(...),
        file: UploadFile = File(...)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    response_message = handle_upload_data_file(user_id, session_id, file)

    # 返回统一格式的响应
    return {
        "status": "success",
        "data": {
            "message": response_message
        }
    }


@router.post("/dialog/")
def dialog(request: DialogRequest):
    data = handle_dialog(request)
    if not isinstance(data, str):
        data = {"order": data}
    else:
        data = {"message": data}
    return {"status": "success", "data": data}


