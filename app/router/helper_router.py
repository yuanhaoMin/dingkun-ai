import logging
from app.logic.helper_file_logic import (
    get_all_filenames_from_data_directory,
    store_file_in_data_directory,
    process_and_persist_business_file,
    purge_data_directory,
)
from app.logic import helper_chat_logic
from app.model.pydantic_schema.helper_schemas import (
    ChatRequest,
    GetAllFilenamesResponse,
)
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Response

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/helper",
    tags=["helper"],
)

ALLOWED_FILE_EXTENSIONS = ["doc", "docx", "txt", "pdf"]


@router.post("/dialog/")
def chat(request: ChatRequest):
    data = helper_chat_logic.chat(
        session_id=request.session_id, user_message=request.user_message
    )
    if not isinstance(data, str):
        data = {"order": data}
    else:
        data = {"message": data}
    return {"status": "success", "data": data}


@router.get("/filenames")
def get_all_filenames(user_id: int) -> GetAllFilenamesResponse:
    return get_all_filenames_from_data_directory(user_id)


@router.post("/upload-business-file/")
def upload_business_file(file: UploadFile = File(...), user_id: int = Form(...)):
    file_extension = file.filename.split(".")[-1]
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(ALLOWED_FILE_EXTENSIONS)} files are accepted.",
        )
    process_and_persist_business_file(uploadFile=file, user_id=user_id)
    return Response(status_code=200)


@router.post("/upload-data-file/")
def upload_data_file(file: UploadFile = File(...), user_id: int = Form(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    store_file_in_data_directory(filename=file.filename, file=file.file)
    return Response(status_code=200)


@router.post("/purge-local-files/")
def purge_local_files():
    purge_data_directory()
    return Response(status_code=200)
