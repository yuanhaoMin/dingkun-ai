import logging
from app.logic.helper_file_logic import (
    persist_csv_file,
    process_and_persist_business_file,
)
from app.logic.helper_logic import handle_dialog
from app.model.pydantic_schema.helper_schemas import DialogRequest
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Response

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/helper",
    tags=["helper"],
)

ALLOWED_FILE_EXTENSIONS = ["doc", "docx", "txt", "pdf"]


@router.post("/upload-business-file/")
def upload_business_file(file: UploadFile = File(...), user_id: str = Form(...)):
    file_extension = file.filename.split(".")[-1]
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(ALLOWED_FILE_EXTENSIONS)} files are accepted.",
        )
    process_and_persist_business_file(uploadFile=file, user_id=user_id)
    return Response(status_code=200)


@router.post("/upload-data-file/")
def upload_data_file(file: UploadFile = File(...), user_id: str = Form(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    persist_csv_file(uploadFile=file, user_id=user_id)
    return Response(status_code=200)


@router.post("/dialog/")
def dialog(request: DialogRequest):
    data = handle_dialog(request)
    if not isinstance(data, str):
        data = {"order": data}
    else:
        data = {"message": data}
    return {"status": "success", "data": data}
