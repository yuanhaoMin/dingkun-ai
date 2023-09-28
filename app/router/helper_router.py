import logging
from app.logic import helper_chat_logic, helper_file_logic
from app.model.pydantic_schema.helper_schemas import (
    ChatWithDataRequest,
    ChatWithDocumentRequest,
    GetAllFilenamesResponse,
)
from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/helper",
    tags=["helper"],
)

ALLOWED_FILE_EXTENSIONS = ["doc", "docx", "txt", "pdf"]


@router.post("/dialog/")
def chat_with_document(request: ChatWithDocumentRequest):
    result = helper_chat_logic.chat(
        session_id=request.session_id, user_message=request.user_message, stream=False
    )
    return {"result": result}


@router.get("/dialog-stream", response_class=StreamingResponse)
def stream_completion(session_id: str, user_message: str) -> StreamingResponse:
    return StreamingResponse(
        helper_chat_logic.chat(
            session_id=session_id, user_message=user_message, stream=True
        ),
        media_type="text/event-stream",
    )


@router.post("/analyse-data-file/")
def chat_with_data(request: ChatWithDataRequest):
    if not request.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    ai_message = helper_chat_logic.chat_with_data_file(
        filename=request.filename,
        user_message=request.user_message,
    )
    return {"ai_message": ai_message}


@router.get("/filenames")
def get_all_filenames(user_id: int) -> GetAllFilenamesResponse:
    return helper_file_logic.get_all_filenames_from_data_directory(user_id)


@router.post("/upload-business-file/")
def upload_business_file(file: UploadFile = File(...), user_id: int = Form(...)):
    file_extension = file.filename.split(".")[-1]
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(ALLOWED_FILE_EXTENSIONS)} files are accepted.",
        )
    helper_file_logic.process_and_persist_business_file(
        uploadFile=file, user_id=user_id
    )
    return Response(status_code=200)


@router.post("/upload-data-file/")
def upload_data_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    helper_file_logic.store_file_in_data_directory(
        filename=file.filename, file=file.file
    )
    return Response(status_code=200)


@router.post("/purge-local-files/")
def purge_local_files():
    helper_file_logic.purge_data_directory()
    return Response(status_code=200)
