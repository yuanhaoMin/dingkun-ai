import copy
import os
import shutil
from pathlib import Path
from typing import *

import openai

from app.config.api_config import get_config, config
from app.interpreter.jupyter_backend import JupyterKernel

functions = [
    {
        "name": "execute_code",
        "description": "This function allows you to execute Python code and retrieve the terminal output. If the code "
                       "generates image output, the function will return the text '[image]'. The code is sent to a "
                       "Jupyter kernel for execution. The kernel will remain active after execution, retaining all "
                       "variables in memory.",
        "parameters": {
            "type": "object",
            "properties": {"code": {"type": "string", "description": "The code text"}},
            "required": ["code"],
        },
    }
]
# functions.extend([
#     {
#         "name": "process_text_file",
#         "description": "This function allows you to process a given text file. You only need to provide the filename, and the AI will handle the rest.",
#         "parameters": {
#             "type": "object",
#             "properties": {"filename": {"type": "string", "description": "The name of the uploaded text file."}},
#             "required": ["filename"],
#         },
#     }
# ])


system_msg = """You are an AI code interpreter.
Your goal is to help users do a variety of jobs by executing Python code.

You should:
1. Comprehend the user's requirements carefully & 



to the letter. 
2. Give a brief description for what you plan to do & call the execute_code function to run code
3. Provide results analysis based on the execution output. 
4. If error occurred, try to fix it.

Note: If the user uploads a file, you will receive a system message "User uploaded a file: filename". Use the filename as the path in the code. """

def config_openai_api(api_type, api_base, api_version, api_key):
    openai.api_type = api_type
    openai.api_base = api_base
    openai.api_version = api_version
    openai.api_key = api_key


class GPTResponseLog:
    def __init__(self):
        self.assistant_role_name = ""
        self.content = ""
        self.function_name = None
        self.function_args_str = ""
        self.display_code_block = ""
        self.finish_reason = "stop"
        self.bot_history = None

    def reset_gpt_response_log_values(self, exclude=None):
        if exclude is None:
            exclude = []

        attributes = {
            "assistant_role_name": "",
            "content": "",
            "function_name": None,
            "function_args_str": "",
            "display_code_block": "",
            "finish_reason": "stop",
            "bot_history": None,
        }

        for attr_name in exclude:
            del attributes[attr_name]
        for attr_name, value in attributes.items():
            setattr(self, attr_name, value)

    def set_assistant_role_name(self, assistant_role_name: str):
        self.assistant_role_name = assistant_role_name

    def add_content(self, content: str):
        self.content += content

    def set_function_name(self, function_name: str):
        self.function_name = function_name

    def copy_current_bot_history(self, bot_history: List):
        self.bot_history = copy.deepcopy(bot_history)

    def add_function_args_str(self, function_args_str: str):
        self.function_args_str += function_args_str

    def update_display_code_block(self, display_code_block):
        self.display_code_block = display_code_block

    def update_finish_reason(self, finish_reason: str):
        self.finish_reason = finish_reason


class BotBackend(GPTResponseLog):
    def __init__(self):
        super().__init__()
        self.unique_id = hash(id(self))
        self.jupyter_work_dir = f"cache/work_dir_{self.unique_id}"
        self.jupyter_kernel = JupyterKernel(work_dir=self.jupyter_work_dir)
        self.gpt_model_choice = "GPT-3.5"
        self.revocable_files = []
        self._init_conversation()
        self._init_api_config()
        self._init_kwargs_for_chat_completion()

    def _init_conversation(self):
        first_system_msg = {"role": "system", "content": system_msg}
        if hasattr(self, "conversation"):
            self.conversation.clear()
            self.conversation.append(first_system_msg)
        else:
            self.conversation: List[Dict] = [first_system_msg]

    def _init_api_config(self):
        self.config = get_config()
        api_type = self.config["API_TYPE"]
        api_base = self.config["API_base"]
        api_version = self.config["API_VERSION"]
        api_key = config["API_KEY"]
        config_openai_api(api_type, api_base, api_version, api_key)

    def _init_kwargs_for_chat_completion(self):
        self.kwargs_for_chat_completion = {
            "stream": True,
            "messages": self.conversation,
            "functions": functions,
            "function_call": "auto",
        }

        model_name = self.config["model"][self.gpt_model_choice]["model_name"]

        if self.config["API_TYPE"] == "azure":
            self.kwargs_for_chat_completion["engine"] = model_name
        else:
            self.kwargs_for_chat_completion["model"] = model_name

    def _clear_all_files_in_work_dir(self):
        for filename in os.listdir(self.jupyter_work_dir):
            os.remove(os.path.join(self.jupyter_work_dir, filename))

    def add_gpt_response_content_message(self):
        self.conversation.append(
            {"role": self.assistant_role_name, "content": self.content}
        )

    def add_text_message(self, user_text):
        """
            添加用户文本消息到对话中。
            :param user_text: 用户的文本内容
        """
        self.conversation.append({"role": "user", "content": user_text})
        self.revocable_files.clear()
        self.update_finish_reason(finish_reason="new_input")

    def add_file_message(self, file, bot_msg):
        # filename = os.path.basename(path)
        work_dir = self.jupyter_work_dir
        file_location = f"{work_dir}/{file.filename}"
        Path(work_dir).mkdir(parents=True, exist_ok=True)
        with open(file_location, "wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # shutil.copy(path, work_dir)

        gpt_msg = {
            "role": "system",
            "content": f"User uploaded a file: {file.filename}",
        }
        self.conversation.append(gpt_msg)
        self.revocable_files.append(
            {
                "bot_msg": bot_msg,
                "gpt_msg": gpt_msg,
                "path": os.path.join(work_dir, file.filename),
            }
        )

    def add_function_call_response_message(
            self, function_response: str, save_tokens=True
    ):
        """
            添加函数调用的响应消息到对话中。

            :param function_response: 函数的响应内容
            :param save_tokens: 是否保存tokens
        """
        self.conversation.append(
            {
                "role": self.assistant_role_name,
                "name": self.function_name,
                "content": self.function_args_str,
            }
        )

        if save_tokens and len(function_response) > 500:
            function_response = (
                f"{function_response[:200]}\n[Output too much, the middle part output is omitted]\n "
                f"End part of output:\n{function_response[-200:]}"
            )
        self.conversation.append(
            {
                "role": "function",
                "name": self.function_name,
                "content": function_response,
            }
        )

    def revoke_file(self):
        """
            撤销文件上传操作。
            :return: 如果有文件被撤销则返回相应的机器人消息，否则返回None。
        """
        if self.revocable_files:
            file = self.revocable_files[-1]
            bot_msg = file["bot_msg"]
            gpt_msg = file["gpt_msg"]
            path = file["path"]

            assert self.conversation[-1] is gpt_msg
            del self.conversation[-1]

            os.remove(path)

            del self.revocable_files[-1]

            return bot_msg
        else:
            return None

    def update_gpt_model_choice(self, model_choice):
        self.gpt_model_choice = model_choice
        self._init_kwargs_for_chat_completion()

    def restart(self):
        """
            重启机器人后端，清除工作目录中的所有文件并重置对话。
        """
        self._clear_all_files_in_work_dir()
        self.revocable_files.clear()
        self._init_conversation()
        self.reset_gpt_response_log_values()
        self.jupyter_kernel.restart_jupyter_kernel()
