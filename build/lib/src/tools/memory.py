from __future__ import annotations

from typing import Any

from src.core.platform import Mem0Client


class MemoryTools:
    """Wrapper for basic Mem0Client operations."""

    def __init__(self, memory: Mem0Client) -> None:
        self.memory = memory

    def search(self, query: str, repository: str = "default") -> Any:
        return self.memory.search(query, {"repository": repository})

    def add(self, data: dict[str, str], repository: str = "default") -> bool:
        payload = {**data, "repository": repository}
        return self.memory.add(payload)
