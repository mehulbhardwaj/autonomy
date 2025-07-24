"""
Autonomy - Enable human-AI collaboration in software development.

Utilities for coordinating AI agents and human teammates through a
Generate-Verify workflow. Inspired by "Writing Software in English" by
Mehul Bhardwaj.
"""

from .api import create_app
from .core.agents import BaseAgent, PMAgent, QAAgent, SDEAgent
from .core.config import WorkflowConfig
from .core.platform import AutonomyPlatform, BaseWorkflow
from .core.secret_vault import SecretVault
from .core.workflow_manager import WorkflowManager
from .github import (
    REQUIRED_GITHUB_SCOPES,
    BoardManager,
    GraphQLClient,
    IssueManager,
    get_github_token_scopes,
    validate_github_token_scopes,
)
from .github.device_flow import DeviceFlowResponse, GitHubDeviceFlow, OAuthError
from .github.token_storage import (
    SecureTokenStorage,
    refresh_token_if_needed,
    validate_token,
)
from .metrics import MetricsCollector, MetricsStorage
from .slack import (
    BacklogDoctorNotifier,
    MetricsDashboard,
    NotificationScheduler,
    NotificationTemplates,
    SlackOAuth,
    SlashCommandHandler,
    SystemNotifier,
    get_slack_auth_info,
    verify_slack_signature,
)
from .tasks.backlog_doctor import BacklogDoctor
from .tasks.task_manager import TaskManager
from .tools import GitHubTools, MemoryTools, SlackTools, ToolRegistry

__version__ = "0.1.1"
__author__ = "Mehul Bhardwaj"
__email__ = "mehul@example.com"
__license__ = "GPL-3.0-or-later"

from .utils.distribution import check_for_updates, verify_installation

__all__ = [
    # Core classes
    "WorkflowManager",
    "WorkflowConfig",
    "AutonomyPlatform",
    "BaseWorkflow",
    # Agents
    "BaseAgent",
    "PMAgent",
    "SDEAgent",
    "QAAgent",
    # GitHub integration
    "IssueManager",
    "BoardManager",
    "GraphQLClient",
    "REQUIRED_GITHUB_SCOPES",
    "get_github_token_scopes",
    "validate_github_token_scopes",
    "GitHubDeviceFlow",
    "OAuthError",
    "DeviceFlowResponse",
    "SecureTokenStorage",
    "validate_token",
    "refresh_token_if_needed",
    # Planning
    "TaskManager",
    "BacklogDoctor",
    "SecretVault",
    # Version info
    "__version__",
    "get_slack_auth_info",
    "SlackOAuth",
    "SlashCommandHandler",
    "verify_slack_signature",
    "BacklogDoctorNotifier",
    "MetricsDashboard",
    "SystemNotifier",
    "NotificationTemplates",
    "NotificationScheduler",
    "ToolRegistry",
    "GitHubTools",
    "SlackTools",
    "MemoryTools",
    "MetricsCollector",
    "MetricsStorage",
    "verify_installation",
    "check_for_updates",
    "create_app",
]


# Convenience imports for common usage patterns
def create_workflow_manager(
    github_token: str, owner: str, repo: str, workspace_path: str = ".", **config_kwargs
) -> WorkflowManager:
    """
    Convenience function to create a WorkflowManager with configuration.

    Args:
        github_token: GitHub personal access token
        owner: Repository owner
        repo: Repository name
        workspace_path: Local workspace path
        **config_kwargs: Additional configuration options

    Returns:
        Configured WorkflowManager instance

    Example:
        >>> manager = create_workflow_manager(
        ...     github_token="ghp_...",
        ...     owner="myorg",
        ...     repo="myproject",
        ...     max_file_lines=300,
        ...     test_coverage_target=0.8
        ... )
    """
    config = WorkflowConfig(**config_kwargs)
    return WorkflowManager(
        github_token=github_token,
        owner=owner,
        repo=repo,
        workspace_path=workspace_path,
        config=config,
    )


def quick_setup(
    github_token: str, owner: str, repo: str, template: str = "library"
) -> WorkflowManager:
    """
    Quick setup for new repositories with sensible defaults.

    Args:
        github_token: GitHub personal access token
        owner: Repository owner
        repo: Repository name
        template: Project template (web, api, cli, library)

    Returns:
        Configured and initialized WorkflowManager

    Example:
        >>> manager = quick_setup(
        ...     github_token="ghp_...",
        ...     owner="myorg",
        ...     repo="myproject",
        ...     template="api"
        ... )
        >>> manager.setup_repository()
    """
    manager = create_workflow_manager(
        github_token=github_token,
        owner=owner,
        repo=repo,
        autonomy_level="supervised",
        test_coverage_target=0.75,
    )

    # Auto-setup repository
    manager.setup_repository()

    return manager
