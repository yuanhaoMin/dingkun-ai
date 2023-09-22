# gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --timeout 600
# uvicorn app.main:app --reload
from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.error.json_errors import InvalidAIGeneratedJSONError, invalid_ai_generated_json_error_handler
from app.api.router import visitor_router, data_report_router, helper_router, dashboard_router
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from app.db.session.mysql_db import reflect_log_tables

# Make sure .env is loaded before invoking
load_dotenv()
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
app.include_router(data_report_router.router)
app.include_router(helper_router.router)
app.include_router(dashboard_router.router)
app.add_exception_handler(InvalidAIGeneratedJSONError, invalid_ai_generated_json_error_handler)


@app.get("/")
def health_check():
    return "Server is up!"


@app.get("/reload_mysql_schema")
def reload_mysql_schema():
    return reflect_log_tables()
