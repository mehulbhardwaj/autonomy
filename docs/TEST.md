# Test Strategy Document (Core)

**Version:** 2.0   |   **Project:** Autonomy Planning Agent (Core)   |   **Focus:** Open Core Agentic Platform Testing

---

## 1. Testing Philosophy (Core)

### Core Testing Principles
1. **Test AI Agent Behavior**: Verify intelligent decision-making with predictable outcomes
2. **Mock LLM Interactions**: Use deterministic responses for reproducible testing
3. **Memory Isolation**: Each test operates with isolated memory context
4. **Permission Validation**: Verify all security and access controls
5. **Error Resilience**: Test graceful degradation and error recovery

### Quality Standards
- **Unit Test Coverage**: >90% for core business logic
- **Integration Test Coverage**: >80% for API interactions
- **E2E Test Coverage**: All critical user workflows
- **Performance Benchmarks**: All response time targets met
- **Security Validation**: All permission checks verified

---

## 2. Test Architecture (Core)

- This document covers only the open source, GPLv3-licensed core testing strategy. Proprietary/enterprise features are out of scope and will be detailed in the pro TEST doc.

### Test Pyramid Structure
```
    ┌─────────────────┐
    │   E2E Tests     │  ← Complete workflows (10%)
    │     (Slow)      │    Full agent collaboration
    └─────────────────┘
           ▲
    ┌─────────────────┐
    │ Integration     │  ← Component interaction (20%)
    │     Tests       │    GitHub API, Memory + LLM
    └─────────────────┘
           ▲
    ┌─────────────────┐
    │  Unit Tests     │  ← Individual components (70%)
    │    (Fast)       │    Agents, Memory, Tools
    └─────────────────┘
```

### Test Organization
```
tests/
├── unit/                     # Fast, isolated tests
│   ├── agents/
│   │   ├── test_planning.py      # Planning agent logic
│   │   ├── test_pm.py            # PM agent behavior
│   │   ├── test_sde.py           # SDE agent functionality
│   │   └── test_qa.py            # QA agent capabilities
│   ├── memory/
│   │   ├── test_mem0_client.py   # Memory integration
│   │   ├── test_context_builder.py # Context aggregation
│   │   └── test_graph_store.py   # Relationship tracking
│   ├── llm/
│   │   ├── test_openrouter.py    # LLM gateway
│   │   ├── test_model_selector.py # Model selection
│   │   └── test_fallback.py      # Fallback strategies
│   └── tools/
│       ├── test_registry.py      # Tool registry
│       ├── test_github_tools.py  # GitHub tool implementations
│       └── test_slack_tools.py   # Slack tool implementations
├── integration/              # Component interaction tests
│   ├── test_agent_memory.py      # Agents + Memory integration
│   ├── test_agent_tools.py       # Agents + Tools integration
│   ├── test_github_api.py        # GitHub API integration
│   ├── test_slack_api.py         # Slack API integration
│   ├── test_workflows.py         # LangGraph workflows
│   └── test_permission_system.py # Security integration
├── e2e/                      # End-to-end workflow tests
│   ├── test_planning_workflow.py # Complete planning cycles
│   ├── test_team_collaboration.py # Multi-agent scenarios
│   ├── test_memory_learning.py   # Memory-based learning
│   └── test_cli_workflows.py     # CLI user experience
├── performance/              # Performance and load tests
│   ├── test_response_times.py    # Response time benchmarks
│   ├── test_memory_growth.py     # Memory system performance
│   └── test_llm_efficiency.py    # LLM usage optimization
└── fixtures/                 # Shared test data
    ├── mock_responses/           # Mock LLM responses
    ├── test_repositories/        # GitHub test data
    └── sample_memories/          # Memory test data
```

---

## 3. Testing Standards by Component

### 3.1 Agent Testing

