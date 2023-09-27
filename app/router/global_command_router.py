from fastapi import APIRouter

from app.logic.global_command_logic import parse_text_command
from app.model.pydantic_schema.global_command_schemas import VoiceRedirectRequest

router = APIRouter(
    prefix="/global_command",
    tags=["/global_command"],
)


@router.post("/")
def global_command(request: VoiceRedirectRequest):
    order = parse_text_command(
        request.user_message,
        request.route
    )
    return order
