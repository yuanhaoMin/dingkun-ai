# gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
# uvicorn app.main:app --reload
import time

import schedule
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.background import BackgroundTasks

from app.api.error.json_errors import InvalidAIGeneratedJSONError, invalid_ai_generated_json_error_handler
from app.api.router import visitor_router, data_report_router, helper_router
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
app.add_exception_handler(InvalidAIGeneratedJSONError, invalid_ai_generated_json_error_handler)


@app.get("/")
def health_check():
    return "Server is up!"


def run_schedule():
    """执行schedule的任务"""
    while True:
        schedule.run_pending()
        time.sleep(1)


@app.on_event("startup")
async def startup_event():
    # 在启动时首先进行表的反射
    reflect_log_tables()
    # 添加周期性任务
    schedule.every().day.at("04:00").do(reflect_log_tables)
    # 启动后台任务
    task = BackgroundTasks()
    task.add_task(run_schedule)
