"""
Autonomy MCP - Enable human-AI collaboration in software development

A utility package for implementing the Generate-Verify loop workflow with AI agents.
Supports PM-agent, SDE-agent, and QA-agent roles with human oversight.

Inspired by "Writing Software in English" by Mehul Bhardwaj.
https://mehulbhardwaj.substack.com/p/building-software-in-english
"""

from .core.agents import BaseAgent, PMAgent, QAAgent, SDEAgent
from .core.config import WorkflowConfig
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
from .planning.plan_manager import PlanManager
from .slack import get_slack_auth_info
from .tasks.task_manager import TaskManager

__version__ = "0.1.0"
__author__ = "Mehul Bhardwaj"
__email__ = "mehul@example.com"
__license__ = "MIT"

__all__ = [
    # Core classes
    "WorkflowManager",
    "WorkflowConfig",
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
    # Planning
    "PlanManager",
    "TaskManager",
    "SecretVault",
    # Version info
    "__version__",
    "get_slack_auth_info",
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
