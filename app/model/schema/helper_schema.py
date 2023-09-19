from pydantic import BaseModel


class DialogRequest(BaseModel):
    user_id: str
    session_id: str
    role: str
    query: str
