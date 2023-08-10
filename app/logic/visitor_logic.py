from app.logic.conversation_training_logic import HistoryBasedTrainingManager
from app.util.openai_util import completion
from app.util.text_util import create_prompt_from_template_file
from datetime import datetime


current_date = datetime.now().strftime("%Y-%m-%d")
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today = datetime.today().date()
day_of_week = days[today.weekday()]


def determine_registration_function_call(text: str) -> str:
    replacements = {"current_date:": current_date,
                    "day_of_week:": day_of_week}
    prompt = create_prompt_from_template_file(
        filename="visitor_register_prompts", replacements=replacements
    )
    print(prompt)
    messages = [{"role": "system", "content": prompt}]
    messages.extend(HistoryBasedTrainingManager.get_visitor_register_messages())
    messages.append({"role": "user", "content": text})
    return completion(messages)

