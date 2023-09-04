import logging
from app.config.api_config import get_openai_key
from fastapi import HTTPException
from openai import ChatCompletion
import json
import openai
import requests

# from tenacity import retry, wait_random_exponential, stop_after_attempt
# from termcolor import colored

logger = logging.getLogger(__name__)


def completion(messages: list[dict]) -> str:
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
                    detail=f"Failed to get completion response from OpenAI API after {max_retries} retries. Error: {e}",
                )
            else:
                logger.warning(
                    "Failed to get completion response from OpenAI API. Retrying..."
                )
                continue


class Conversation:
    def __init__(self, prompt, num_of_round):
        self.prompt = prompt
        self.num_of_round = num_of_round
        self.messages = []
        self.messages.append({"role": "system", "content": self.prompt})

    def ask(self, question):
        try:
            self.messages.append({"role": "user", "content": question})
            message = completion(self.messages)
        except Exception as e:
            print(e)
            return e

        self.messages.append({"role": "assistant", "content": message})

        if len(self.messages) > self.num_of_round * 2 + 1:
            del self.messages[1:3]
        return message

    def save_messages_to_file(self, filename="temp.txt"):
        with open(filename, 'w', encoding='utf-8') as file:
            for message in self.messages:
                file.write(f"{message['role']}: {message['content']}\n")


def chat_completion_request(messages, functions=None, function_call=None, model="gpt-3.5-turbo-0613"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
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
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e
