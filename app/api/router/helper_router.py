import json
import logging

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from app.interpreter.bot_backend import BotBackend, get_config
from app.logic.helper_logic import bot, add_text, refresh_file_display, add_file, switch_to_gpt4, undo_upload_file, \
    restart_bot_backend

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
    global HISTORY, STATE
    HISTORY = add_text(STATE, HISTORY, message.text)

    def generate():
        global HISTORY, STATE
        for h in bot(STATE, HISTORY):
            yield json.dumps({"data": h[-1][-1]}, ensure_ascii=False)

    return StreamingResponse(generate(), media_type="application/json;charset=utf-8")


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
    HISTORY.clear()
    restart_bot_backend(STATE)
    return {"data": "OK"}
