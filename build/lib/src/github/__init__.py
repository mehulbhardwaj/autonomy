"""GitHub integration utilities."""

from .board_manager import BoardManager, GraphQLClient
from .client import ResilientGitHubClient
from .device_flow import DeviceFlowResponse, GitHubDeviceFlow, OAuthError
from .issue_manager import IssueManager
from .pat_scopes import (
    REQUIRED_GITHUB_SCOPES,
    get_github_token_scopes,
    validate_github_token_scopes,
)
from .token_storage import SecureTokenStorage, refresh_token_if_needed, validate_token

__all__ = [
    "IssueManager",
    "BoardManager",
    "GraphQLClient",
    "REQUIRED_GITHUB_SCOPES",
    "get_github_token_scopes",
    "validate_github_token_scopes",
    "GitHubDeviceFlow",
    "DeviceFlowResponse",
    "OAuthError",
    "SecureTokenStorage",
    "validate_token",
    "refresh_token_if_needed",
    "ResilientGitHubClient",
]
