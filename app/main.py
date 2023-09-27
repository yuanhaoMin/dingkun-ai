# gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --timeout 600
# uvicorn app.main:app --reload

import logging
from app.config import my_sql_db
from app.logic import start_up_logic
from app.router import (
    dashboard_router,
    data_visualization_router,
    helper_router,
    visitor_router, global_command_router,
)
from dotenv import load_dotenv
from fastapi import FastAPI
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
# Set logging level
logging.basicConfig(level=logging.INFO)

app = FastAPI(middleware=middleware)
app.include_router(dashboard_router.router)
app.include_router(data_visualization_router.router)
app.include_router(helper_router.router)
app.include_router(visitor_router.router)
app.include_router(global_command_router.router)


@app.on_event("startup")
def startup_event():
    load_dotenv()
    start_up_logic.generate_embedding_for_scenarios()


@app.get("/")
def health_check():
    return "Server is up!"


@app.get("/load_mysql_schema")
def load_mysql_schema():
    return my_sql_db.load_log_table_schemas()
