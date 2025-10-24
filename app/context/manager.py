# context manager
from typing import Dict

class ContextManager:
    _store: Dict[str, dict] = {}

    @classmethod
    def create_context(cls, ctx_id: str, data: dict):
        cls._store[ctx_id] = data

    @classmethod
    def read_context(cls, ctx_id: str) -> dict:
        return cls._store[ctx_id]

    @classmethod
    def update_context(cls, ctx_id: str, data: dict):
        if ctx_id not in cls._store:
            raise KeyError("Context not found")
        cls._store[ctx_id] = data

    @classmethod
    def delete_context(cls, ctx_id: str):
        cls._store.pop(ctx_id, None)

    @classmethod
    def clear_context(cls):
        cls._store.clear()
