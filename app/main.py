# gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
# uvicorn app.main:app --reload
from fastapi import FastAPI

from app.api.error.json_errors import InvalidAIGeneratedJSONError, invalid_ai_generated_json_error_handler
from app.api.router import visitor_router
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,  # This is required
        allow_methods=["*"],
        allow_headers=["*"],
    )
]
app = FastAPI(middleware=middleware)
app.include_router(visitor_router.router)
app.add_exception_handler(InvalidAIGeneratedJSONError, invalid_ai_generated_json_error_handler)

@app.get("/")
def health_check():
    return "Server is up!"
