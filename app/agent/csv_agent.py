import inspect
import json

from langchain import OpenAI
from langchain.agents import create_csv_agent
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage


# OpenAI()默认使用text-davinci-003 效果似乎好于gpt-3.5-turbo
# 问无关问题会返回none
def query_csv(file_path: str, query: str, temperature: int = 0) -> str:
    agent = create_csv_agent(OpenAI(temperature=temperature), file_path)
    return agent.run(query)


def get_function_parameter_names(function):
    if function is not None and inspect.isfunction(function):
        parameter_names = inspect.signature(function).parameters.keys()
        return list(parameter_names)
    else:
        return None


functions = [
    {
        "name": "document_answer_service",
        "description": "Provide answers or services related to document files such as .txt, .pdf, and .docx.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file."
                },
                "question": {
                    "type": "string",
                    "description": "Question related to the document."
                }
            },
            "required": ["file_path", "question"]
        }
    }
]


def auto_process_csv_with_llm(message):
    model = 'gpt-3.5-turbo-0613'
    llm = ChatOpenAI(model=model)
    function_descriptions = functions
    system_prompt = """
        你是名为“定坤”的智能客服助理。你的主要功能是从用户的信息中发现需求去调用执行数据分析服务。始终确保你的回答是准确、及时和有帮助的。
        你是一个热心、礼貌和诚实的助理。始终尽可能地提供有帮助的回答，同时要确保安全。你的回答不应包括任何有害、不道德、种族主义、性别歧视、有毒、危险或非法的内容。请确保你的回应在社交上是无偏见的，并且本质上是积极的。
        如果一个问题没有任何意义，或者在事实上并不连贯，请解释原因，而不是回答不正确的内容。如果你不知道某个问题的答案，或者用户的请求与你的功能不匹配，请明确告知并提供适当的建议，而不是分享虚假信息。
        """
    messages = [SystemMessage(content=system_prompt)]
    messages.append(HumanMessage(content=message))

    # 使用llm预测消息
    response = llm.predict_messages(messages, functions=function_descriptions)

    # 检查是否有函数调用的请求
    function_call = response.additional_kwargs.get("function_call")
    if function_call:
        # 获取函数名和参数
        function_name = function_call["name"]
        arguments = json.loads(function_call["arguments"])

        # 调用函数
        the_function = globals().get(function_name)
        if the_function:  # 确保函数存在
            parameter_names = get_function_parameter_names(the_function)
            parameter_values = [arguments[parameter_name] for parameter_name in parameter_names]
            returned_value = the_function(*parameter_values)
            return f"{returned_value}"
        else:
            return f"函数 {function_name} 不存在。"
    else:
        return f"{response.content}"
