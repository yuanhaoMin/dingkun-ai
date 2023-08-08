from util.openai_utils import completion
from util.text_utils import create_prompt_from_template_file


def determine_registration_function_call(text: str) -> str:
    prompt = create_prompt_from_template_file(
        "visitor_register_prompts", "Text to extract from:", text
    )
    messages = [
        {"role": "user", "content": prompt},
    ]
    return completion(messages)
