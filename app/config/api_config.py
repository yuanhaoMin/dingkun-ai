import os
from functools import lru_cache


@lru_cache
def get_openai_key():
    apikey = os.environ.get("OPENAI_API_KEY")
    return apikey
