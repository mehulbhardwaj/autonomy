"""
Basic tests for GitHub Workflow Manager
"""

import pytest
import os
from unittest.mock import Mock, patch
from src import WorkflowManager, WorkflowConfig
from src.github.issue_manager import IssueManager


def test_workflow_config():
    """Test workflow configuration"""
    config = WorkflowConfig()
    
    # Test default values
    assert config.max_file_lines == 300
    assert config.max_function_lines == 40
    assert config.test_coverage_target == 0.75
    assert config.autonomy_level == "supervised"
    
    # Test validation
    assert config.validate() == True


def test_workflow_config_from_dict():
    """Test creating config from dictionary"""
    config_dict = {
        "max_file_lines": 200,
        "test_coverage_target": 0.8,
        "pm_agent_model": "gpt-3.5-turbo"
    }
    
    config = WorkflowConfig.from_dict(config_dict)
    assert config.max_file_lines == 200
    assert config.test_coverage_target == 0.8
    assert config.pm_agent_model == "gpt-3.5-turbo"


def test_workflow_manager_init():
    """Test workflow manager initialization"""
    config = WorkflowConfig()
    
    manager = WorkflowManager(
        github_token="test_token",
        owner="test_owner",
        repo="test_repo",
        workspace_path="./test",
        config=config
    )
    
    assert manager.github_token == "test_token"
    assert manager.owner == "test_owner"
    assert manager.repo == "test_repo"
    assert manager.config == config
    assert isinstance(manager.issue_manager, IssueManager)


@patch('src.github.issue_manager.IssueManager')
def test_setup_repository(mock_issue_manager):
    """Test repository setup"""
    mock_issue_manager_instance = Mock()
    mock_issue_manager.return_value = mock_issue_manager_instance
    
    config = WorkflowConfig()
    manager = WorkflowManager(
        github_token="test_token",
        owner="test_owner", 
        repo="test_repo",
        config=config
    )
    
    # Mock the setup_repository method
    mock_issue_manager_instance.setup_repository.return_value = True
    
    # Test setup (this would create files in real scenario)
    manager.setup_repository()
    
    # Verify issue manager setup was called
    mock_issue_manager_instance.setup_repository.assert_called_once()


def test_extract_agent_role():
    """Test agent role extraction from labels"""
    config = WorkflowConfig()
    manager = WorkflowManager(
        github_token="test_token",
        owner="test_owner",
        repo="test_repo", 
        config=config
    )
    
    # Test PM agent role
    labels = ["feature", "pm-agent", "priority-high"]
    role = manager._extract_agent_role(labels)
    assert role == "pm-agent"
    
    # Test SDE agent role
    labels = ["task", "sde-agent", "in-development"]
    role = manager._extract_agent_role(labels)
    assert role == "sde-agent"
    
    # Test QA agent role
    labels = ["bug", "qa-agent", "needs-testing"]
    role = manager._extract_agent_role(labels)
    assert role == "qa-agent"
    
    # Test unknown role
    labels = ["feature", "priority-low"]
    role = manager._extract_agent_role(labels)
    assert role == "unknown"


def test_extract_current_phase():
    """Test current phase extraction from labels"""
    config = WorkflowConfig()
    manager = WorkflowManager(
        github_token="test_token",
        owner="test_owner",
        repo="test_repo",
        config=config
    )
    
    # Test needs-requirements phase
    labels = ["feature", "needs-requirements", "pm-agent"]
    phase = manager._extract_current_phase(labels)
    assert phase == "needs-requirements"
    
    # Test in-development phase
    labels = ["task", "in-development", "sde-agent"]
    phase = manager._extract_current_phase(labels)
    assert phase == "in-development"
    
    # Test needs-testing phase
    labels = ["feature", "needs-testing", "qa-agent"]
    phase = manager._extract_current_phase(labels)
    assert phase == "needs-testing"
    
    # Test new issue (no phase label)
    labels = ["feature", "priority-high"]
    phase = manager._extract_current_phase(labels)
    assert phase == "new"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
