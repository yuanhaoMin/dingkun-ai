"""
Create env
    python -m venv C:\Workspace\dingkun-ai\venv

Activate env
    .\venv\Scripts\activate

Install pipreqs to collect and export dependency
    pip install pipreqs

Generate requirements.txt
    pipreqs ./ --force --encoding=utf8

Install dependencies
    pip install --upgrade -r requirements.txt
"""
import dotenv
import matplotlib # For openai.embeddings_utils
import plotly # For openai.embeddings_utils
import pyarrow # For pandas
import scipy # For openai.embeddings_utils
import sklearn # For openai.embeddings_utils
import tiktoken
import uvicorn
"""
Manually paste the following dependency into the requirements.txt file:
jsonschema==4.19.0
mysqlclient==2.2.0
pdfminer.six==20221105
python_docx==0.8.11
python-multipart==0.0.6
"""
"""
Use specific version to solve conflict
starlette==0.27.0
"""