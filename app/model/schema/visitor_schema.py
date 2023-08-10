from pydantic import BaseModel, Field


class DetermineFunctionCallRequest(BaseModel):
    text: str = Field(min_length=1)
