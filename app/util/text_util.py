import os
import re


def create_prompt_from_template_file(filename: str, replacements: dict) -> str:
    # 获取当前文件的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 使用这个路径来定义文件路径
    file_path = os.path.normpath(
        os.path.join(current_dir, "../", "constant", "prompt", filename)
    )

    # 不用替换，直接传回文本内容
    if replacements is None:
        with open(file_path, 'r', encoding='utf-8') as file:
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