#### Unit Testing Agents
```python
# Example: Planning Agent Unit Tests
class TestPlanningAgent:
    def setup_method(self):
        """Setup isolated test environment"""
        self.mock_memory = MockMem0Client()
        self.mock_llm = MockLLMGateway()
        self.mock_tools = MockToolRegistry()
        
        self.agent = PlanningAgent(
            memory=self.mock_memory,
            llm_gateway=self.mock_llm,
            tool_registry=self.mock_tools
        )
    
    def test_issue_analysis_basic(self):
        """Test basic issue analysis functionality"""
        # Given: A simple issue
        issue = Issue(
            title="Add user authentication",
            body="Users should be able to log in with email/password",
            labels=["feature", "P1"]
        )
        
        # When: Agent analyzes the issue
        analysis = self.agent.analyze_issue(issue)
        
        # Then: Analysis includes expected components
        assert analysis.complexity in ["low", "medium", "high"]
        assert analysis.estimated_effort > 0
        assert len(analysis.dependencies) >= 0
        assert analysis.recommended_approach is not None
    
    def test_memory_integration(self):
        """Test agent uses memory for context"""
        # Given: Previous similar issues in memory
        self.mock_memory.add_memory(
            "authentication_patterns",
            "Previous auth implementations used JWT tokens"
        )
        
        # When: Agent analyzes auth-related issue
        issue = Issue(title="Add OAuth authentication")
        analysis = self.agent.analyze_issue(issue)
        
        # Then: Agent references past experience
        self.mock_memory.search_memories.assert_called()
        assert "JWT" in analysis.context or "previous" in analysis.context.lower()
    
    def test_tool_usage_permissions(self):
        """Test agent respects tool permissions"""
        # Given: Restricted tool access
        self.mock_tools.set_permissions("github_create_issue", ["admin"])
        
        # When: Agent tries to use restricted tool
        with pytest.raises(PermissionError):
            self.agent.create_follow_up_issue("Test issue")
```

#### Integration Testing Agent Workflows
```python
class TestAgentWorkflowIntegration:
    def test_planning_to_execution_handoff(self):
        """Test complete planning to execution workflow"""
        # Given: Planning agent completes analysis
        planning_result = planning_agent.analyze_issue(issue)
        
        # When: SDE agent receives planning result
        implementation_plan = sde_agent.create_implementation_plan(planning_result)
        
        # Then: Plan maintains context and adds technical details
        assert implementation_plan.requirements == planning_result.requirements
        assert len(implementation_plan.technical_tasks) > 0
        assert implementation_plan.test_strategy is not None
```

### 3.2 Memory System Testing

#### Memory Accuracy and Retrieval
```python
class TestMemorySystem:
    def test_issue_context_memory(self):
        """Test issue context is properly stored and retrieved"""
        # Given: A completed issue interaction
        issue = Issue(title="Fix login bug")
        solution = "Updated password validation logic"
        
        # When: Memory stores the interaction
        memory.remember_interaction(issue, solution, outcome="success")
        
        # Then: Similar issues retrieve relevant context
        similar_issue = Issue(title="Password reset not working")
        context = memory.get_context(similar_issue)
        
        assert "password validation" in context.lower()
        assert context.confidence_score > 0.7
    
    def test_team_pattern_learning(self):
        """Test memory learns team collaboration patterns"""
        # Given: Multiple team interactions
        for i in range(5):
            memory.remember_team_decision(
                issue_type="bug",
                decision_maker="alice",
                outcome="approved",
                pattern="prefers_quick_fixes"
            )
        
        # When: Similar situation arises
        pattern = memory.get_team_pattern("bug", "alice")
        
        # Then: Memory suggests learned pattern
        assert pattern.preference == "quick_fixes"
        assert pattern.confidence > 0.8
```

### 3.3 LLM Integration Testing

#### Model Selection and Fallback
```python
class TestLLMIntegration:
    def test_model_fallback_chain(self):
        """Test fallback when primary model fails"""
        # Given: Primary model fails
        openrouter_client.models["gpt-4o-mini"].set_failure(True)
        
        # When: Agent makes LLM call
        response = llm_gateway.complete(
            messages=[{"role": "user", "content": "Analyze this issue"}],
            preferred_model="gpt-4o-mini"
        )
        
        # Then: Fallback model is used
        assert response.model_used == "claude-3-haiku"
        assert response.content is not None
    
    def test_cost_tracking(self):
        """Test LLM usage cost tracking"""
        # Given: Cost tracking enabled
        cost_tracker = llm_gateway.cost_tracker
        initial_cost = cost_tracker.total_cost
        
        # When: Multiple LLM calls made
        for _ in range(3):
            llm_gateway.complete([{"role": "user", "content": "test"}])
        
        # Then: Costs are tracked accurately
        assert cost_tracker.total_cost > initial_cost
        assert len(cost_tracker.usage_log) == 3
```

### 3.4 GitHub Integration Testing

#### Projects v2 GraphQL Testing
```python
class TestGitHubIntegration:
    def test_projects_v2_field_creation(self):
        """Test Projects v2 field creation and caching"""
        # Given: Repository without custom fields
        repo = test_repositories.get_clean_repo()
        
        # When: Bootstrap creates fields
        fields = projects_manager.bootstrap_project(repo)
        
        # Then: Required fields are created and cached
        assert "Priority" in fields
        assert "Pinned" in fields  
        assert "Sprint" in fields
        assert field_cache.has_fields(repo.id)
    
    def test_issue_ranking_integration(self):
        """Test issue ranking with real GitHub data"""
        # Given: Repository with issues and Projects v2 fields
        issues = github_client.get_issues(repo_id, state="open")
        
        # When: Ranking engine processes issues
        ranked_issues = ranking_engine.rank_issues(issues)
        
        # Then: Issues are ranked according to priority logic
        assert len(ranked_issues) == len(issues)
        assert ranked_issues[0].priority_score >= ranked_issues[-1].priority_score
```

