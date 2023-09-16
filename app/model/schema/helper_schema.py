# 依赖项：验证角色权限
from typing import Optional

from fastapi import HTTPException, UploadFile
from pydantic import BaseModel


def verify_role(role: str) -> str:
    if role not in ["admin", "user"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return role


# 请求模型
class FileUploadRequest(BaseModel):
    session_id: str
    role: str
    file: UploadFile


class DialogRequest(BaseModel):
    session_id: str
    role: str
    query: Optional[str]
