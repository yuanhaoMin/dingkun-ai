import os

from app.constant.function.navigation import functions
from app.util.embeddings_util import get_embeddings_with_backoff
from pymilvus import MilvusClient


def upload_helper_navigation_functions():
    client = MilvusClient(
        uri=os.environ.get("MILVUS_URI"), token=os.environ.get("MILVUS_TOKEN")
    )
    descriptions = [item["text"] for item in functions]

    existing_entities = client.query(
        collection_name=os.environ.get("MILVUS_COLLECTION"),
        filter=f'text in {descriptions}',
        output_fields=["id"]
    )

    if existing_entities:
        existing_ids = [entity["id"] for entity in existing_entities]
        client.delete(
            collection_name=os.environ.get("MILVUS_COLLECTION"),
            pks=existing_ids
        )

    embedded_descriptions = get_embeddings_with_backoff(descriptions)
    for i, item in enumerate(functions):
        item["vector"] = embedded_descriptions[i]

    client.insert(os.environ.get("MILVUS_COLLECTION"), functions)


upload_helper_navigation_functions()
