# Test Strategy Document (Core)

**Version:** 2.0   |   **Project:** Autonomy Planning Agent (Core)   |   **Focus:** Simple CLI Tool Testing

---

## 1. Testing Philosophy (Core)

### Core Testing Principles
1. **Test Workflow Behavior**: Verify simple workflow execution with predictable outcomes
2. **Mock LLM Interactions**: Use deterministic responses for reproducible testing
3. **Memory Isolation**: Each test operates with isolated memory context
4. **Permission Validation**: Verify basic security and access controls
5. **Error Resilience**: Test graceful degradation and error recovery

### Quality Standards
- **Unit Test Coverage**: >80% for core business logic
- **Integration Test Coverage**: >70% for API interactions
- **E2E Test Coverage**: All critical user workflows
- **Performance Benchmarks**: Basic response time targets met
- **Security Validation**: Basic permission checks verified

---

## 2. Test Architecture (Core)

### Test Pyramid Structure
```
    ┌─────────────────┐
    │   E2E Tests     │  ← Complete workflows (10%)
    │     (Slow)      │    Full workflow execution
    └─────────────────┘
           ▲
    ┌─────────────────┐
    │ Integration     │  ← Component interaction (20%)
    │     Tests       │    GitHub API, Memory + LLM
    └─────────────────┘
           ▲
    ┌─────────────────┐
    │  Unit Tests     │  ← Individual components (70%)
    │    (Fast)       │    Workflows, Memory, Tools
    └─────────────────┘
```

### Test Organization
```
tests/
├── unit/                     # Fast, isolated tests
│   ├── test_workflows.py     # Workflow behavior tests
│   ├── test_memory.py        # Memory system tests
│   ├── test_llm.py           # LLM integration tests
│   └── test_tools.py         # Tool functionality tests
├── integration/              # Component interaction tests
│   ├── test_github_api.py    # GitHub API integration
│   ├── test_slack_api.py     # Slack API integration
│   └── test_memory_llm.py    # Memory + LLM integration
├── e2e/                      # End-to-end workflow tests
│   └── test_planning_flow.py # Complete planning workflows
└── fixtures/                 # Shared test data
    ├── mock_responses/        # Mock LLM responses
    └── test_repositories/     # GitHub test data
```

---

## 3. Testing Standards by Component

### 3.1 Workflow Testing

#### Unit Testing Workflows
```python
# Example: Planning Workflow Unit Tests
class TestPlanningWorkflow:
    def setup_method(self):
        """Setup isolated test environment"""
        self.mock_memory = MockMem0Client()
        self.mock_llm = MockOpenRouterClient()
        self.mock_github = MockGitHubTools()
        self.mock_slack = MockSlackTools()
        
        self.workflow = PlanningWorkflow(
            memory=self.mock_memory,
            llm=self.mock_llm,
            github=self.mock_github,
            slack=self.mock_slack
        )
    
    def test_issue_analysis_basic(self):
        """Test basic issue analysis functionality"""
        # Given: A simple issue
        issue = {
            "title": "Add user authentication",
            "labels": ["feature", "P1"],
            "repository": "default"
        }
        
        # When: Workflow analyzes the issue
        result = self.workflow.execute(issue)
        
        # Then: Analysis includes expected components
        assert result.success
        assert "analysis" in result.state.data
        assert "priority_score" in result.state.data
        assert "tasks" in result.state.data
    
    def test_memory_integration(self):
        """Test workflow uses memory for context"""
        # Given: Previous similar issues in memory
        self.mock_memory.add({
            "similar:auth": "Previous auth implementations used JWT tokens",
            "repository": "default"
        })
        
        # When: Workflow analyzes auth-related issue
        issue = {"title": "Add OAuth authentication", "repository": "default"}
        result = self.workflow.execute(issue)
        
        # Then: Workflow references past experience
        self.mock_memory.search.assert_called()
        assert "JWT" in result.state.data.get("analysis", "")
```

#### Integration Testing Workflow Execution
```python
class TestWorkflowIntegration:
    def test_planning_to_completion_workflow(self):
        """Test complete planning workflow execution"""
        # Given: Planning workflow with all components
        platform = AutonomyPlatform()
        workflow = platform.create_workflow(PlanningWorkflow)
        
        # When: Workflow processes an issue
        issue = {
            "title": "Add dark mode toggle",
            "labels": ["feature", "P2"],
            "repository": "default"
        }
        result = workflow.execute(issue)
        
        # Then: All steps complete successfully
        assert result.success
        assert "analysis" in result.state.data
        assert "priority_score" in result.state.data
        assert "tasks" in result.state.data
        assert "plan" in result.state.data
```

### 3.2 Memory System Testing

