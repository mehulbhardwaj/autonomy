from __future__ import annotations

from typing import Type

from .workflow import BaseWorkflow


class Mem0Client:  # pragma: no cover - simple stub
    """Extremely small in-memory store used for tests."""

    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def search(self, query: str) -> str:
        return self.store.get(query, "")

    def add(self, data: dict[str, str]) -> bool:
        self.store.update(data)
        return True


class OpenRouterClient:  # pragma: no cover - simple stub
    """Return simple echo responses for tests."""

    def complete(self, messages):
        if not messages:
            return ""
        content = messages[-1].get("content", "")
        return f"LLM:{content}"


class GitHubTools:  # pragma: no cover - simple stub
    def get_issue(self, issue_number: int) -> dict:
        return {}


class SlackTools:  # pragma: no cover - simple stub
    def post_message(self, channel: str, text: str) -> bool:
        return True


class AutonomyPlatform:
    """Shared foundation for all workflows."""

    def __init__(self):
        self.memory = Mem0Client()
        self.llm = OpenRouterClient()
        self.github = GitHubTools()
        self.slack = SlackTools()

    def create_workflow(self, workflow_class: Type[BaseWorkflow]) -> BaseWorkflow:
        return workflow_class(
            memory=self.memory,
            llm=self.llm,
            github=self.github,
            slack=self.slack,
        )
