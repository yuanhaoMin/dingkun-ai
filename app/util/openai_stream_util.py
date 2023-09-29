import logging

from app.config.environment import get_openai_key
from app.model.conversation import Conversation
from app.model.pydantic_schema.event_data_schemas import EventData
from fastapi import HTTPException
from openai import ChatCompletion

logger = logging.getLogger(__name__)


def chat_completion_stream_no_functions(
    conversation: Conversation, messages: list[dict], user_message_to_save: str
) -> str:
    contents = []
    event_data = EventData()
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
                    event_data.content = delta.content
                    yield "data: %s\n\n" % event_data.model_dump_json()
                if finish_reason == "stop":
                    full_response_text = "".join(contents)
                    conversation.extend_and_prune(
                        [
                            {"role": "user", "content": user_message_to_save},
                            {"role": "assistant", "content": full_response_text},
                        ]
                    )
                    event_data.hasEnd = True
                    yield "data: %s\n\n" % event_data.model_dump_json()
            break
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
