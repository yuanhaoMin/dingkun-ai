import os

from app.constant.function.navigation import (global_dict_array, screen_dict_array,
                                             track_dict_array, help_dict_array)
from app.util.embeddings_util import get_embeddings_with_backoff
from pymilvus import MilvusClient


def process_dict_array(dict_array):
    client = MilvusClient(
        uri=os.environ.get("MILVUS_URI"), token=os.environ.get("MILVUS_TOKEN"), secure='true'
    )
    descriptions = [item["text"] for item in dict_array]

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
    for i, item in enumerate(dict_array):
        item["vector"] = embedded_descriptions[i]

    client.insert(os.environ.get("MILVUS_COLLECTION"), dict_array)


def upload_helper_navigation_functions():
    for dict_array in [global_dict_array, screen_dict_array, track_dict_array, help_dict_array]:
        process_dict_array(dict_array)


upload_helper_navigation_functions()
