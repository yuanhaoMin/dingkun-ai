import os
from typing import List, Dict

from app.interpreter.bot_backend import BotBackend
from app.interpreter.functional import chat_completion
from app.interpreter.response_parser import parse_response


def initialization(state_dict: Dict) -> None:
    if not os.path.exists("cache"):
        os.mkdir("cache")
    if state_dict["bot_backend"] is None:
        state_dict["bot_backend"] = BotBackend()
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def get_bot_backend(state_dict: Dict) -> BotBackend:
    return state_dict["bot_backend"]


def switch_to_gpt4(state_dict: Dict, whether_switch: bool) -> None:
    bot_backend = get_bot_backend(state_dict)
    if whether_switch:
        bot_backend.update_gpt_model_choice("GPT-4")
    else:
        bot_backend.update_gpt_model_choice("GPT-3.5")


def add_text(state_dict: Dict, history: List, text: str) -> List:
    bot_backend = get_bot_backend(state_dict)
    bot_backend.add_text_message(user_text=text)

    history = history + [[text, None]]

    return history


def add_file(state_dict: Dict, history: List, file) -> List:
    bot_backend = get_bot_backend(state_dict)

    bot_msg = [f"📁[{file.filename}]", None]
    history.append(bot_msg)

    bot_backend.add_file_message(file=file, bot_msg=bot_msg)

    return history


def undo_upload_file(state_dict: Dict, history: List) -> List:
    bot_backend = get_bot_backend(state_dict)
    bot_msg = bot_backend.revoke_file()

    if bot_msg is None:
        return history

    else:
        assert history[-1] == bot_msg
        del history[-1]
        if bot_backend.revocable_files:
            return history
        else:
            return history


def refresh_file_display(state_dict: Dict) -> List[str]:
    bot_backend = get_bot_backend(state_dict)
    work_dir = bot_backend.jupyter_work_dir
    filenames = os.listdir(work_dir)
    paths = []
    for filename in filenames:
        paths.append(filename)
        # paths.append(os.path.join(work_dir, filename))
    return paths


def restart_bot_backend(state_dict: Dict) -> None:
    bot_backend = get_bot_backend(state_dict)
    bot_backend.restart()


def bot(state_dict: Dict, history: List) -> List:
    bot_backend = get_bot_backend(state_dict)
    while bot_backend.finish_reason in ("new_input", "function_call"):
        if history[-1][0] is None:
            history.append([None, ""])
        else:
            history[-1][1] = ""

        response = chat_completion(bot_backend=bot_backend)
        for chunk in response:
            history, weather_exit = parse_response(
                chunk=chunk, history=history, bot_backend=bot_backend
            )
            yield history
            if weather_exit:
                exit(-1)

    yield history