import inspect
import json
from langchain.schema import SystemMessage, HumanMessage, ChatMessage, AIMessage
import logging
from app.agent.helper_agent import query_csv, navigate_to_page, answer_documentation


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
        self.logger.debug("开始 process 函数。")

        self.logger.debug(f"接收到用户输入: {user_input}")
        self.messages.append(HumanMessage(content=user_input))

        # 使用llm预测消息
        response = self.llm.predict_messages(self.messages, functions=self.function_descriptions)
        self.logger.debug(f"从llm获得响应: {response}")

        # 将日志信息存储到字典
        log_info = {
            'user_input': user_input,
            'llm_response': response.additional_kwargs
        }
        self.log_messages.append(log_info)

        # 检查是否有函数调用的请求
        function_call = response.additional_kwargs.get("function_call")
        if function_call:
            self.logger.debug("检测到函数调用请求。")

            # 获取函数名和参数
            function_name = function_call["name"]
            arguments = json.loads(function_call["arguments"])

            # 调用函数
            the_function = globals().get(function_name)

            if the_function:  # 确保函数存在
                self.logger.debug(f"准备调用函数: {function_name}，参数为: {arguments}")

                parameter_names = get_function_parameter_names(the_function)
                parameter_values = [arguments[parameter_name] for parameter_name in parameter_names]
                returned_value = the_function(*parameter_values)

                self.logger.debug(f"函数 {function_name} 返回值为: {returned_value}")

                # 更新消息列表，为下一次迭代做准备
                self.messages.append(AIMessage(content=str(response.additional_kwargs)))
                self.messages.append(
                    ChatMessage(role='function', additional_kwargs={'name': function_name}, content=returned_value))
            else:
                self.logger.warning(f"函数 {function_name} 不存在。")
        else:
            self.logger.debug("未检测到函数调用请求。")
            self.messages.append(
                AIMessage(content=response.content))

        # 保证消息列表只有5条消息
        while len(self.messages) > 5:
            popped_message = self.messages.pop(0)
            self.logger.debug(f"从消息列表中删除一条消息: {popped_message}")
        messages_str = self.get_messages_with_role_and_content()
        self.logger.debug(f"Messages with role and content: {messages_str}")
        return f"{response.content if not function_call else returned_value}"

    def print_messages_content(self):
        for idx, message in enumerate(self.messages, 1):
            self.logger.debug(f"消息 {idx}: {message.content}")

    def get_messages_with_role_and_content(self):
        messages_info = []

        for message in self.messages:
            if isinstance(message, ChatMessage):
                info = {
                    'role': message.role,
                    'content': message.content
                }
            else:
                info = {
                    'role': message.type,  # 使用消息的类型作为默认的角色
                    'content': message.content
                }
            messages_info.append(info)

        # 返回转化为字符串的字典列表，并确保中文字符不会被转化为ASCII
        return json.dumps(messages_info, ensure_ascii=False)


def get_function_parameter_names(function):
    if function is not None and inspect.isfunction(function):
        parameter_names = inspect.signature(function).parameters.keys()
        return list(parameter_names)
    else:
        return None
