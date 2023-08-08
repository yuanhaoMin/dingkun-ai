"""
Create env
    python -m venv C:\Workspace\dingkun-ai\venv

Activate env
    .\venv\Scripts\activate

Install pipreqs
    pip install pipreqs

Generate requirements.txt
    pipreqs ./ --force --encoding=utf8

Install dependencies
    pip install --upgrade -r requirements.txt
"""
import dotenv
import uvicorn

"""
Use specific version to avoid conflict:
starlette==0.27.0
"""
