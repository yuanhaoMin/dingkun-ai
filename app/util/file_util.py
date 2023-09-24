import docx2txt
import os
import re
import typing
from pdfminer.high_level import extract_text


def create_prompt_from_template_file(filename: str, replacements: dict) -> str:
    file_path = os.path.join(os.getcwd(), "app", "constant", "prompt", filename)
    # 不用替换，直接传回文本内容
    if replacements is None:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    # 读取文件内容
    with open(file_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()
    # 用正则表达式替换
    for key, value in replacements.items():
        # 正则表达式模式匹配key后面跟着的内容，直到遇到}
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
    # Split the string into lines, filter out blank lines, and join the non-blank lines back into a string
    lines = input_str.splitlines()
    non_blank_lines = [line for line in lines if line.strip()]
    return "\n".join(non_blank_lines)
