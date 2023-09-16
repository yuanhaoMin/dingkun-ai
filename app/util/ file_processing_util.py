import docx2txt
import tiktoken
from fastapi import UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdfminer.high_level import extract_text


def process_docx_to_str(file: UploadFile) -> str:
    raw_text = docx2txt.process(file)
    processed_text = remove_blank_lines(raw_text)
    return processed_text


def process_pdf_to_str(file: UploadFile) -> str:
    raw_text = extract_text(file)
    processed_text = remove_blank_lines(raw_text)
    return processed_text


def remove_blank_lines(input_str: str) -> str:
    # Split the string into lines, filter out blank lines, and join the non-blank lines back into a string
    lines = input_str.splitlines()
    non_blank_lines = [line for line in lines if line.strip()]
    return "\n".join(non_blank_lines)


enc = tiktoken.get_encoding("cl100k_base")


def length_function(text: str) -> int:
    return len(enc.encode(text))


def split_content_into_chunks(text):
    # 参考官网链接：https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/character_text_splitter
    text_spliter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""],
                                                  chunk_size=500,
                                                  chunk_overlap=80,
                                                  length_function=length_function)
    chunks = text_spliter.split_text(text)
    return chunks
