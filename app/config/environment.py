import os
from functools import lru_cache


@lru_cache
def get_milvus_collection():
    apikey = os.environ.get("MILVUS_COLLECTION")
    return apikey

@lru_cache
def get_milvus_token():
    return os.environ.get("MILVUS_TOKEN")

@lru_cache
def get_milvus_uri():
    return os.environ.get("MILVUS_URI")

@lru_cache
def get_my_sql_url():
    return os.environ.get("SQLALCHEMY_DATABASE_URL")

@lru_cache
def get_openai_key():
    apikey = os.environ.get("OPENAI_API_KEY")
    return apikey

