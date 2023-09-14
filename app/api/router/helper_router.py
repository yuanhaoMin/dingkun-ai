import logging

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from app.interpreter.bot_backend import BotBackend, get_config
from app.logic.helper_logic import bot, add_text, refresh_file_display, add_file, switch_to_gpt4, undo_upload_file

router = APIRouter(
    prefix="/helper",
    tags=["helper"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextMessage(BaseModel):
    text: str


class ModelChoice(BaseModel):
    model: str


config = get_config()
STATE = {"bot_backend": BotBackend()}
HISTORY = []


@router.post("/send-text")
def send_text(message: TextMessage):
    global HISTORY
    HISTORY = add_text(STATE, HISTORY, message.text)
    return {"data": bot(STATE, HISTORY)}


@router.get("/files")
def files():
    return {"data": refresh_file_display(STATE)}


@router.post("/upload-file")
async def upload_file(file: UploadFile):
    global HISTORY
    HISTORY = add_file(STATE, HISTORY, file)
    refresh_file_display(STATE)
    HISTORY = add_text(STATE, HISTORY, "")
    return {"data": bot(STATE, HISTORY)}


@router.get("/undo-upload-file")
def undo_uploadfile():
    global HISTORY
    HISTORY = undo_upload_file(STATE, HISTORY)
    return {"data": HISTORY}


@router.get("/restart")
def restart():
    global HISTORY
    return {"data": "OK"}
