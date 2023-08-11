from app.constant.conversation.companion_register_conversation_data import companion_register_messages
from app.constant.conversation.visitor_register_conversation_data import (
    visitor_register_messages,
)


class HistoryBasedTrainingManager:
    @staticmethod
    def get_visitor_register_messages():
        return visitor_register_messages

    @staticmethod
    def get_visitor_companion_register_messages():
        return companion_register_messages
