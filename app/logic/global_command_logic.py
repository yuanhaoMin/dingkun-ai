import time
import logging
from langchain.embeddings import OpenAIEmbeddings
from app.config.milvus_db import get_milvus_client, MILVUS_COLLECTION, milvus_client_search
from app.util.structured_text_util import (
    determine_extraction_function_based_on_missing_data,
    update_missing_json_values_with_llm,
)
from typing import Union


log = logging.getLogger(__name__)


def parse_text_command(text: str, route: str):
    start_time = time.time()
    embedded_text = OpenAIEmbeddings().embed_query(text)
    end_time = time.time()
    log.debug("Embedding time: %s seconds", end_time - start_time)
    start_time = time.time()
    filter_condition = f"scope in ['{route.name}', 'Global']"
    print(filter_condition)
    response = milvus_client_search(
        collection_name=MILVUS_COLLECTION,
        data=[embedded_text],
        limit=1,
        search_filter=filter_condition,
        output_fields=[
            "text",
            "route",
            "start_time",
            "name",
            "end_time",
            "page",
            "listRows",
            "label",
            "operation",
            "content",
        ],
    )
    end_time = time.time()
    log.debug("Milvus search time: %s seconds", end_time - start_time)

    start_time = time.time()
    distance = response[0][0].get("distance")
    entity = response[0][0].get("entity", {})
    end_time = time.time()
    log.debug("Entity parsing time: %s seconds", end_time - start_time)

    if distance > 0.3:
        entity["route"] = None
        entity["operation"] = "stop"
        entity["text"] = "未能理解您的操作"
        return entity

    start_time = time.time()
    function_description: Union[
        dict, None
    ] = determine_extraction_function_based_on_missing_data(entity)
    end_time = time.time()
    log.debug("Data extraction function time: %s seconds", end_time - start_time)

    start_time = time.time()
    if function_description is None:
        if entity.get("route") == route:
            entity["route"] = None
        return entity

    updated_entity = update_missing_json_values_with_llm(
        json_data=entity, question=text, function_descriptions=function_description
    )

    if updated_entity.get("route") == route:
        updated_entity["route"] = None
    end_time = time.time()
    log.debug("Data update time: %s seconds", end_time - start_time)

    return updated_entity

