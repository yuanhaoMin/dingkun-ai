from pydantic import BaseModel


class GetAllFilenamesResponse(BaseModel):
    filenames: list[str]


class ChatWithDocumentRequest(BaseModel):
    session_id: str
    user_message: str


class ChatWithDataRequest(BaseModel):
    filename: str
    user_message: str
