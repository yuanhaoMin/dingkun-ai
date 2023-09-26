import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.logic.dashboard_logic import (
    extract_chart_information,
    handle_extracted_information,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)


class ChartPosition(BaseModel):
    name: str
    position: int


class InteractiveRequest(BaseModel):
    user_id: int
    session_id: str
    query: str
    role: str
    chart_positions: list[ChartPosition]


@router.post("/interactive")
def ai_interactive_board(request: InteractiveRequest):
    query = request.query

    # 解析chart_positions为字符串
    chart_positions = "\n".join(
        [f"{item.name}:{item.position}" for item in request.chart_positions]
    )

    extracted_info = extract_chart_information(chart_positions, query)
    result = handle_extracted_information(chart_positions, extracted_info, query)

    return result
