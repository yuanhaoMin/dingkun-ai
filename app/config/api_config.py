import os
from functools import lru_cache
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

with open(CONFIG_PATH) as f:
    config = json.load(f)

if not config.get("API_KEY"):
    config["API_KEY"] = os.environ.get("OPENAI_API_KEY")
    os.unsetenv("OPENAI_API_KEY")


@lru_cache
def get_config():
    return config


@lru_cache
def get_openai_key():
    apikey = os.environ.get("OPENAI_API_KEY")
    return apikey
