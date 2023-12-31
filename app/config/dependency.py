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
import backup  # For embedding cosine similarity
import chardet
import dotenv
import matplotlib  # For data visualization
import pandas  # For csv agent
import plotly  # For openai.embeddings_utils
import pyarrow  # For pandas
import scipy  # For openai.embeddings_utils
import sklearn  # For openai.embeddings_utils
import tabulate  # For csv agent
import tiktoken
import uvicorn

"""
Use specific version to solve conflict
starlette==0.27.0

Manually paste the following dependency into the requirements.txt file:
jsonschema==4.19.0
mysqlclient==2.2.0
pdfminer.six==20221105
python-multipart==0.0.6
"""
