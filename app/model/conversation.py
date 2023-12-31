from app.util.openai_util import chat_completion_no_functions


class Conversation:
    def __init__(self, num_of_rounds: int, system_message: str = None):
        self.num_of_rounds = num_of_rounds
        self.messages = []
        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def ask(self, question):
        self.prune_messages()
        self.messages.append({"role": "user", "content": question})
        ai_response = chat_completion_no_functions(self.messages)
        self.messages.append({"role": "assistant", "content": ai_response})
        return ai_response

    def prune_messages(self):
        assert self.messages[0]["role"] == "system"
        if len(self.messages) > self.num_of_rounds * 2:
            del self.messages[1:3]
