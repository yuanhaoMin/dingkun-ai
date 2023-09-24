import os
from pymilvus import MilvusClient
from app.constant.function.helper_navigation import functions


def upload_helper_navigation_functions():
    client = MilvusClient(
        uri=os.environ.get("MILVUS_URI"), token=os.environ.get("MILVUS_TOKEN")
    )
    descriptions = [item["description"] for item in functions["rows"]]


upload_helper_navigation_functions()
