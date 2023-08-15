from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class InvalidSVGGeneratedError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)


def invalid_svg_generated_error_handler(request: Request, exc: InvalidSVGGeneratedError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Invalid SVG generated data", "detail": exc.detail},
    )
