"""GitHub integration utilities."""

from .issue_manager import IssueManager
from .pat_scopes import (
    REQUIRED_GITHUB_SCOPES,
    get_github_token_scopes,
    validate_github_token_scopes,
)

__all__ = [
    "IssueManager",
    "REQUIRED_GITHUB_SCOPES",
    "get_github_token_scopes",
    "validate_github_token_scopes",
]
