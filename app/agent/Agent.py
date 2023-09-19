import inspect
import json
from langchain.schema import SystemMessage, HumanMessage, ChatMessage, AIMessage
import logging

from app.agent.helper_agent import query_csv, navigate_to_page




class AutoProcessor:
    def __init__(self, system_prompt, model, llm, function_descriptions):
        self.system_prompt = system_prompt
        self.model = model
        self.llm = llm
        self.function_descriptions = function_descriptions
        self.messages = [SystemMessage(content=self.system_prompt)]

        # 初始化日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.log_messages = []

    def update_function_descriptions(self, new_function_descriptions):
        self.function_descriptions = new_function_descriptions

    def process(self, user_input):
        self.messages.append(HumanMessage(content=user_input))

        # 使用llm预测消息
        response = self.llm.predict_messages(self.messages, functions=self.function_descriptions)

        # 将日志信息存储到字典
        log_info = {
            'user_input': user_input,
            'llm_response': response.additional_kwargs
        }
        self.log_messages.append(log_info)

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

                # 更新消息列表，为下一次迭代做准备
                self.messages.append(AIMessage(content=str(response.additional_kwargs)))
                self.messages.append(
                    ChatMessage(role='function', additional_kwargs={'name': function_name}, content=returned_value))

                # 保证消息列表只有5条消息
                while len(self.messages) > 5:
                    self.messages.pop(0)

                return f"{returned_value}"
            else:
                return f"函数 {function_name} 不存在。"
        else:
            # 保证消息列表只有5条消息
            while len(self.messages) > 5:
                self.messages.pop(0)

            return f"{response.content}"


def get_function_parameter_names(function):
    if function is not None and inspect.isfunction(function):
        parameter_names = inspect.signature(function).parameters.keys()
        return list(parameter_names)
    else:
        return None
