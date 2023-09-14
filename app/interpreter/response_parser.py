import copy
import json
from abc import ABCMeta, abstractmethod
from typing import List

from app.interpreter.bot_backend import BotBackend
from app.interpreter.functional import parse_json, add_function_response_to_bot_history


class ChoiceStrategy(metaclass=ABCMeta):
    """
    ChoiceStrategy 抽象基类

    所有选择策略应该从此基类继承，并实现其抽象方法。

    属性:
    - choice (dict): 从模型的响应中获取的选择。
    - delta (dict): 选择中的delta字段，通常包含执行某些操作的具体细节。

    抽象方法:
    - support(): 判断此策略是否支持当前的选择。
    - execute(): 执行策略并返回相关结果。
    """

    def __init__(self, choice):
        """
        构造函数

        参数:
        - choice (dict): 从模型的响应中获取的选择。
        """
        self.choice = choice
        self.delta = choice["delta"]

    @abstractmethod
    def support(self):
        pass

    @abstractmethod
    def execute(self, bot_backend: BotBackend, history: List, whether_exit: bool):
        pass


class RoleChoiceStrategy(ChoiceStrategy):
    """
    RoleChoiceStrategy 类

    此策略处理选择中的角色部分。

    方法:
    - support(): 判断此策略是否支持当前的选择。
    - execute(): 执行策略并返回相关结果。
    """

    def support(self):
        """
        判断是否在 delta 中存在 'role' 字段。

        返回:
        - bool: 如果存在 'role' 字段则返回 True，否则返回 False。
        """
        return "role" in self.delta

    def execute(self, bot_backend: BotBackend, history: List, whether_exit: bool):
        """
        执行策略并更新助手的角色名称。

        参数:
        - bot_backend (BotBackend): Bot 的后端实例。
        - history (List): 当前的历史记录。
        - whether_exit (bool): 标记是否退出。

        返回:
        - tuple: 更新后的历史记录和 whether_exit 标记。
        """
        bot_backend.set_assistant_role_name(assistant_role_name=self.delta["role"])
        return history, whether_exit


class ContentChoiceStrategy(ChoiceStrategy):
    """
    ContentChoiceStrategy 类

    此策略处理选择中的内容部分。

    方法:
    - support(): 判断此策略是否支持当前的选择。
    - execute(): 执行策略并返回相关结果。
    """

    def support(self):
        """
        判断是否在 delta 中存在 'content' 字段且其值不为 None。

        返回:
        - bool: 如果条件满足则返回 True，否则返回 False。
        """
        return "content" in self.delta and self.delta["content"] is not None

    def execute(self, bot_backend: BotBackend, history: List, whether_exit: bool):
        """
        执行策略并更新内容。

        参数:
        - bot_backend (BotBackend): Bot 的后端实例。
        - history (List): 当前的历史记录。
        - whether_exit (bool): 标记是否退出。

        返回:
        - tuple: 更新后的历史记录和 whether_exit 标记。
        """
        # null value of content often occur in function call:
        #     {
        #       "role": "assistant",
        #       "content": null,
        #       "function_call": {
        #         "name": "python",
        #         "arguments": ""
        #       }
        #     }
        bot_backend.add_content(content=self.delta.get("content", ""))
        history[-1][1] = bot_backend.content
        return history, whether_exit


