from datetime import datetime, timedelta
from collections import OrderedDict


class SessionManager:
    def __init__(self, max_session_count=1000):
        self._store = OrderedDict()
        self.MAX_SESSION_COUNT = max_session_count

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

    def get_session(self, session_id):
        return self._store.get(session_id, {})

    def prune_sessions(self):
        while len(self._store) > self.MAX_SESSION_COUNT:
            self._store.popitem(last=False)

    def remove_expired_sessions(self):
        expiration_time = datetime.now() - timedelta(minutes=5)
        expired_keys = [key for key, value in self._store.items() if
                        value.get('timestamp') and value.get('timestamp') < expiration_time]

        for key in expired_keys:
            self._store.pop(key)
