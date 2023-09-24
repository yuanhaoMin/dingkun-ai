import docx2txt
import os
import re
import typing
from app.constant.path_constants import PROMPT_DIRECTORY_PATH
from pdfminer.high_level import extract_text


def create_prompt_from_template_file(filename: str, replacements: dict = None) -> str:
    file_path = os.path.join(PROMPT_DIRECTORY_PATH, filename)
    with open(file_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()
    if replacements is None:
        return prompt_template
    for key, value in replacements.items():
        pattern = re.escape(key) + r"\s*\{.*?\}"
        prompt_template = re.sub(pattern, value, prompt_template)
    return prompt_template


def extract_and_remove_blank_lines(filename: str, file: typing.BinaryIO) -> str:
    if filename.endswith(".txt"):
        raw_text = file.read().decode("utf-8")
    elif filename.endswith(".pdf"):
        raw_text = extract_text(file)
    elif filename.endswith(".docx"):
        raw_text = docx2txt.process(file)
    else:
        raise ValueError("Unsupported file type")
    return remove_blank_lines(raw_text)


def remove_blank_lines(input_str: str) -> str:
    lines = input_str.splitlines()
    non_blank_lines = [line for line in lines if line.strip()]
    return "\n".join(non_blank_lines)
