import re
import os


def create_prompt_from_template_file(
    filename: str, pattern: str, content_to_insert: str
) -> str:
    # 获取当前文件的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 使用这个路径来定义文件路径
    file_path = os.path.normpath(
        os.path.join(current_dir, "..", "constant", "prompt", filename)
    )

    # 读取文件内容
    with open(file_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    # 使用正则表达式来查找并替换指定模式中的内容
    prompt = re.sub(
        f"{re.escape(pattern)} \{{.*?\}}",
        f"{pattern} {content_to_insert}",
        prompt_template,
    )
    return prompt
