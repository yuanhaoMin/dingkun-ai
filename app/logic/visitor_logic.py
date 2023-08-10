from app.logic.conversation_training_logic import HistoryBasedTrainingManager
from app.util.openai_util import completion
from app.util.text_util import create_prompt_from_template_file
from datetime import datetime


current_time = datetime.now().strftime("%Y-%m-%d")


def determine_registration_function_call(text: str) -> str:
    replacements = {"current_time:": current_time}
    prompt = create_prompt_from_template_file(
        filename="visitor_register_prompts", replacements=replacements
    )
    messages = [{"role": "system", "content": prompt}]
    messages.extend(HistoryBasedTrainingManager.get_visitor_register_messages())
    messages.append({"role": "user", "content": text})
    return completion(messages)
