import json

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from app.api.error.report_errors import InvalidSVGGeneratedError
from app.logic import data_report_logic
from app.model.schema.report_schema import UserInputText

router = APIRouter(
    prefix="/data-report",
    tags=["data-report"],
)


class DataReportResponse(BaseModel):
    data: str
    status_code: int


@router.post("/generate")
async def generate_data_report(request_text: UserInputText):
    report_str = data_report_logic.generate_data_report(request_text.text)

    try:
        report = json.loads(report_str)
    except json.JSONDecodeError:
        raise InvalidSVGGeneratedError(detail="Failed to generate SVG from provided data.")

    return DataReportResponse(data=report['data'], status_code=report['status_code'])



