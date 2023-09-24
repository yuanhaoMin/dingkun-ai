from app.util.openai_util import chat_completion_no_functions


class Conversation:
    def __init__(self, num_of_round: int, system_message: str = None):
        self.num_of_round = num_of_round
        self.messages = []
        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def ask(self, question):
        if len(self.messages) > self.num_of_round * 2:
            del self.messages[1:3]
        self.messages.append({"role": "user", "content": question})
        ai_response = chat_completion_no_functions(self.messages)
        self.messages.append({"role": "assistant", "content": ai_response})
        return ai_response

    def save_messages_to_file(self, filename="temp.txt"):
        with open(filename, "w", encoding="utf-8") as file:
            for message in self.messages:
                file.write(f"{message['role']}: {message['content']}\n")
