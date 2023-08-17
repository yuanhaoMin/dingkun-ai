import logging
from app.config.api_config import get_openai_key
from fastapi import HTTPException
from openai import ChatCompletion

logger = logging.getLogger(__name__)


def completion(
    messages: list[dict], model="gpt-3.5-turbo", temperature=0, stream=True
) -> str:
    retry_count = 0
    max_retries = 2

    while True:
        try:
            response = ChatCompletion.create(
                api_key=get_openai_key(),
                model=model,
                messages=messages,
                request_timeout=10,
                temperature=temperature,  # 这是模型输出的随机度
                stream=stream,
            )

            if stream:
                contents = []
                for stream_response in response:
                    delta = stream_response["choices"][0]["delta"]
                    if hasattr(delta, "content"):
                        contents.append(delta.content)
                return "".join(contents)
            else:
                return response.choices[0].message["content"]
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
