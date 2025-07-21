# Test Plan Document (TEST.md)
## Autonomous MCP - AI-Assisted Development Workflow

**Version**: 0.1.0  
**Date**: January 2025  
**Owner**: Development Team  
**Status**: In Progress  

---

## 1. Test Strategy Overview

### 1.1 Testing Objectives
- Ensure core package functionality works reliably
- Validate GitHub integration and API operations
- Verify configuration system and validation
- Confirm agent system architecture
- Test template system functionality

### 1.2 Testing Approach
- **Test-Driven Development**: Write tests before implementation
- **Unit Testing**: Test individual components in isolation
- **Integration Testing**: Test component interactions
- **Automated Testing**: Run tests on every commit
- **Mock-Based Testing**: Mock external dependencies (GitHub API, LLM APIs)

### 1.3 Current Status
- **Unit Tests**: Partially implemented, needs fixes
- **Integration Tests**: Basic GitHub API tests
- **System Tests**: Not yet implemented
- **Test Coverage**: ~46% (target: >80%)

---

## 2. Test Scope

### 2.1 In Scope ✅
- Core package imports and initialization
- Configuration system validation
- Agent class definitions and instantiation
- GitHub issue manager operations
- Plan manager template system
- CLI interface basic functionality

### 2.2 Current Issues 🔄
- Abstract base class instantiation errors
- Missing method implementations
- Import path corrections needed
- Mock setup improvements required

### 2.3 Out of Scope (Future Versions)
- LLM API integration testing
- Complex workflow orchestration
- Performance and load testing
- UI/UX testing
- Security penetration testing

---

## 3. Test Levels

### 3.1 Unit Testing

#### 3.1.1 Core Components
**Target Coverage**: >90% for core components

**Configuration System Tests:**
```python
def test_workflow_config_defaults():
    """Test default configuration values"""
    config = WorkflowConfig()
    assert config.max_file_lines == 300
    assert config.max_function_lines == 40
    assert config.test_coverage_target == 0.75
    assert config.autonomy_level == "supervised"

def test_workflow_config_validation():
    """Test configuration validation"""
    config = WorkflowConfig(max_file_lines=-1)
    assert not config.validate()
```

**Agent System Tests:**
```python
def test_pm_agent_initialization():
    """Test PM agent can be created with config"""
    config = WorkflowConfig()
    agent = PMAgent(config)
    assert agent.config == config
    assert "product manager" in agent.get_system_prompt().lower()

def test_agent_system_prompts():
    """Test all agents have valid system prompts"""
    config = WorkflowConfig()
    pm_agent = PMAgent(config)
    sde_agent = SDEAgent(config)
    qa_agent = QAAgent(config)
    
    assert len(pm_agent.get_system_prompt()) > 0
    assert len(sde_agent.get_system_prompt()) > 0
    assert len(qa_agent.get_system_prompt()) > 0
```

**Plan Manager Tests:**
```python
def test_plan_template_creation():
    """Test creating different plan templates"""
    manager = PlanManager()
    
    basic_plan = manager.create_plan_template("basic")
    api_plan = manager.create_plan_template("api")
    
    assert basic_plan["metadata"]["template_type"] == "basic"
    assert api_plan["metadata"]["template_type"] == "api"

def test_plan_validation():
    """Test plan validation logic"""
    manager = PlanManager()
    valid_plan = manager.create_plan_template("basic")
    
    errors = manager.validate_plan(valid_plan)
    assert len(errors) == 0
```

#### 3.1.2 Current Test Fixes Needed
**BaseAgent Abstract Class Issue:**
```python
# Fix: Don't instantiate BaseAgent directly in tests
def test_base_agent_interface():
    """Test base agent interface through concrete implementations"""
    config = WorkflowConfig()
    pm_agent = PMAgent(config)
    
    # Test that concrete agent implements required methods
    assert hasattr(pm_agent, 'get_system_prompt')
    assert callable(pm_agent.get_system_prompt)
```

**Agent Attribute Access:**
```python
# Fix: Update tests to match actual implementation
def test_pm_agent_properties():
    """Test PM agent properties and methods"""
    config = WorkflowConfig()
    agent = PMAgent(config)
    
    # Test actual implementation properties
    assert hasattr(agent, 'config')
    assert agent.config == config
    # Remove tests for non-existent 'role' attribute
```

### 3.2 Integration Testing

#### 3.2.1 GitHub API Integration
**Mock-Based GitHub Tests:**
```python
@patch('src.github.issue_manager.requests.get')
def test_issue_manager_initialization(mock_get):
    """Test IssueManager can be initialized"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"login": "testuser"}
    
    manager = IssueManager("fake_token", "owner", "repo")
    assert manager.github_token == "fake_token"
    assert manager.owner == "owner"
    assert manager.repo == "repo"

@patch('src.github.issue_manager.requests.post')
def test_create_issue_basic(mock_post):
    """Test basic issue creation"""
    mock_response = {
        "number": 1,
        "title": "Test Issue",
        "state": "open",
        "labels": []
    }
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = mock_response
    
    manager = IssueManager("fake_token", "owner", "repo")
    issue = manager.create_issue("Test Issue", "Test body", [])
    
    assert issue["number"] == 1
    assert issue["title"] == "Test Issue"
```

