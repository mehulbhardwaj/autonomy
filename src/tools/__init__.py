"""Core tool registry and implementations."""

from .github import GitHubTools
from .registry import ToolRegistry
from .slack import SlackTools

__all__ = ["ToolRegistry", "GitHubTools", "SlackTools", "MemoryTools"]


def __getattr__(name):
    if name == "MemoryTools":  # pragma: no cover - lazy import
        from .memory import MemoryTools

        return MemoryTools
    raise AttributeError(name)
