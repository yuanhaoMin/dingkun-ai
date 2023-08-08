import openai
import json
from fastapi import FastAPI, HTTPException, Depends, Request
from typing import Optional

from starlette.middleware import Middleware

from starlette.middleware.cors import CORSMiddleware

from utils.text_tools import insert_text


def visitor_registration(details):
    """Function to register a visitor with the provided details."""
    # print("Visitor Registration Details:")
    # print(json.dumps(details, indent=4,ensure_ascii=False))
    return details

text = """
我是深圳电力的经理张三，我手机号12345678910。我要见市场部的王总。时间10点。目的是谈ai的项目。
"""
# message=insert_text("visitor_regist_prompts","Text to extract from:",text)

def extract_and_register(text):
    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": f"Extract details from this text: {text}"}]
    functions = [
        {
            "name": "visitor_registration",
            "description": "Function to register a visitor with the provided details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_details": {
                        "type": "object",
                        "properties": {
                            "phone": {"type": "string"},
                            "name": {"type": "string"},
                            "id_number": {"type": "string"},
                            "license_plate": {"type": "string"}
                        },
                        "required": ["phone", "name", "id_number", "license_plate"]
                    },
                    "visit_details": {
                        "type": "object",
                        "properties": {
                            "visit_unit": {"type": "string"},
                            "visit_reason": {"type": "string"}
                        },
                        "required": ["visit_unit", "visit_reason"]
                    },
                    "reception_details": {
                        "type": "object",
                        "properties": {
                            "visited_department": {"type": "string"},
                            "visited_person": {"type": "string"}
                        },
                        "required": ["visited_department", "visited_person"]
                    },
                    "appointment_details": {
                        "type": "object",
                        "properties": {
                            "visit_time": {"type": "string"}
                        },
                        "required": ["visit_time"]
                    }
                },
                "required": ["contact_details", "visit_details", "reception_details", "appointment_details"]
            }
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        temperature=0,
        functions=functions,
        function_call="auto"
    )

    # response_message = response["choices"][0]["message"]
    #
    # # Check if GPT wanted to call a function
    # if response_message.get("function_call"):
    #     function_name = response_message["function_call"]["name"]
    #     function_args = json.loads(response_message["function_call"]["arguments"])
    #     if function_name == "visitor_registration":
    #         visitor_registration(function_args)
    response_message = response["choices"][0]["message"]

    if "function_call" in response_message:
        function_name = response_message["function_call"]["name"]
        function_args = response_message["function_call"]["arguments"]
        if function_name == "visitor_registration":
            return visitor_registration(function_args)
    else:
        return {"error": "Function call not found in GPT response"}


extract_and_register(text)


