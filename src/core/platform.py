from __future__ import annotations

from typing import Type

from ..llm.openrouter import ModelSelector, OpenRouterClient
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


class GitHubTools:  # pragma: no cover - simple stub
    def get_issue(self, issue_number: int) -> dict:
        return {}


class SlackTools:  # pragma: no cover - simple stub
    def post_message(self, channel: str, text: str) -> bool:
        return True


class AutonomyPlatform:
    """Shared foundation for all workflows."""

    def __init__(
        self, api_key: str | None = None, model_selector: ModelSelector | None = None
    ):
        self.memory = Mem0Client()
        self.llm = OpenRouterClient(api_key=api_key)
        self.model_selector = model_selector or ModelSelector()
        self.github = GitHubTools()
        self.slack = SlackTools()

    def create_workflow(self, workflow_class: Type[BaseWorkflow]) -> BaseWorkflow:
        kwargs = {
            "memory": self.memory,
            "llm": self.llm,
            "github": self.github,
            "slack": self.slack,
        }
        if "model_selector" in workflow_class.__init__.__code__.co_varnames:
            kwargs["model_selector"] = self.model_selector
        return workflow_class(**kwargs)
