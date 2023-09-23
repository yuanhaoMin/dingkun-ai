from pydantic import BaseModel


class DialogRequest(BaseModel):
    user_id: str
    session_id: str
    query: str
