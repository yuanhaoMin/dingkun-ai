from app.util.time_utll import get_current_date_and_day

current_date, day_of_week = get_current_date_and_day()
function_csv = [
    {
        "name": "query_csv",
        "description": "Provide data analysis services, especially when detecting .csv files or explicit data "
                       "analysis requests.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the data file.如果你不知道具体请询问用户。"
                },
                "query": {
                    "type": "string",
                    "description": "Query or request related to data analysis in chinese."
                }
            },
            "required": ["file_path", "query"]
        }
    }
]
function_navigation = [
    {
        "name": "navigate_to_page",
        "description": "Help users navigate to the desired page.",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "User-described natural language requirements in chinese."
                }
            },
            "required": ["page_name"]
        }
    }
]
function_create_documentation = [
    {
        "name": "answer_documentation",
        "description": "Answer questions related to company's documentation, rules, and regulations.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Specific question about the document or rule."
                }
            },
            "required": ["question"]
        }
    }
]
csv_system_prompt = """
        你是名为“定坤”，热心、礼貌和诚实的助理。你的主要功能是从用户的信息中发现需求去调用执行数据分析服务。始终确保你的回答是准确、及时和有帮助的。
        你的回答不应包括任何有害、不道德、种族主义、性别歧视、有毒、危险或非法的内容。
        如果一个问题没有任何意义，或者在事实上并不连贯，请解释原因，而不是回答不正确的内容。
        如果你不知道某个问题的答案，或者用户的请求与你的功能不匹配，请明确告知并提供适当的建议，而不是分享虚假信息不要假设要插入函数的值是什么。如果函数的值没有明确指定，请寻求澄清。
""" + f"今天是 {current_date}, {day_of_week}."

documentation_system_prompt = """
        你是名为“定坤”，热心、礼貌和诚实的助理。你的主要功能是回答与公司的文档、规章和制度相关的问题。
        你的回答不应包括任何有害、不道德、种族主义、性别歧视、有毒、危险或非法的内容。
        如如果一个问题没有任何意义，或者在事实上并不连贯，请解释原因，而不是回答不正确的内容。
        如果你不知道某个问题的答案，或者用户的请求与你的功能不匹配，请明确告知并提供适当的建议，而不是分享虚假信息。
        不要假设要插入函数的值是什么。如果函数的值没有明确指定，请寻求澄清。
""" + f"今天是 {current_date}, {day_of_week}."

navigation_system_prompt = """
        你是名为“定坤”，热心、礼貌和诚实的助理。你的主要功能是帮助用户导航到他们想要的页面。
        你的回答不应包括任何有害、不道德、种族主义、性别歧视、有毒、危险或非法的内容。
        如果一个问题没有任何意义，或者在事实上并不连贯，请解释原因，而不是回答不正确的内容。
        如果你不知道某个问题的答案，或者用户的请求与你的功能不匹配，请明确告知并提供适当的建议，而不是分享虚假信息。
        不要假设要插入函数的值是什么。如果函数的值没有明确指定，请寻求澄清。
""" + f"今天是 {current_date}, {day_of_week}."


name_time_start_time_end = [
    {
        "name": "extracting",
        "description": "extracting",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
                "time_start": {
                    "type": "string",
                    "description": "Start time in the format '2023-09-20 11:00'."
                },
                "time_end": {
                    "type": "string",
                    "description": "End time in the format '2023-09-20 12:00'. '"
                }
            },
            "required": ["name", "time_start", "time_end"]
        }
    }
]

name_extract = [
    {
        "name": "extracting",
        "description": "extracting",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                }
            },
            "required": ["file_path", "query"]
        }
    }
]
