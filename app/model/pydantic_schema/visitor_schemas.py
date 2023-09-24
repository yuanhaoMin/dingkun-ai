from typing import List, Optional
from pydantic import BaseModel, Field


class Department(BaseModel):
    id: int
    name: str


class DetermineFunctionCallRequest(BaseModel):
    sessionId: str
    text: str
    departments: Optional[List[Department]] = None


class DetermineFunctionCallResponse(BaseModel):
    sessionId: str
    data: list[dict]


class DetermineFunctionCallRequestSmart(BaseModel):
    sessionId: str = Field(min_length=1, alias="sessionId")
    text: str = Field(min_length=1)
    departmentsJson: Optional[str] = Field(default=None, alias="departments")
    historyData: Optional[str] = Field(default=None)