class NameFunctionCallChoiceStrategy(ChoiceStrategy):
    """
       NameFunctionCallChoiceStrategy 类

       这个类的主要职责是处理函数调用的名称相关的选择策略。

       方法:
       - support(): 判断当前的策略是否适用。
       - execute(): 执行具体的策略操作。
       """
    def support(self):
        """
            判断当前的 delta 是否包含 "function_call" 以及其子项 "name"。

            返回:
                bool: 如果 delta 包含所需的项则返回 True，否则返回 False。
        """
        return "function_call" in self.delta and "name" in self.delta["function_call"]

    def execute(self, bot_backend: BotBackend, history: List, whether_exit: bool):
        """
            执行策略操作。设置函数名并检查是否存在于 available_functions 字典中。

            参数:
                bot_backend (BotBackend): Bot 后端实例。
                history (List): 当前的历史记录。
                whether_exit (bool): 标记是否退出。

            返回:
                tuple: 更新后的历史记录和 whether_exit 标记。
         """
        function_dict = bot_backend.jupyter_kernel.available_functions
        bot_backend.set_function_name(function_name=self.delta["function_call"]["name"])
        bot_backend.copy_current_bot_history(bot_history=history)
        if bot_backend.function_name not in function_dict:
            history.append(
                [
                    None,
                    f"GPT attempted to call a function that does "
                    f"not exist: {bot_backend.function_name}\n ",
                ]
            )
            whether_exit = True

        return history, whether_exit


class ArgumentsFunctionCallChoiceStrategy(ChoiceStrategy):
    """
        ArgumentsFunctionCallChoiceStrategy 类

        这个类的主要职责是处理包含参数的函数调用的选择策略。

        方法:
        - support(): 判断当前的策略是否适用。
        - execute(): 执行具体的策略操作。
    """
    def support(self):
        """
            判断当前的 delta 是否包含 "function_call" 以及其子项 "arguments"。

            返回:
                bool: 如果 delta 包含所需的项则返回 True，否则返回 False。
        """
        return (
            "function_call" in self.delta and "arguments" in self.delta["function_call"]
        )

    def execute(self, bot_backend: BotBackend, history: List, whether_exit: bool):
        """
            执行策略操作。设置函数调用的参数，并根据参数的类型进行特定处理。

            参数:
                bot_backend (BotBackend): Bot 后端实例。
                history (List): 当前的历史记录。
                whether_exit (bool): 标记是否退出。

            返回:
                tuple: 更新后的历史记录和 whether_exit 标记。
        """

        bot_backend.add_function_args_str(
            function_args_str=self.delta["function_call"]["arguments"]
        )

        if bot_backend.function_name == "python":  # handle hallucinatory function calls
            """
            In practice, we have noticed that GPT, especially GPT-3.5, may occasionally produce hallucinatory
            function calls. These calls involve a non-existent function named `python` with arguments consisting
            solely of raw code text (not a JSON format).
            """
            temp_code_str = bot_backend.function_args_str
            bot_backend.update_display_code_block(
                display_code_block="\n🔴Working:\n```python\n{}\n```".format(
                    temp_code_str
                )
            )
            history = copy.deepcopy(bot_backend.bot_history)
            history[-1][1] += bot_backend.display_code_block
        else:
            temp_code_str = parse_json(
                function_args=bot_backend.function_args_str, finished=False
            )
            if temp_code_str is not None:
                bot_backend.update_display_code_block(
                    display_code_block="\n🔴Working:\n```python\n{}\n```".format(
                        temp_code_str
                    )
                )
                history = copy.deepcopy(bot_backend.bot_history)
                history[-1][1] += bot_backend.display_code_block

        return history, whether_exit


