import json
from fastapi import APIRouter
from pydantic import BaseModel
from app.api.error.report_errors import InvalidSVGGeneratedError
from app.api.function.function_call import execute_function_from_json
from app.knowledge.chart_json import chart_json
from app.logic import data_report_logic
from app.logic.data_report_logic import get_chart_and_function
from app.model.schema.report_schema import UserInputText

router = APIRouter(
    prefix="/data-report",
    tags=["data-report"],
)


class DataReportResponse(BaseModel):
    data: str
    status_code: int


@router.post("/generate")
def generate_data_report(request_text: UserInputText):
    report_str = data_report_logic.generate_data_report(request_text.text)

    try:
        report = json.loads(report_str)
    except json.JSONDecodeError:
        raise InvalidSVGGeneratedError(
            detail="Failed to generate SVG from provided data."
        )

    return DataReportResponse(data=report["data"], status_code=report["status_code"])


@router.post("/generate-viz-data")
async def generate_data(request_text: UserInputText):
    user_message = request_text.text

    response_data = await get_chart_and_function(user_message, chart_json)
    function_response = execute_function_from_json(response_data)

    config_data = json.loads(response_data.get("chart_info", "{}"))

    chart_name = config_data.get("chart_name", "")

    return {
        "chart_name": chart_name,
        "config": config_data,
        "url_data": function_response,
    }