#### 3.2.2 Workflow Integration
```python
def test_workflow_manager_initialization():
    """Test WorkflowManager can be initialized with config"""
    config = WorkflowConfig()
    manager = WorkflowManager(
        github_token="fake_token",
        owner="owner",
        repo="repo",
        config=config
    )
    
    assert manager.config == config
    assert hasattr(manager, 'issue_manager')
```

### 3.3 System Testing

#### 3.3.1 End-to-End Package Testing
```python
def test_package_import():
    """Test that main package imports work correctly"""
    try:
        from src import WorkflowManager, WorkflowConfig
        from src.core.agents import PMAgent, SDEAgent, QAAgent
        from src.planning import PlanManager
        from src.github.issue_manager import IssueManager
        
        # Test basic instantiation
        config = WorkflowConfig()
        pm_agent = PMAgent(config)
        plan_manager = PlanManager()
        
        assert isinstance(config, WorkflowConfig)
        assert isinstance(pm_agent, PMAgent)
        assert isinstance(plan_manager, PlanManager)
        
    except ImportError as e:
        pytest.fail(f"Package import failed: {e}")
```

---

## 4. Test Implementation Status

### 4.1 Completed Tests ✅
- WorkflowConfig basic functionality
- PlanManager template creation
- Basic package imports
- Configuration validation

### 4.2 Tests Needing Fixes 🔄
- BaseAgent instantiation (abstract class issue)
- Agent role attribute access
- IssueManager method implementations
- WorkflowManager method availability

### 4.3 Missing Tests ❌
- Complete GitHub API integration
- Workflow orchestration
- CLI interface testing
- Error handling scenarios

---

## 5. Test Data and Fixtures

### 5.1 Test Configuration
```python
@pytest.fixture
def test_config():
    """Standard test configuration"""
    return WorkflowConfig(
        max_file_lines=300,
        max_function_lines=40,
        test_coverage_target=0.75,
        autonomy_level="supervised"
    )

@pytest.fixture
def mock_github_token():
    """Mock GitHub token for testing"""
    return "ghp_test_token_123456789"
```

### 5.2 Mock Data
```python
@pytest.fixture
def sample_issue_data():
    """Sample GitHub issue data for testing"""
    return {
        "number": 1,
        "title": "Test Feature Implementation",
        "body": "Implement a test feature with proper validation",
        "state": "open",
        "labels": [
            {"name": "feature", "color": "84b6eb"},
            {"name": "needs-requirements", "color": "ff7619"}
        ],
        "milestone": None,
        "assignee": None
    }
```

---

## 6. Test Execution

### 6.1 Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_autonomy_mcp.py -v

# Run tests with debugging
pytest tests/test_autonomy_mcp.py -v -s
```

### 6.2 Test Environment Setup
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Set up test environment
export GITHUB_TOKEN="test_token_for_integration_tests"

# Run tests in isolation
python -m pytest tests/
```

---

## 7. Quality Gates

### 7.1 Test Coverage Requirements
- **Unit Tests**: >90% coverage for core modules
- **Integration Tests**: All API endpoints covered
- **Overall Coverage**: >80% total coverage

### 7.2 Test Quality Standards
- All tests must pass before code merge
- No skipped tests in main branch
- Clear test names and documentation
- Proper mock usage for external dependencies

### 7.3 Performance Criteria
- Test suite completes in <60 seconds
- Individual tests complete in <5 seconds
- No memory leaks in test execution

---

## 8. Known Issues and Workarounds

### 8.1 Current Test Issues
```python
# Issue: BaseAgent can't be instantiated directly
# Workaround: Test through concrete implementations

# Issue: Some methods not implemented
# Workaround: Add implementation or skip tests temporarily

# Issue: Import path changes
# Workaround: Update import statements in tests
```

### 8.2 Temporary Skips
```python
@pytest.mark.skip(reason="Implementation not complete")
def test_workflow_orchestration():
    """This test is skipped until workflow manager is complete"""
    pass
```

---

## 9. Future Testing Improvements

### 9.1 Planned Enhancements
- **Property-based testing** for configuration validation
- **Mutation testing** to verify test quality
- **Performance testing** for GitHub API operations
- **Security testing** for token handling

### 9.2 Test Automation
- **GitHub Actions** for continuous testing
- **Pre-commit hooks** for test execution
- **Coverage reporting** in pull requests
- **Automated test generation** for new features

---

## 10. Test Maintenance

### 10.1 Regular Tasks
- Update test data when API changes
- Refactor tests to match code changes
- Remove obsolete tests
- Add tests for new features

### 10.2 Test Review Process
- Code reviews must include test changes
- Test coverage must not decrease
- New features require corresponding tests
- Test failures must be investigated promptly

---

**Status**: This test plan reflects the current v0.1.0 testing approach. Priority is on fixing existing test issues and establishing a solid foundation for future development. 