class FinishReasonChoiceStrategy(ChoiceStrategy):
    """
        FinishReasonChoiceStrategy 类

        这个类主要处理基于完成原因的选择策略。

        方法:
        - support(): 判断当前的 choice 是否有 "finish_reason"。
        - execute(): 执行具体的策略操作。
    """
    def support(self):
        """
            检查当前的 choice 是否有 "finish_reason" 属性。

            返回:
                bool: 如果 choice 有 "finish_reason" 属性则返回 True，否则返回 False。
        """
        return self.choice["finish_reason"] is not None

    def execute(self, bot_backend: BotBackend, history: List, whether_exit: bool):
        """
            执行策略操作。如果完成原因是function_call，则会尝试执行相关代码。

            参数:
                bot_backend (BotBackend): Bot 后端实例。
                history (List): 当前的历史记录。
                whether_exit (bool): 标记是否退出。

            返回:
                tuple: 更新后的历史记录和 whether_exit 标记。
        """
        function_dict = bot_backend.jupyter_kernel.available_functions

        if bot_backend.content:
            bot_backend.add_gpt_response_content_message()

        bot_backend.update_finish_reason(finish_reason=self.choice["finish_reason"])
        if bot_backend.finish_reason == "function_call":
            try:
                code_str = self.get_code_str(bot_backend)

                bot_backend.update_display_code_block(
                    display_code_block="\n🟢Working:\n```python\n{}\n```".format(
                        code_str
                    )
                )
                history = copy.deepcopy(bot_backend.bot_history)
                history[-1][1] += bot_backend.display_code_block

                # function response
                text_to_gpt, content_to_display = function_dict[
                    bot_backend.function_name
                ](code_str)

                # add function call to conversion
                bot_backend.add_function_call_response_message(
                    function_response=text_to_gpt, save_tokens=True
                )

                add_function_response_to_bot_history(
                    content_to_display=content_to_display,
                    history=history,
                    unique_id=bot_backend.unique_id,
                )

            except json.JSONDecodeError:
                history.append(
                    [
                        None,
                        f"GPT generate wrong function args: {bot_backend.function_args_str}",
                    ]
                )
                whether_exit = True
                return history, whether_exit

            except Exception as e:
                history.append([None, f"Backend error: {e}"])
                whether_exit = True
                return history, whether_exit

        bot_backend.reset_gpt_response_log_values(exclude=["finish_reason"])

        return history, whether_exit

    @staticmethod
    def get_code_str(bot_backend):
        if bot_backend.function_name == "python":
            code_str = bot_backend.function_args_str
        else:
            code_str = parse_json(
                function_args=bot_backend.function_args_str, finished=True
            )
            if code_str is None:
                raise json.JSONDecodeError
        return code_str


class ChoiceHandler:
    """
        ChoiceHandler 类

        这个类的主要职责是处理不同的选择策略，并决定使用哪种策略来处理给定的选择。

        属性:
        - strategies: 包含所有可用策略类的列表。

        方法:
        - handle(): 遍历所有策略，找到支持当前选择的策略并执行它。
    """
    strategies = [
        RoleChoiceStrategy,
        ContentChoiceStrategy,
        NameFunctionCallChoiceStrategy,
        ArgumentsFunctionCallChoiceStrategy,
        FinishReasonChoiceStrategy,
    ]

    def __init__(self, choice):
        self.choice = choice

    def handle(self, bot_backend: BotBackend, history: List, whether_exit: bool):
        """
        处理给定的选择。

        遍历所有策略，查找一个支持当前选择的策略并执行它。

        参数:
        - bot_backend (BotBackend): Bot 的后端实例。
        - history (List): 当前的历史记录。
        - whether_exit (bool): 标记是否退出。

        返回:
        - tuple: 更新后的历史记录和 whether_exit 标记。
        """
        for Strategy in self.strategies:
            strategy_instance = Strategy(choice=self.choice)
            if not strategy_instance.support():
                continue
            history, whether_exit = strategy_instance.execute(
                bot_backend=bot_backend, history=history, whether_exit=whether_exit
            )
        return history, whether_exit


def parse_response(chunk, history, bot_backend: BotBackend):
    """
    解析模型的响应并处理其中的选择。

    参数:
    - chunk (dict): 模型的响应片段。
    - history (List): 当前的历史记录。
    - bot_backend (BotBackend): Bot 的后端实例。

    返回:
    - tuple: 更新后的历史记录和 whether_exit 标记。
    """
    whether_exit = False
    print(chunk)
    if chunk["choices"]:
        choice = chunk["choices"][0]
        choice_handler = ChoiceHandler(choice=choice)
        history, whether_exit = choice_handler.handle(
            history=history, bot_backend=bot_backend, whether_exit=whether_exit
        )

    return history, whether_exit