### 3.5 Tool Registry Testing

#### Permission and Audit Testing
```python
class TestToolRegistry:
    def test_permission_enforcement(self):
        """Test tool permission enforcement"""
        # Given: Agent with limited permissions
        agent = Agent(id="test_agent", permissions=["read"])
        
        # When: Agent tries to use write tool
        with pytest.raises(PermissionError):
            tool_registry.execute_tool(
                "github_update_issue",
                agent=agent,
                params={"issue_id": "123", "updates": {"title": "New title"}}
            )
    
    def test_audit_logging(self):
        """Test tool usage audit logging"""
        # Given: Tool registry with audit logging
        agent = Agent(id="authorized_agent", permissions=["write"])
        
        # When: Agent uses tool
        result = tool_registry.execute_tool(
            "github_update_issue",
            agent=agent,
            params={"issue_id": "123", "updates": {"title": "Updated"}}
        )
        
        # Then: Usage is logged
        audit_entries = audit_logger.get_entries(agent_id="authorized_agent")
        assert len(audit_entries) == 1
        assert audit_entries[0].tool_name == "github_update_issue"
        assert audit_entries[0].success == result.success
```

---

## 4. End-to-End Testing Scenarios

### 4.1 Complete Planning Workflow
```python
class TestPlanningWorkflow:
    def test_issue_to_completion_workflow(self):
        """Test complete issue processing workflow"""
        # Given: New issue created
        issue = github_client.create_issue(
            title="Add dark mode toggle",
            body="Users want dark mode option in settings",
            labels=["feature", "P2"]
        )
        
        # When: Planning workflow processes issue
        result = planning_workflow.execute(issue)
        
        # Then: Issue progresses through all phases
        assert result.phases_completed == ["analyze", "plan", "review"]
        assert result.artifacts_created is not None
        assert result.human_checkpoints_passed > 0
        
        # And: Issue is updated with results
        updated_issue = github_client.get_issue(issue.number)
        assert "planned" in [label.name for label in updated_issue.labels]
```

### 4.2 Team Collaboration Scenarios
```python
class TestTeamCollaboration:
    def test_multi_agent_coordination(self):
        """Test multiple agents working on same issue"""
        # Given: Complex issue requiring multiple agents
        issue = Issue(
            title="Redesign user dashboard",
            body="Complex UI/UX overhaul with backend changes"
        )
        
        # When: Multiple agents collaborate
        pm_result = pm_agent.analyze_requirements(issue)
        sde_result = sde_agent.plan_implementation(pm_result)
        qa_result = qa_agent.plan_testing(sde_result)
        
        # Then: Agents build on each other's work
        assert sde_result.requirements_source == pm_result.id
        assert qa_result.implementation_source == sde_result.id
        assert qa_result.test_coverage > 0.8
```

### 4.3 Memory Learning Validation
```python
class TestMemoryLearning:
    def test_learning_from_successful_patterns(self):
        """Test memory improves recommendations over time"""
        # Given: Multiple successful implementations of similar features
        successful_patterns = [
            complete_feature_implementation("user_auth", "jwt_approach"),
            complete_feature_implementation("admin_auth", "jwt_approach"),
            complete_feature_implementation("api_auth", "jwt_approach")
        ]
        
        # When: New auth feature is planned
        new_auth_issue = Issue(title="Add OAuth authentication")
        recommendations = planning_agent.get_recommendations(new_auth_issue)
        
        # Then: Agent recommends proven approach
        assert "jwt" in recommendations.suggested_approach.lower()
        assert recommendations.confidence > 0.9
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
        result = cli.invoke(["next", "--assignee", "alice"])
        response_time = time.time() - start_time
        
        assert response_time < 2.0
        assert result.exit_code == 0
    
    def test_memory_retrieval_performance(self):
        """Test memory system performance"""
        # Target: < 500ms for context building
        
        # Given: Large memory store
        for i in range(1000):
            memory.add_memory(f"test_memory_{i}", f"content_{i}")
        
        # When: Context is retrieved
        start_time = time.time()
        context = memory.get_context("test query")
        retrieval_time = time.time() - start_time
        
        # Then: Retrieval is fast
        assert retrieval_time < 0.5
        assert len(context) > 0
```

