import json
from fastapi import APIRouter
from app.logic import (
    data_visualization_config_logic,
    data_visualization_function_call_logic,
    data_visualization_svg_logic,
)
from app.model.pydantic_schema.data_visualization_schemas import (
    GenerateConfigRequest,
    GenerateConfigResponse,
    VisualizeInSVGRequest,
    VisualizeInSVGResponse,
)

router = APIRouter(
    prefix="/data_visualization",
    tags=["data_visualization"],
)


@router.post("/svg")
def visualize_in_svg(request: VisualizeInSVGRequest) -> VisualizeInSVGResponse:
    return data_visualization_svg_logic.visualize_in_svg(request.text)


@router.post("/config")
async def generate_config(request: GenerateConfigRequest):
    (
        chart_config,
        function_call,
    ) = await data_visualization_config_logic.get_chart_and_function(request.text)
    url = data_visualization_function_call_logic.determine_url_from_json(function_call)
    return GenerateConfigResponse(chart_config=chart_config, url=url)
