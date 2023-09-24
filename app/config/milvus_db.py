from app.config.environment import (
    get_milvus_collection,
    get_milvus_token,
    get_milvus_uri,
)
from pymilvus import MilvusClient

MILVUS_COLLECTION = get_milvus_collection()


def get_milvus_client() -> MilvusClient:
    return MilvusClient(uri=get_milvus_uri(), token=get_milvus_token())