#### Memory Accuracy and Retrieval
```python
class TestMemorySystem:
    def test_issue_context_memory(self):
        """Test issue context is properly stored and retrieved"""
        # Given: A completed issue interaction
        memory = Mem0Client()
        memory.add({
            "tasks:login": "Implement JWT authentication",
            "repository": "default"
        })
        
        # When: Similar issue is processed
        context = memory.search("similar:login", {"repository": "default"})
        
        # Then: Relevant context is retrieved
        assert "JWT" in context.lower()
    
    def test_memory_cleanup(self):
        """Test memory cleanup when max entries reached"""
        # Given: Memory with max entries limit
        memory = Mem0Client(max_entries=2)
        
        # When: Adding more entries than limit
        memory.add({"a": "1", "repository": "default"})
        memory.add({"b": "2", "repository": "default"})
        memory.add({"c": "3", "repository": "default"})
        
        # Then: Oldest entry is removed
        assert "a" not in memory.store["default"]
        assert len(memory.store["default"]) == 2
```

### 3.3 LLM Integration Testing

#### Model Selection and Fallback
```python
class TestLLMIntegration:
    def test_model_fallback_chain(self):
        """Test fallback when primary model fails"""
        # Given: Primary model fails
        client = OpenRouterClient()
        
        # When: Making LLM call with fallback
        response = client.complete_with_fallback(
            messages=[{"role": "user", "content": "Analyze this issue"}],
            models=["failing-model", "working-model"]
        )
        
        # Then: Fallback model is used
        assert response is not None
        assert response.startswith("LLM:")  # Mock response
    
    def test_cost_tracking(self):
        """Test LLM usage cost tracking"""
        # Given: Cost tracking enabled
        client = OpenRouterClient()
        initial_cost = len(client.costs)
        
        # When: Multiple LLM calls made
        for _ in range(3):
            client.complete_with_fallback(
                [{"role": "user", "content": "test"}],
                models=["openai/gpt-4o"]
            )
        
        # Then: Costs are tracked
        assert len(client.costs) > initial_cost
```

### 3.4 GitHub Integration Testing

#### Projects v2 GraphQL Testing
```python
class TestGitHubIntegration:
    def test_projects_v2_field_creation(self):
        """Test Projects v2 field creation and caching"""
        # Given: Repository without custom fields
        manager = IssueManager("token", "owner", "repo")
        
        # When: Bootstrap creates fields
        fields = manager.bootstrap_project()
        
        # Then: Required fields are created
        assert "Priority" in fields
        assert "Pinned" in fields  
        assert "Sprint" in fields
    
    def test_issue_ranking_integration(self):
        """Test issue ranking with real GitHub data"""
        # Given: Repository with issues
        issues = [
            {"labels": ["P1"], "created_at": "2025-01-01"},
            {"labels": ["P2"], "created_at": "2025-01-02"}
        ]
        
        # When: Ranking engine processes issues
        ranking = RankingEngine()
        scores = [ranking.score_issue(issue) for issue in issues]
        
        # Then: Issues are ranked according to priority logic
        assert scores[0] >= scores[1]  # P1 should score higher than P2
```

---

## 4. End-to-End Testing Scenarios

### 4.1 Complete Planning Workflow
```python
class TestPlanningWorkflow:
    def test_issue_to_completion_workflow(self):
        """Test complete issue processing workflow"""
        # Given: New issue to process
        platform = AutonomyPlatform()
        workflow = platform.create_workflow(PlanningWorkflow)
        
        issue = {
            "title": "Add dark mode toggle",
            "labels": ["feature", "P2"],
            "repository": "default"
        }
        
        # When: Planning workflow processes issue
        result = workflow.execute(issue)
        
        # Then: Issue progresses through all phases
        assert result.success
        assert "analysis" in result.state.data
        assert "priority_score" in result.state.data
        assert "tasks" in result.state.data
        assert "plan" in result.state.data
```

### 4.2 CLI Integration Testing
```python
class TestCLIIntegration:
    def test_plan_command(self):
        """Test CLI plan command execution"""
        # Given: CLI with planning workflow
        from src.cli.main import cmd_plan
        
        # When: Executing plan command
        result = cmd_plan(manager, args)
        
        # Then: Command executes successfully
        assert result == 0
```

---

## 5. Performance Testing

### 5.1 Response Time Benchmarks
```python
class TestPerformance:
    def test_cli_response_times(self):
        """Test CLI command response times"""
        # Target: < 2 seconds for most operations
        
        start_time = time.time()
        result = cli.invoke(["plan", "--issue", "123"])
        response_time = time.time() - start_time
        
        assert response_time < 2.0
        assert result.exit_code == 0
    
    def test_memory_retrieval_performance(self):
        """Test memory system performance"""
        # Target: < 500ms for context building
        
        # Given: Memory store with data
        memory = Mem0Client()
        for i in range(100):
            memory.add({f"test_{i}": f"content_{i}", "repository": "default"})
        
        # When: Context is retrieved
        start_time = time.time()
        context = memory.search("test", {"repository": "default"})
        retrieval_time = time.time() - start_time
        
        # Then: Retrieval is fast
        assert retrieval_time < 0.5
        assert len(context) > 0
```

---

## 6. Security Testing

