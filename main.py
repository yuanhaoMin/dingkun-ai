# gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
# uvicorn main:app --reload
from fastapi import FastAPI

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from api.routes.visitor.visitor_registration import extract_and_register

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,  # This is required
        allow_methods=["*"],
        allow_headers=["*"],
    )
]
app = FastAPI(docs_url=None, middleware=middleware, redoc_url=None)



@app.get("/")
def health_check():
    return "Server is up!"

@app.post("/register/")
def register_endpoint(text: str):
    return extract_and_register(text)