import logging
from app.config.environment import get_openai_key
from fastapi import HTTPException
from openai import ChatCompletion
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt

logger = logging.getLogger(__name__)


def chat_completion_no_functions(messages: list[dict]) -> str:
    contents = []
    retry_count = 0
    max_retries = 2
    while True:
        try:
            response = ChatCompletion.create(
                api_key=get_openai_key(),
                model="gpt-3.5-turbo",
                messages=messages,
                request_timeout=2,
                temperature=0,
                stream=True,
            )
            for stream_response in response:
                delta = stream_response["choices"][0]["delta"]
                finish_reason = stream_response["choices"][0]["finish_reason"]
                if hasattr(delta, "content"):
                    contents.append(delta.content)
                if finish_reason == "stop":
                    full_response_text = "".join(contents)
            return full_response_text
        except Exception as e:
            retry_count += 1
            if retry_count > max_retries:
                raise HTTPException(
                    status_code=504,
                    detail=f"Failed to get chat completion response from OpenAI API after {max_retries} retries. Error: {e}",
                )
            else:
                logger.warning(
                    "Failed to get chat completion response from OpenAI API. Retrying... Error: {e}"
                )
                continue


class Conversation:
    def __init__(self, prompt, num_of_round, function_map=None):
        self.prompt = prompt
        self.num_of_round = num_of_round
        self.function_map = function_map or {}
        self.messages = []
        self.messages.append({"role": "system", "content": self.prompt})

    def ask(self, question):
        self.messages.append({"role": "user", "content": question})
        ai_response = chat_completion_no_functions(self.messages)

        self.messages.append({"role": "assistant", "content": ai_response})

        if len(self.messages) > self.num_of_round * 2 + 1:
            del self.messages[1:3]
        return ai_response

    def ask_functions(self, question, functions=None):
        self.messages.append({"role": "user", "content": question})
        ai_response = self.chat_session(functions)
        self.messages.append({"role": "assistant", "content": ai_response})
        # 保持会话长度，确保不超过指定的轮数
        if len(self.messages) > self.num_of_round * 2 + 1:
            del self.messages[1:3]
        return ai_response

    def save_messages_to_file(self, filename="temp.txt"):
        with open(filename, "w", encoding="utf-8") as file:
            for message in self.messages:
                file.write(f"{message['role']}: {message['content']}\n")

    def chat_session(self, functions=None):
        while True:
            response = chat_completion_with_functions(
                self.messages, functions=functions
            )
            response = response.json()
            if (
                "finish_reason" in response
                and response["finish_reason"] == "function_call"
            ):
                function_name = response["choices"][0]["message"]["function_call"][
                    "name"
                ]
                arguments = eval(
                    response["choices"][0]["message"]["function_call"]["arguments"]
                )
                func = self.function_map.get(function_name)
                if func:
                    function_result = func(**arguments)
                    # 将功能的结果添加到消息列表中，以便GPT可以使用它作为上下文
                    self.messages.append({"role": "system", "content": function_result})
                else:
                    raise ValueError(f"Function {function_name} not found")
            else:
                # 如果没有更多的功能调用，返回GPT的回复
                return response["choices"][0]["message"]["content"]


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_with_functions(
    messages, functions=None, function_call=None, model="gpt-3.5-turbo"
):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + get_openai_key(),
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        logger.warning(
            f"Failed to get function call response from OpenAI API. Retrying... Error: {e}"
        )
