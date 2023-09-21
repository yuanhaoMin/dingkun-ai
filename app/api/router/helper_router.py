from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import logging

from starlette.responses import StreamingResponse

from app.agent.Agent import AutoProcessor
from app.db.SessionManager import SessionManager
from app.knowledge.helper_dict import function_create_documentation
from app.logic.helper_logic import handle_upload_data_file, handle_dialog, handle_upload_business_file
from app.model.schema.helper_schema import DialogRequest

session_manager = SessionManager()
router = APIRouter(
    prefix="/helper",
    tags=["helper"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/helper",
    tags=["helper"],
)

ALLOWED_FILE_EXTENSIONS = ["doc", "docx", "txt", "pdf"]


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


