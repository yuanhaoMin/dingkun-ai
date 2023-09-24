import logging
from app.model.conversation import Conversation
from datetime import datetime, timedelta
from collections import OrderedDict
from typing import OrderedDict as TypedOrderedDict

SESSION_EXPIRATION_TIME_MINUTES = 15  # making this a constant


class Session:
    def __init__(self, conversation):
        self.conversation = conversation
        self.timestamp = datetime.now()


class SessionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SessionManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, max_session_count: int = 100):
        # Check if we've already initialized this instance
        if not hasattr(self, "_store"):
            self._store: TypedOrderedDict[str, Session] = OrderedDict()
            self.MAX_SESSION_COUNT = max_session_count
            self._initialize_logger()

    def _initialize_logger(self):
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)

    def _prune_sessions_to_limit(self):
        over_limit = len(self._store) - self.MAX_SESSION_COUNT
        if over_limit > 0:
            self.logger.debug("Pruning sessions to meet the max limit.")
            for _ in range(over_limit):
                self._store.popitem(last=False)

    def _remove_expired_sessions(self) -> None:
        expiration_time = datetime.now() - timedelta(
            minutes=SESSION_EXPIRATION_TIME_MINUTES
        )
        expired_keys = [
            key
            for key, session in self._store.items()
            if session.timestamp < expiration_time
        ]
        if expired_keys:
            self.logger.debug(f"Removing {len(expired_keys)} expired session(s).")
            for key in expired_keys:
                self._store.pop(key)

    def remove_session(self, session_id: str) -> None:
        self._store.pop(session_id)

    def add_or_update_session_conversation(
        self, session_id: str, conversation: Conversation
    ) -> None:
        self._prune_sessions_to_limit()
        self._remove_expired_sessions()
        self._store[session_id] = Session(conversation)
        self.logger.debug(f"Updated session {session_id}")

    def get_session_conversation(self, session_id: str) -> Conversation:
        self._remove_expired_sessions()
        session = self._store.get(session_id)
        return session.conversation if session else None

    def retrieve_or_create_session_conversation(
        self, session_id: str, num_of_rounds: int = 5, system_message: str = None
    ) -> Conversation:
        conversation = self.get_session_conversation(session_id)
        if not conversation:
            conversation = Conversation(
                num_of_rounds=num_of_rounds, system_message=system_message
            )
            self.add_or_update_session_conversation(session_id, conversation)
        return conversation
