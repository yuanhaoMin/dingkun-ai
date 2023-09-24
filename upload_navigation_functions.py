import os
from app.constant.function.helper_navigation import functions
from app.util.embeddings_util import get_embeddings_with_backoff
from pymilvus import MilvusClient


def upload_helper_navigation_functions():
    client = MilvusClient(
        uri=os.environ.get("MILVUS_URI"), token=os.environ.get("MILVUS_TOKEN")
    )
    descriptions = [item["text"] for item in functions]
    embedded_descriptions = get_embeddings_with_backoff(descriptions)
    for i, item in enumerate(functions):
        item["vector"] = embedded_descriptions[i]
    client.insert(os.environ.get("MILVUS_COLLECTION"), functions)


upload_helper_navigation_functions()
