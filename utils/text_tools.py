import re
import os


def insert_text(filename, pattern, content_to_insert):
    # 获取当前文件的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 使用这个路径来定义文件路径
    file_path = os.path.normpath(os.path.join(current_dir, "..", "prompts", filename))

    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # 使用正则表达式来查找并替换指定模式中的内容
    modified_content = re.sub(f"{re.escape(pattern)} \{{.*?\}}", f"{pattern} {content_to_insert}", file_content)

    return modified_content


# 示例
# result = insert_text("visitor_regist_prompts", "Text to extract from:", "hello")
# print(result)
