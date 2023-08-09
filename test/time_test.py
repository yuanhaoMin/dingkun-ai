import re

def replace_custom_format(text, replacements):
    for key, value in replacements.items():
        # 正则表达式模式匹配key后面跟着的内容，直到遇到}
        pattern = re.escape(key) + r'\s*\{.*?\}'
        text = re.sub(pattern, value, text)
    return text

# 示例
template = """
The appointment time should be in the format "YYYY-MM-DD [上午/下午]", for instance, based on the current date "current_time: {current_time}".current_time: {current_time}
Text to extract from: {text}
"""

replacements = {
    "current_time:": "2023-08-09",
    "Text to extract from:": "hello"
}

print(replace_custom_format(template, replacements))
