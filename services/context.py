class ContextService:
    def __init__(self):
        self._contexts: dict[int, dict] = {}  # user_id -> context

    def set(self, user_id: int, key: str, value):
        if user_id not in self._contexts:
            self._contexts[user_id] = {}
        self._contexts[user_id][key] = value

    def get(self, user_id: int, key: str, default=None):
        return self._contexts.get(user_id, {}).get(key, default)

    def get_all(self, user_id: int) -> dict:
        return self._contexts.get(user_id, {})

    def clear(self, user_id: int):
        self._contexts.pop(user_id, None)

    def clear_key(self, user_id: int, key: str):
        self._contexts[user_id].pop(key, None)

    def clear_all(self):
        self._contexts.clear()


context_service = ContextService()
