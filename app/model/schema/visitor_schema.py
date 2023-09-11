from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class DetermineFunctionCallRequest(BaseModel):
    text: str = Field(min_length=1)


class DetermineFunctionCallRequestOld(BaseModel):
    sessionId: str = Field(min_length=1, alias="sessionId")
    text: str = Field(min_length=1)
    departmentNames: Optional[List[str]] = Field(default=None)


class DetermineFunctionCallRequestSmart(BaseModel):
    sessionId: str = Field(min_length=1, alias="sessionId")
    text: str = Field(min_length=1)
    departmentsJson: Optional[str] = Field(default=None, alias="departments")
    historyData: Optional[str] = Field(default=None)

