from pydantic import BaseModel


class GetAllFilenamesResponse(BaseModel):
    filenames: list[str]


class ChatRequest(BaseModel):
    session_id: str
    user_message: str
