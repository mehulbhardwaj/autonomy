"""Custom error types and handling utilities."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable


class AutonomyError(Exception):
    """Base exception with optional suggestion and error code."""

    def __init__(
        self, message: str, suggestion: str | None = None, error_code: str | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code


class GitHubAPIError(AutonomyError):
    """GitHub API specific errors."""


class ConfigurationError(AutonomyError):
    """Configuration related errors."""


def handle_errors(func: Callable[..., int]) -> Callable[..., int]:
    """Decorator to display helpful messages for common errors."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> int:
        try:
            return func(*args, **kwargs)
        except GitHubAPIError as e:
            print(f"❌ GitHub API Error: {e.message}")
            if e.suggestion:
                print(f"💡 Suggestion: {e.suggestion}")
            return 1
        except AutonomyError as e:
            print(f"❌ {e.message}")
            if e.suggestion:
                print(f"💡 Suggestion: {e.suggestion}")
            return 1
        except Exception as e:  # pragma: no cover - fallback
            print(f"❌ Unexpected error: {e}")
            print(
                "🐛 Please report this at: https://github.com/mehulbhardwaj/autonomy/issues"
            )
            return 1

    return wrapper
