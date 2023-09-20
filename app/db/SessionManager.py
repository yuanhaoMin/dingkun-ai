import threading
from copy import deepcopy
from datetime import datetime, timedelta
from collections import OrderedDict
import logging


class SessionManager:
    def __init__(self, max_session_count=1000):
        self._store = OrderedDict()
        self.MAX_SESSION_COUNT = max_session_count

        # 初始化日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def add_or_update_session(self, session_id, conversation):
        if session_id not in self._store:
            self._store[session_id] = {
                "conversation": conversation,
                "timestamp": datetime.now(),
                "previous_response": None
            }
        else:
            self._store[session_id]["conversation"] = conversation
            self._store[session_id]["timestamp"] = datetime.now()
        self.logger.debug(f"Updated session {session_id} with conversation {conversation}")

    def get_session(self, session_id):
        return self._store.get(session_id, {})

    def prune_sessions(self):
        while len(self._store) > self.MAX_SESSION_COUNT:
            self._store.popitem(last=False)

    def remove_expired_sessions(self):
        expiration_time = datetime.now() - timedelta(minutes=15)
        expired_keys = [key for key, value in self._store.items() if
                        value.get('timestamp') and value.get('timestamp') < expiration_time]

        for key in expired_keys:
            self._store.pop(key)
