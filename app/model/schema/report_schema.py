from pydantic import BaseModel, Field


class DataReportResponse(BaseModel):
    data: str
    status_code: int


class UserInputText(BaseModel):
    text: str = Field(min_length=1)
