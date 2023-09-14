import re


def replace_custom_format(text, replacements):
    for key, value in replacements.items():
        # 正则表达式模式匹配key后面跟着的内容，直到遇到}
        pattern = re.escape(key) + r'\s*\{.*?\}'
        text = re.sub(pattern, value, text)
    return text



