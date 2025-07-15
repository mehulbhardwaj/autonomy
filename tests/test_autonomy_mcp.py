"""
Basic tests for Autonomy MCP package.
"""

import os
import tempfile
from unittest.mock import patch

import pytest

# Import the main classes
from src import PlanManager, WorkflowConfig, WorkflowManager
from src.core.agents import BaseAgent, PMAgent, QAAgent, SDEAgent
from src.github.issue_manager import IssueManager
from src.planning.plan_manager import TaskPlan


class TestWorkflowConfig:
    """Test WorkflowConfig functionality."""

    def test_default_config(self):
        """Test default configuration values."""
        config = WorkflowConfig()

        assert config.max_file_lines == 300
        assert config.max_function_lines == 40
        assert config.test_coverage_target == 0.75
        assert config.autonomy_level == "supervised"

    def test_custom_config(self):
        """Test custom configuration values."""
        config = WorkflowConfig(
            max_file_lines=500, test_coverage_target=0.9, autonomy_level="autonomous"
        )

        assert config.max_file_lines == 500
        assert config.test_coverage_target == 0.9
        assert config.autonomy_level == "autonomous"


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


class TestPlanManager:
    """Test PlanManager functionality."""

    def test_plan_manager_init(self):
        """Test PlanManager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = PlanManager(temp_dir)
            assert manager.workspace_path == temp_dir

    def test_create_basic_template(self):
        """Test basic plan template creation."""
        manager = PlanManager()
        plan = manager.create_plan_template("basic")

        assert isinstance(plan, TaskPlan)
        assert plan.name == "Basic Project Plan"
        assert len(plan.milestones) == 4
        assert len(plan.issues) == 3

    def test_create_api_template(self):
        """Test API plan template creation."""
        manager = PlanManager()
        plan = manager.create_plan_template("api")

        assert isinstance(plan, TaskPlan)
        assert plan.name == "API Project Plan"
        assert len(plan.milestones) == 4
        assert len(plan.issues) == 3

    def test_save_and_load_plan(self):
        """Test saving and loading plans."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = PlanManager(temp_dir)
            plan = manager.create_plan_template("basic")

            # Save plan
            plan_file = "test_plan.json"
            manager.save_plan(plan, plan_file)

            # Verify file exists
            plan_path = os.path.join(temp_dir, plan_file)
            assert os.path.exists(plan_path)

            # Load plan
            loaded_plan = manager.load_plan(plan_file)

            assert loaded_plan.name == plan.name
            assert len(loaded_plan.milestones) == len(plan.milestones)
            assert len(loaded_plan.issues) == len(plan.issues)

    def test_validate_plan(self):
        """Test plan validation."""
        manager = PlanManager()

        # Valid plan
        valid_plan = manager.create_plan_template("basic")
        errors = manager.validate_plan(valid_plan)
        assert len(errors) == 0

        # Invalid plan - missing name
        invalid_plan = TaskPlan(name="", description="Test", milestones=[], issues=[])
        errors = manager.validate_plan(invalid_plan)
        assert len(errors) > 0
        assert any("name is required" in error for error in errors)


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
            PlanManager,
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
        _ = PlanManager()
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
