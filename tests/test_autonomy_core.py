"""
Basic tests for the Autonomy core package.
"""

import os
import tempfile
from unittest.mock import patch

import pytest

# Import the main classes
from src import WorkflowConfig, WorkflowManager
from src.core.agents import BaseAgent, PMAgent, QAAgent, SDEAgent
from src.github.issue_manager import IssueManager


class TestWorkflowConfig:
    """Test WorkflowConfig functionality."""

    def test_default_config(self):
        """Test default configuration values."""
        config = WorkflowConfig()

        assert config.max_file_lines == 300
        assert config.max_function_lines == 40
        assert config.test_coverage_target == 0.75
        assert config.autonomy_level == "supervised"
        assert config.board_cache_path.endswith("field_cache.json")

    def test_custom_config(self):
        """Test custom configuration values."""
        config = WorkflowConfig(
            max_file_lines=500, test_coverage_target=0.9, autonomy_level="autonomous"
        )

        assert config.max_file_lines == 500
        assert config.test_coverage_target == 0.9
        assert config.autonomy_level == "autonomous"

    def test_custom_board_cache(self):
        """Custom board cache path is stored."""
        config = WorkflowConfig(board_cache_path="/tmp/cache.json")
        assert config.board_cache_path == "/tmp/cache.json"


class TestAgents:
    """Test agent functionality."""

    def test_base_agent(self):
        """Test BaseAgent initialization."""
        config = WorkflowConfig()
        agent = BaseAgent(config)

        assert agent.config == config
        assert agent.role == "base"

    def test_pm_agent(self):
        """Test PMAgent initialization."""
        config = WorkflowConfig()
        agent = PMAgent(config)

        assert agent.role == "pm"
        assert "product manager" in agent.system_prompt.lower()

    def test_sde_agent(self):
        """Test SDEAgent initialization."""
        config = WorkflowConfig()
        agent = SDEAgent(config)

        assert agent.role == "sde"
        assert "software development" in agent.system_prompt.lower()

    def test_qa_agent(self):
        """Test QAAgent initialization."""
        config = WorkflowConfig()
        agent = QAAgent(config)

        assert agent.role == "qa"
        assert "quality assurance" in agent.system_prompt.lower()


class TestIssueManager:
    """Test IssueManager functionality."""

    @patch("requests.get")
    @patch("requests.post")
    def test_issue_manager_init(self, mock_post, mock_get):
        """Test IssueManager initialization."""
        # Mock GitHub API responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []

        manager = IssueManager("fake_token", "owner", "repo")

        assert manager.github_token == "fake_token"
        assert manager.owner == "owner"
        assert manager.repo == "repo"

    @patch("requests.get")
    def test_list_issues(self, mock_get):
        """Test listing issues."""
        # Mock GitHub API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"number": 1, "title": "Test Issue", "state": "open"}
        ]

        manager = IssueManager("fake_token", "owner", "repo")
        issues = manager.list_issues()

        assert len(issues) == 1
        assert issues[0]["title"] == "Test Issue"


class TestWorkflowManager:
    """Test WorkflowManager functionality."""

    @patch("src.github.issue_manager.IssueManager")
    def test_workflow_manager_init(self, mock_issue_manager):
        """Test WorkflowManager initialization."""
        config = WorkflowConfig()
        manager = WorkflowManager(
            github_token="fake_token", owner="owner", repo="repo", config=config
        )

        assert manager.github_token == "fake_token"
        assert manager.owner == "owner"
        assert manager.repo == "repo"
        assert manager.config == config

    @patch("src.github.issue_manager.IssueManager")
    def test_get_agents(self, mock_issue_manager):
        """Test agent creation."""
        config = WorkflowConfig()
        manager = WorkflowManager(
            github_token="fake_token", owner="owner", repo="repo", config=config
        )

        pm_agent = manager.get_pm_agent()
        sde_agent = manager.get_sde_agent()
        qa_agent = manager.get_qa_agent()

        assert isinstance(pm_agent, PMAgent)
        assert isinstance(sde_agent, SDEAgent)
        assert isinstance(qa_agent, QAAgent)


class TestIntegration:
    """Integration tests."""

    def test_package_imports(self):
        """Test that all main classes can be imported."""
        from src import (
            BaseAgent,
            IssueManager,
            PMAgent,
            QAAgent,
            SDEAgent,
            WorkflowConfig,
            WorkflowManager,
        )

        # Basic instantiation test
        config = WorkflowConfig()
        assert isinstance(config, WorkflowConfig)

        # Instantiate classes to ensure they can be imported correctly
        _ = IssueManager("token", "owner", "repo")
        _ = WorkflowManager(
            github_token="token", owner="owner", repo="repo", config=config
        )

        agents = [BaseAgent(config), PMAgent(config), SDEAgent(config), QAAgent(config)]

        for agent in agents:
            assert hasattr(agent, "config")
            assert hasattr(agent, "role")

    def test_convenience_functions(self):
        """Test convenience functions."""
        from src import create_workflow_manager

        with patch("src.github.issue_manager.IssueManager"):
            manager = create_workflow_manager(
                github_token="fake_token",
                owner="owner",
                repo="repo",
                max_file_lines=500,
            )

            assert manager.config.max_file_lines == 500


if __name__ == "__main__":
    pytest.main([__file__])
