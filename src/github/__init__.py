"""GitHub integration utilities."""

from .board_manager import BoardManager, GraphQLClient
from .device_flow import DeviceFlowResponse, GitHubDeviceFlow, OAuthError
from .issue_manager import IssueManager
from .pat_scopes import (
    REQUIRED_GITHUB_SCOPES,
    get_github_token_scopes,
    validate_github_token_scopes,
)

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
]
