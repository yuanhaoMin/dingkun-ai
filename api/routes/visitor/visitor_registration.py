from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

import openai
import os

from utils.text_tools import insert_text

openai.api_key ='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'
COMPLETION_MODEL = "text-davinci-003"

message='我是小王，我的手机号是12345678910'

def get_response(prompt, temperature = 1.0):
    completions = openai.Completion.create (
        engine=COMPLETION_MODEL,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=temperature,
    )
    message = completions.choices[0].text
    return message

print(get_response(insert_text("visitor_regist_prompts", "Text to extract from:", message)))

