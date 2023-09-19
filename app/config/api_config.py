import os
from functools import lru_cache


@lru_cache
def get_openai_key():
    apikey = os.environ.get("OPENAI_API_KEY")
    return apikey


@lru_cache
def get_milvus_uri():
    return os.environ.get("MILVUS_URI")


@lru_cache
def get_milvus_token():
    return os.environ.get("MILVUS_TOKEN")
