import os
import docx2txt
from app.config.environment import (
    get_milvus_collection,
    get_milvus_token,
    get_milvus_uri,
)
from app.util.embeddings_util import get_embeddings_with_backoff
from datetime import datetime
from fastapi import UploadFile
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdfminer.high_level import extract_text
from pymilvus import MilvusClient


def persist_csv_file(uploadFile: UploadFile, user_id: str):
    folder_path = os.path.join(os.getcwd(), "data")
    file_path = os.path.join(folder_path, f"{user_id}.csv")
    with open(file_path, "wb") as buffer:
        buffer.write(uploadFile.file.read())


def process_and_persist_business_file(
    uploadFile: UploadFile,
    user_id: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
):
    doc = create_document_from_file(uploadFile, user_id)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    splitted_docs = text_splitter.split_documents([doc])

    text_list = [document.page_content for document in splitted_docs]
    metadata_list = [document.metadata for document in splitted_docs]
    vector_list = get_embeddings_with_backoff(text_list)

    list_of_rows = [
        {
            "filename": metadata["filename"],
            "text": text,
            "vector": vector,
            "creation_time": metadata["creation_time"],
        }
        for text, metadata, vector in zip(text_list, metadata_list, vector_list)
    ]

    client = MilvusClient(uri=get_milvus_uri(), token=get_milvus_token())
    client.insert(get_milvus_collection(), list_of_rows)


def create_document_from_file(uploadFile: UploadFile, user_id: str) -> list[Document]:
    # Determine file type and process accordingly
    if uploadFile.filename.endswith(".txt"):
        raw_text = uploadFile.file.read().decode("utf-8")
    elif uploadFile.filename.endswith(".pdf"):
        raw_text = extract_text(uploadFile.file)
    elif uploadFile.filename.endswith(".docx"):
        raw_text = docx2txt.process(uploadFile.file)
    else:
        raise ValueError("Unsupported file type")
    processed_text = remove_blank_lines(raw_text)
    # Prepare the metadata
    metadata = {
        "filename": uploadFile.filename,
        "creation_time": datetime.now().isoformat(),
        "user_id": user_id,
    }

    # Create a Document instance
    return Document(page_content=processed_text, metadata=metadata)


def remove_blank_lines(input_str: str) -> str:
    # Split the string into lines, filter out blank lines, and join the non-blank lines back into a string
    lines = input_str.splitlines()
    non_blank_lines = [line for line in lines if line.strip()]
    return "\n".join(non_blank_lines)
