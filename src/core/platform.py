from __future__ import annotations

from collections import OrderedDict
from typing import Type

from ..llm.openrouter import ModelSelector, OpenRouterClient
from .workflow import BaseWorkflow


class Mem0Client:  # pragma: no cover - simple stub
    """Minimal repository-scoped memory store for tests."""

    def __init__(self, max_entries: int = 50) -> None:
        self.max_entries = max_entries
        # Each repository gets its own ordered store of key -> value pairs
        self.store: dict[str, OrderedDict[str, str]] = {}

    def _get_repo_store(self, repo: str) -> OrderedDict[str, str]:
        if repo not in self.store:
            self.store[repo] = OrderedDict()
        return self.store[repo]

    def search(self, query: str, filter_metadata: dict | None = None) -> str:
        """Return stored value filtered by repository."""
        repo = filter_metadata.get("repository") if filter_metadata else "default"
        return self.store.get(repo, {}).get(query, "")

    def add(self, data: dict[str, str]) -> bool:
        """Add data to repository-specific store with cleanup."""
        repository = data.pop("repository", "default")
        repo_store = self._get_repo_store(repository)
        for key, value in data.items():
            if len(repo_store) >= self.max_entries:
                repo_store.popitem(last=False)
            repo_store[key] = value
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
