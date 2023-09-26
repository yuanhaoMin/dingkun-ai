from pydantic import BaseModel, Field


class VisualizeInSVGRequest(BaseModel):
    text: str = Field(min_length=1)


class VisualizeInSVGResponse(BaseModel):
    svg_data: str


class GenerateConfigRequest(BaseModel):
    text: str = Field(min_length=1)


class GenerateConfigResponse(BaseModel):
    chart_config: dict
    url: str
