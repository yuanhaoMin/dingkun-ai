from fastapi import APIRouter
from pydantic import BaseModel, Field
from logic import visitor_logic

router = APIRouter(
    prefix="/visitor",
    tags=["visitor"],
)


class DetermineFunctionCallRequest(BaseModel):
    text: str = Field(min_length=1)


@router.post("/registration/function-call")
async def determine_registration_function_call(request: DetermineFunctionCallRequest):
    return visitor_logic.determine_registration_function_call(request.text)
