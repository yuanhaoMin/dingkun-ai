from app.constant.conversation.companion_register_conversation_data import companion_register_messages, \
    companion_register_messages_old
from app.constant.conversation.visitor_register_conversation_data import (
    visitor_register_messages, visitor_register_messages_old,
)


class HistoryBasedTrainingManager:
    @staticmethod
    def get_visitor_register_messages():
        return visitor_register_messages

    @staticmethod
    def get_visitor_companion_register_messages():
        return companion_register_messages

    @staticmethod
    def get_visitor_register_messages_old():
        return visitor_register_messages_old

    @staticmethod
    def get_visitor_companion_register_messages_old():
        return companion_register_messages_old
