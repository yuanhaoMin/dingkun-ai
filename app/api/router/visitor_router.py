from fastapi import APIRouter

from app.logic import visitor_logic
from app.model.schema.visitor_schema import DetermineFunctionCallRequest

router = APIRouter(
    prefix="/visitor",
    tags=["visitor"],
)


@router.post("/registration/function-call")
async def determine_registration_function_call(request: DetermineFunctionCallRequest):
    return visitor_logic.determine_registration_function_call(request.text)
