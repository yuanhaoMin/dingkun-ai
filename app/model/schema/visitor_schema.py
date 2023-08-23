from pydantic import BaseModel, Field
from typing import List, Optional


class DetermineFunctionCallRequest(BaseModel):
    text: str = Field(min_length=1)


class DetermineFunctionCallRequestOld(BaseModel):
    sessionId: str = Field(min_length=1, alias="sessionId")
    text: str = Field(min_length=1)
    departmentNames: Optional[List[str]] = Field(default=None)