### 6.1 Basic Permission System Validation
```python
class TestSecurity:
    def test_basic_permission_checks(self):
        """Test basic permission validation"""
        # Given: Workflow with permission checks
        workflow = PlanningWorkflow(memory, llm, github, slack)
        
        # When: Workflow executes
        result = workflow.execute({"title": "test"})
        
        # Then: No permission errors occur
        assert result.success
    
    def test_memory_privacy_protection(self):
        """Test sensitive information is not stored in memory"""
        # Given: Interaction with sensitive data
        memory = Mem0Client()
        sensitive_content = "API key: sk-1234567890abcdef"
        
        # When: Memory processes the content
        memory.add({
            "sensitive": sensitive_content,
            "repository": "default"
        })
        
        # Then: Sensitive data is handled appropriately
        stored = memory.search("sensitive", {"repository": "default"})
        # Note: In real implementation, sensitive data should be filtered
        assert stored == sensitive_content  # Current simple implementation
```

---

## 7. Test Data Management

### 7.1 Mock LLM Responses
```python
# fixtures/mock_responses/planning_workflow_responses.py
MOCK_RESPONSES = {
    "analyze_issue": {
        "input_pattern": "analyze.*authentication",
        "response": "LLM: Analysis of authentication feature"
    },
    "decompose_tasks": {
        "input_pattern": "decompose.*auth",
        "response": "LLM: Task1; Task2; Task3"
    },
    "generate_plan": {
        "input_pattern": "plan.*auth",
        "response": "LLM: Implementation plan for authentication"
    }
}
```

### 7.2 Test Repository Setup
```python
# fixtures/test_repositories.py
class TestRepositoryManager:
    def create_test_repository(self, name: str) -> Repository:
        """Create isolated test repository"""
        # Mock repository creation for testing
        return {
            "name": f"test-{name}",
            "full_name": f"test-org/test-{name}",
            "private": True
        }
```

---

## 8. Testing Guidelines for Developers

### 8.1 Writing Workflow Tests
1. **Mock External Dependencies**: Always mock LLM calls, GitHub API, and Slack API
2. **Test Decision Logic**: Focus on testing the workflow's decision-making process
3. **Verify Memory Usage**: Ensure workflows properly use and update memory
4. **Test Error Handling**: Verify graceful degradation when services fail

### 8.2 Memory Testing Patterns
1. **Isolation**: Each test gets fresh memory context
2. **Deterministic Data**: Use consistent test data for reproducible results
3. **Simple Storage**: Verify memory correctly stores and retrieves data
4. **Privacy Validation**: Ensure sensitive data is handled appropriately

### 8.3 Integration Testing Best Practices
1. **Real API Testing**: Use real GitHub/Slack APIs for integration tests
2. **Rate Limit Respect**: Implement delays to respect API rate limits
3. **Cleanup**: Always clean up test data after tests
4. **Environment Isolation**: Use separate test GitHub organizations

---

## 9. Continuous Integration

### 9.1 GitHub Actions Test Pipeline
```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e .[dev]
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: pytest tests/integration/ -v
        env:
          GITHUB_TOKEN: ${{ secrets.TEST_GITHUB_TOKEN }}
          OPENROUTER_API_KEY: ${{ secrets.TEST_OPENROUTER_KEY }}

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4
      - name: Run e2e tests
        run: pytest tests/e2e/ -v --timeout=300
        env:
          GITHUB_TOKEN: ${{ secrets.TEST_GITHUB_TOKEN }}
```

### 9.2 Quality Gates
- **Unit Tests**: Must pass with >80% coverage
- **Integration Tests**: Must pass with <5% flaky test rate
- **E2E Tests**: Must pass for all critical workflows
- **Performance Tests**: Must meet response time targets
- **Security Tests**: Must pass all basic permission checks

---

## 10. Testing Tools and Frameworks

### Required Testing Dependencies
```python
# pyproject.toml test dependencies
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.10.0",
    "pytest-timeout>=2.1.0",
    "responses>=0.23.0",      # HTTP request mocking
    "factory-boy>=3.2.0",    # Test data factories
    "freezegun>=1.2.0",      # Time mocking
    "httpx>=0.24.0",         # HTTP client testing
]
```

### Test Utilities
```python
# tests/utils/test_helpers.py
class TestHelpers:
    @staticmethod
    def create_mock_workflow(workflow_type: str) -> BaseWorkflow:
        """Create mock workflow for testing"""
        return PlanningWorkflow(
            memory=MockMem0Client(),
            llm=MockOpenRouterClient(),
            github=MockGitHubTools(),
            slack=MockSlackTools()
        )
    
    @staticmethod
    def create_test_issue(title: str, priority: str = "P2") -> Dict:
        """Create test issue with standard properties"""
        return {
            "title": title,
            "labels": [priority, "test"],
            "repository": "default"
        }
```

---

**Testing Success Criteria**: All tests pass consistently, coverage targets met, performance benchmarks achieved, and security validations complete. The test suite provides confidence in system reliability and workflow behavior predictability.
