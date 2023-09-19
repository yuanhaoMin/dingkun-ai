from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import logging
from app.db.SessionManager import SessionManager
from app.logic.helper_logic import create_csv_processor, handle_upload_data_file, handle_dialog, \
    handle_upload_business_file
from app.model.schema.helper_schema import DialogRequest
from app.util.file_processing_util import process_and_store_file_to_database
from app.util.time_utll import get_current_date_and_day

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
        session_id: str = Form(...),
        role: str = Form(...),
        file: UploadFile = File(...)
):
    file_extension = file.filename.split('.')[-1]
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Only {', '.join(ALLOWED_FILE_EXTENSIONS)} files are accepted.")

    response = handle_upload_business_file(user_id, file)
    return {"message": response}


@router.post("/upload-data-file/")
def upload_data_file(
        user_id: str = Form(...),
        session_id: str = Form(...),
        role: str = Form(...),
        file: UploadFile = File(...)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    response = handle_upload_data_file(user_id, session_id, file)
    return {"message": response}


@router.post("/dialog/")
def dialog(request: DialogRequest):
    response = handle_dialog(request)
    return {"message": response}