### 5.2 Load Testing
```python
class TestLoadPerformance:
    def test_concurrent_agent_operations(self):
        """Test system handles concurrent agent operations"""
        # Given: Multiple agents working simultaneously
        agents = [create_test_agent(f"agent_{i}") for i in range(10)]
        
        # When: All agents process issues concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(agent.process_issue, f"issue_{i}")
                for i, agent in enumerate(agents)
            ]
            results = [future.result() for future in futures]
        
        # Then: All operations complete successfully
        assert len(results) == 10
        assert all(result.success for result in results)
```

---

## 6. Security Testing

### 6.1 Permission System Validation
```python
class TestSecurity:
    def test_agent_permission_boundaries(self):
        """Test agents cannot exceed their permissions"""
        # Given: Agent with read-only permissions
        readonly_agent = Agent(
            id="readonly",
            permissions=["read_issues", "read_projects"]
        )
        
        # When: Agent attempts write operations
        with pytest.raises(PermissionError):
            tool_registry.execute_tool(
                "github_create_issue",
                agent=readonly_agent,
                params={"title": "Unauthorized issue"}
            )
    
    def test_memory_privacy_protection(self):
        """Test sensitive information is not stored in memory"""
        # Given: Interaction with sensitive data
        sensitive_content = "API key: sk-1234567890abcdef"
        
        # When: Memory processes the content
        memory.remember_interaction("user_query", sensitive_content)
        
        # Then: Sensitive data is filtered out
        stored_memories = memory.search_memories("API key")
        assert not any("sk-" in memory.content for memory in stored_memories)
```

---

## 7. Test Data Management

### 7.1 Mock LLM Responses
```python
# fixtures/mock_responses/planning_agent_responses.py
MOCK_RESPONSES = {
    "analyze_issue": {
        "input_pattern": "analyze.*authentication",
        "response": {
            "complexity": "medium",
            "estimated_effort": 5,
            "dependencies": ["user_model", "session_management"],
            "recommended_approach": "JWT-based authentication with refresh tokens"
        }
    },
    "generate_plan": {
        "input_pattern": "create.*plan.*authentication",
        "response": {
            "tasks": [
                "Design user authentication schema",
                "Implement JWT token generation",
                "Create login/logout endpoints",
                "Add session management"
            ],
            "timeline": "2 weeks",
            "resources_needed": ["backend_developer", "security_review"]
        }
    }
}
```

### 7.2 Test Repository Setup
```python
# fixtures/test_repositories.py
class TestRepositoryManager:
    def create_test_repository(self, name: str) -> Repository:
        """Create isolated test repository"""
        repo = github_client.create_repository(
            name=f"test-{name}-{uuid.uuid4()}",
            private=True,
            auto_init=True
        )
        
        # Add test issues and Projects v2 setup
        self.setup_test_issues(repo)
        self.setup_projects_v2(repo)
        
        return repo
    
    def cleanup_test_repository(self, repo: Repository):
        """Clean up test repository after tests"""
        github_client.delete_repository(repo.full_name)
```

---

## 8. Testing Guidelines for Developers

### 8.1 Writing Agent Tests
1. **Mock External Dependencies**: Always mock LLM calls, GitHub API, and Slack API
2. **Test Decision Logic**: Focus on testing the agent's decision-making process
3. **Verify Memory Usage**: Ensure agents properly use and update memory
4. **Test Error Handling**: Verify graceful degradation when services fail

### 8.2 Memory Testing Patterns
1. **Isolation**: Each test gets fresh memory context
2. **Deterministic Data**: Use consistent test data for reproducible results
3. **Relationship Testing**: Verify memory correctly captures relationships
4. **Privacy Validation**: Ensure sensitive data is not stored

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
- **Unit Tests**: Must pass with >90% coverage
- **Integration Tests**: Must pass with <5% flaky test rate
- **E2E Tests**: Must pass for all critical workflows
- **Performance Tests**: Must meet response time targets
- **Security Tests**: Must pass all permission and privacy checks

---

## 10. Testing Tools and Frameworks

### Required Testing Dependencies
```python
# pyproject.toml test dependencies
[project.optional-dependencies]
test = [
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
    def create_mock_agent(agent_type: str, permissions: List[str]) -> Agent:
        """Create mock agent for testing"""
        return Agent(
            id=f"test_{agent_type}",
            type="ai",
            role=agent_type,
            capabilities=[agent_type],
            permissions=permissions
        )
    
    @staticmethod
    def create_test_issue(title: str, complexity: str = "medium") -> Issue:
        """Create test issue with standard properties"""
        return Issue(
            title=title,
            body=f"Test issue for {complexity} complexity testing",
            labels=[complexity, "test"],
            created_at=datetime.now()
        )
```

---

**Testing Success Criteria**: All tests pass consistently, coverage targets met, performance benchmarks achieved, and security validations complete. The test suite provides confidence in system reliability and agent behavior predictability.