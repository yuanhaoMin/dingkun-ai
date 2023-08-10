from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class InvalidAIGeneratedJSONError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


def invalid_ai_generated_json_error_handler(request: Request, exc: InvalidAIGeneratedJSONError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Invalid AI-generated JSON data", "detail": exc.detail},
    )