from app.config.environment import (
    get_milvus_collection,
    get_milvus_token,
    get_milvus_uri,
)
from pymilvus import MilvusClient

MILVUS_COLLECTION = get_milvus_collection()


_milvus_client_instance = None


def get_milvus_client() -> MilvusClient:
    global _milvus_client_instance
    if _milvus_client_instance is None:
        _milvus_client_instance = MilvusClient(
            uri=get_milvus_uri(), token=get_milvus_token()
        )
    return _milvus_client_instance
