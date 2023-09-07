import json
from fastapi import APIRouter
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
def generate_data(request_text: UserInputText):
    if request_text.text == "1":
        config = {
            "title": {
                "visible": True,
                "text": "单折线图"
            },
            "description": {
                "text": "一个简单的单折线图"
            },
            "legend": {
                "flipPage": False
            },
            "xAxis": {
                "title": {
                    "visible": True,
                    "text": "这是x轴"
                }
            },
            "yAxis": {
                "title": {
                    "visible": True,
                    "text": "这是y轴"
                }
            },
            "padding": "auto",
            "forceFit": True,
            "xField": "Date",
            "yField": "scales",
            "color": [
                "#CFCFE2"
            ]
        }
        return {
            "config": config,
            "url_data": "https://gw.alipayobjects.com/os/bmw-prod/1d565782-dde4-4bb6-8946-ea6a38ccf184.json"

        }
    return {}
