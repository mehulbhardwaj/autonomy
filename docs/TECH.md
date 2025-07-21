# Autonomy Planning Agent – Technical Architecture (Core)

**Version:** 2.0   |   **Target:** Agentic Platform for Team Collaboration   |   **Design Principle:** Human + AI Collaboration

---

## 1. Vision & Principles

### Core Vision
**Agentic platform enabling humans + AI to collaborate for knowledge work**, specifically focused on intelligent GitHub project planning and task coordination.

### Guiding Principles
1. **Human + AI Collaboration** – AI agents augment human decision-making, don't replace it
2. **Memory-Driven Intelligence** – Agents learn from past interactions and team patterns
3. **Flexible Agent Coordination** – Support for multiple agent types (AI and human)
4. **GitHub-Native Integration** – Leverage Projects v2, Issues, and native workflows
5. **Transparency & Auditability** – All AI decisions explainable and reversible

---

## 2. Architectural Overview (Core)

- This document covers only the open source, GPLv3-licensed core architecture. Proprietary/enterprise features are out of scope and will be detailed in the pro TECH doc.

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Client    │    │   Slack Bot     │    │  Web Interface  │
│   (Click)       │    │   (Webhooks)    │    │   (Future)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Agent Platform │
                    │   (LangGraph)   │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  LLM Gateway    │    │  Memory System  │    │  Tool Registry  │
│  (OpenRouter)   │    │   (Mem0)        │    │ (GitHub/Slack)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   GitHub API    │
                    │  (Source of     │
                    │    Truth)       │
                    └─────────────────┘
```

### Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Agent Orchestration** | LangGraph | Production-ready agent workflows with state management |
| **LLM Integration** | OpenRouter | Unified access to 400+ models with fallback capabilities |
| **Memory System** | Mem0 | Graph-based memory with relationship tracking |
| **CLI Framework** | Python Click | Professional CLI with rich output |
| **GitHub Integration** | GraphQL + REST | Projects v2 for advanced features, REST for simple ops |
| **Slack Integration** | Slack Web API | Team communication and notifications |
| **Secret Management** | OS Keychain + Fernet | Native security with encrypted fallback |

---

## 3. Simplified Agent Architecture (Core)

### Core Design Philosophy

**Keep it Simple**: LangGraph + Mem0 + OpenRouter provides everything we need for extensibility without over-engineering. Focus on elegant composition over complex abstraction.

#### **Three-Layer Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflows                     │
│            (Orchestration & State Management)              │
├─────────────────────────────────────────────────────────────┤
│  Planning       │    Specialist    │      Custom           │
│  Workflows      │    Workflows     │      Workflows        │
│  • Plan Issue   │  • Code Review   │  • User-Defined       │
│  • Prioritize   │  • Test Design   │  • Domain-Specific    │
│  • Coordinate   │  • Security Scan │  • Integration        │
├─────────────────────────────────────────────────────────────┤
│         Shared Foundation: Mem0 + OpenRouter + Tools       │
│         (Memory, LLM Gateway, GitHub/Slack Integration)    │
└─────────────────────────────────────────────────────────────┘
```

### Core Planning Agent (Out of the Box)

The **Planning Agent** is the foundational organizational intelligence that ships with the platform. It's what makes this a team coordination tool rather than just a developer tool.

#### **Planning Agent Core Responsibilities**
```python
class PlanningWorkflow(BaseWorkflow):
    """
    Core Planning Agent - the organizational brain of the platform
    Ships out of the box, provides immediate value for team coordination
    """
    
    def _build_graph(self) -> StateGraph:
        return StateGraph({
            "analyze_issue": self.analyze_issue_context,
            "rank_priority": self.calculate_priority_score,
            "decompose_tasks": self.break_down_into_tasks,
            "route_workflows": self.determine_required_workflows,
            "assign_optimal": self.suggest_team_assignments,
            "create_plan": self.generate_execution_plan,
            "get_approval": self.human_approval_gate
        })
    
    def analyze_issue_context(self, state: Dict) -> Dict:
        """Understand issue scope, type, and complexity"""
        issue = state['issue']
        
        # Get similar issues from memory
        similar_context = self.memory.search(
            f"issues similar to {issue.title}",
            filter_metadata={"repository": state['repository']}
        )
        
        # Analyze with LLM
        analysis = self.llm.complete([
            {"role": "system", "content": "You are a planning expert. Analyze issues for scope, complexity, and type."},
            {"role": "user", "content": f"""
            Issue: {issue.title}
            Description: {issue.body}
            Labels: {issue.labels}
            
            Similar past issues: {similar_context}
            
            Analyze:
            1. Issue type (bug, feature, epic, spike, etc.)
            2. Complexity (low, medium, high)
            3. Estimated effort (story points 1-8)
            4. Key dependencies and blockers
            5. Risk factors
            """}
        ])
        
        return {"analysis": analysis, **state}
    
    def calculate_priority_score(self, state: Dict) -> Dict:
        """Apply repo-specific ranking criteria with learning"""
        issue = state['issue']
        analysis = state['analysis']
        
        # Get repo-specific ranking preferences
        ranking_config = self.memory.search(
            f"priority ranking patterns",
            filter_metadata={"repository": state['repository']}
        )
        
        # Calculate base score from multiple signals
        priority_score = self._calculate_base_priority(issue, analysis, ranking_config)
        
        # Apply team context adjustments
        team_context = self.memory.search(
            f"team capacity and preferences",
            filter_metadata={"repository": state['repository']}
        )
        
        adjusted_score = self._adjust_for_team_context(priority_score, team_context)
        
        return {"priority_score": adjusted_score, **state}
    
    def determine_required_workflows(self, state: Dict) -> Dict:
        """Decide which other workflows this issue needs"""
        analysis = state['analysis']
        
        required_workflows = []
        
        # Security review needed?
        if any(keyword in analysis.lower() for keyword in ['auth', 'security', 'password', 'token']):
            required_workflows.append('security')
        
        # Code review needed?
        if 'implementation' in analysis.lower() or 'code' in analysis.lower():
            required_workflows.append('code_review')
        
        # Documentation needed?
        if 'api' in analysis.lower() or 'public' in analysis.lower():
            required_workflows.append('documentation')
        
        return {"required_workflows": required_workflows, **state}
```

#### **Repository-Specific Customization**
```python
class PlanningConfig:
    """Per-repository planning configuration"""
    
    def __init__(self, repository: str):
        self.repository = repository
        
        # Default ranking weights (can be overridden per repo)
        self.ranking_weights = {
            "priority_label": 0.4,      # P0=1.0, P1=0.7, P2=0.4, P3=0.1
            "sprint_proximity": 0.3,     # How close to current sprint
            "issue_age": 0.1,           # Older issues get slight boost
            "dependency_urgency": 0.2,   # Blocks other work
        }
        
        # Team-specific patterns (learned from memory)
        self.team_preferences = {}
        
        # Workflow routing rules
        self.workflow_rules = {
            "security_keywords": ["auth", "security", "password", "token", "crypto"],
            "documentation_requirements": ["api", "public", "integration"],
            "performance_triggers": ["slow", "performance", "optimization", "scale"]
        }
```

### Extensible Workflow Platform

**Simple Inheritance Model** - Users create new workflows by inheriting from `BaseWorkflow`
**Planning Agent Orchestration** - New workflows integrate with Planning Agent decisions  
**Repository Customization** - Each repo can tune the Planning Agent's behavior

### Simple Workflow-Based Implementation

#### **Core Platform Pattern**
```python
class AutonomyPlatform:
    def __init__(self):
        # Shared foundation - simple and elegant
        self.memory = Mem0Client()
        self.llm = OpenRouterClient()
        self.github = GitHubTools()
        self.slack = SlackTools()
    
    def create_workflow(self, workflow_class: Type[BaseWorkflow]) -> BaseWorkflow:
        """Create any workflow with shared foundation"""
        return workflow_class(
            memory=self.memory,
            llm=self.llm,
            github=self.github,
            slack=self.slack
        )

class BaseWorkflow:
    def __init__(self, memory: Mem0Client, llm: OpenRouterClient, 
                 github: GitHubTools, slack: SlackTools):
        self.memory = memory
        self.llm = llm  
        self.github = github
        self.slack = slack
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Override this to define workflow steps"""
        raise NotImplementedError

# Example: Planning Workflow (Core)
class PlanningWorkflow(BaseWorkflow):
    def _build_graph(self) -> StateGraph:
        return StateGraph({
            "analyze_issue": self.analyze_issue,
            "determine_approach": self.determine_approach,
            "create_plan": self.create_plan,
            "get_approval": self.get_human_approval
        })
    
    def analyze_issue(self, state: Dict) -> Dict:
        # Use shared memory and LLM
        context = self.memory.get_context(f"issue_{state['issue_id']}")
        analysis = self.llm.complete([
            {"role": "system", "content": "You are a planning expert..."},
            {"role": "user", "content": f"Analyze: {state['issue']} Context: {context}"}
        ])
        return {"analysis": analysis, **state}

# Example: Code Review Workflow (Specialist)  
class CodeReviewWorkflow(BaseWorkflow):
    def _build_graph(self) -> StateGraph:
        return StateGraph({
            "fetch_pr": self.fetch_pr_details,
            "analyze_code": self.analyze_code_changes,
            "check_tests": self.verify_test_coverage,
            "provide_feedback": self.generate_feedback
        })

# Example: Custom Security Workflow
class SecurityWorkflow(BaseWorkflow):
    def _build_graph(self) -> StateGraph:
        return StateGraph({
            "scan_vulnerabilities": self.run_security_scan,
            "check_dependencies": self.check_dependency_security,
            "validate_auth": self.validate_authentication,
            "report_findings": self.create_security_report
        })
```

### Workflow Composition & Orchestration

```python
# Simple workflow chaining and composition
class MasterOrchestrator:
    def __init__(self, platform: AutonomyPlatform):
        self.platform = platform
        
        # Create workflows as needed - no registry overhead
        self.planning = platform.create_workflow(PlanningWorkflow)
        self.code_review = platform.create_workflow(CodeReviewWorkflow)
        self.security = platform.create_workflow(SecurityWorkflow)
    
    def process_issue(self, issue: Issue) -> WorkflowResult:
        # Start with planning (always)
        plan_result = self.planning.execute({"issue": issue})
        
        # Chain additional workflows based on planning decision
        if plan_result.requires_security_review:
            security_result = self.security.execute(plan_result.state)
            plan_result.state.update(security_result.state)
        
        if plan_result.has_code_changes:
            review_result = self.code_review.execute(plan_result.state)
            plan_result.state.update(review_result.state)
        
        return plan_result

# Memory-driven intelligence - simple pattern
class WorkflowBase:
    def remember_and_learn(self, interaction_type: str, context: Dict, outcome: Dict):
        """Simple pattern: remember what worked"""
        self.memory.add({
            "type": interaction_type,
            "context": context,
            "outcome": outcome,
            "timestamp": datetime.now(),
            "workflow": self.__class__.__name__
        })
    
    def get_similar_context(self, current_situation: Dict) -> str:
        """Simple pattern: get relevant past experiences"""
        return self.memory.search(
            query=f"similar to {current_situation}",
            filter_metadata={"workflow": self.__class__.__name__}
        )
```

---

## 4. Data Architecture (Core)

### Simplified Data Models

#### **Core Workflow Models**
```python
@dataclass
class WorkflowState:
    issue_id: str
    current_step: str
    context: Dict[str, Any]
    artifacts: List[str]
    human_approval_needed: bool = False
    next_workflows: List[str] = field(default_factory=list)

@dataclass
class WorkflowResult:
    success: bool
    state: WorkflowState
    outputs: Dict[str, Any]
    next_action: Optional[str] = None
    requires_security_review: bool = False
    has_code_changes: bool = False

@dataclass
class Issue:
    id: str
    title: str
    body: str
    labels: List[str]
    assignee: Optional[str]
    milestone: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class TeamContext:
    repository: str
    team_members: List[str]
    preferences: Dict[str, Any]
    workflow_settings: Dict[str, Any]

# Memory is handled entirely by Mem0 - no custom memory models needed
# LLM calls are handled entirely by OpenRouter - no custom LLM models needed
# Tools are simple function calls - no complex tool models needed
```

### Simple Memory Integration
```python
# Just use Mem0 directly - no wrapper complexity
class WorkflowWithMemory:
    def __init__(self, memory: Mem0Client, llm: OpenRouterClient):
        self.memory = memory
        self.llm = llm
    
    def analyze_with_context(self, issue: Issue) -> str:
        # Simple: get relevant memories
        context = self.memory.search(f"issues similar to {issue.title}")
        
        # Simple: make LLM call with context
        response = self.llm.complete([
            {"role": "system", "content": "You are a planning expert. Use past context to inform decisions."},
            {"role": "user", "content": f"Issue: {issue.title}\nContext: {context}\nAnalyze and plan."}
        ])
        
        # Simple: remember this interaction
        self.memory.add({
            "issue_id": issue.id,
            "analysis": response,
            "timestamp": datetime.now(),
            "outcome": "planned"  # Will be updated later
        })
        
        return response
```

### Simple Extension Pattern

#### **Adding New Workflows - Just Inherit and Implement**
```python
# Want a security workflow? Just create it!
class SecurityWorkflow(BaseWorkflow):
    def _build_graph(self) -> StateGraph:
        return StateGraph({
            "scan_vulnerabilities": self.scan_vulnerabilities,
            "check_dependencies": self.check_dependencies,
            "create_report": self.create_security_report
        })
    
    def scan_vulnerabilities(self, state: Dict) -> Dict:
        # Get security context from memory
        context = self.memory.search("security vulnerabilities in similar projects")
        
        # Use LLM to analyze code
        analysis = self.llm.complete([
            {"role": "system", "content": "You are a security expert. Analyze code for vulnerabilities."},
            {"role": "user", "content": f"Code: {state['code']}\nContext: {context}"}
        ])
        
        # Remember this analysis
        self.memory.add({
            "type": "security_scan",
            "code_files": state['code_files'],
            "findings": analysis,
            "timestamp": datetime.now()
        })
        
        return {"security_analysis": analysis, **state}

# Want a documentation workflow? Just create it!
class DocumentationWorkflow(BaseWorkflow):
    def _build_graph(self) -> StateGraph:
        return StateGraph({
            "analyze_code": self.analyze_code_structure,
            "generate_docs": self.generate_documentation,
            "review_docs": self.review_documentation
        })

# Want a custom domain workflow? Just create it!
class FinanceWorkflow(BaseWorkflow):
    def _build_graph(self) -> StateGraph:
        return StateGraph({
            "check_compliance": self.check_financial_compliance,
            "validate_calculations": self.validate_financial_calculations,
            "generate_audit_trail": self.generate_audit_trail
        })

# Usage is simple - just instantiate what you need
platform = AutonomyPlatform()
orchestrator = MasterOrchestrator(platform)

# Add any workflow you want
orchestrator.security = platform.create_workflow(SecurityWorkflow)
orchestrator.documentation = platform.create_workflow(DocumentationWorkflow)
orchestrator.finance = platform.create_workflow(FinanceWorkflow)
```

---

## 5. Integration Patterns (Core)

### GitHub Projects v2 Integration
```python
class ProjectsV2Manager:
    def __init__(self):
        self.graphql_client = GraphQLClient()
        self.field_cache = FieldCache()
    
    def bootstrap_project(self, repo: Repository):
        # Create required fields: Priority, Pinned, Sprint, Track
        fields = {
            "Priority": self.create_single_select_field(["P0", "P1", "P2", "P3"]),
            "Pinned": self.create_boolean_field(),
            "Sprint": self.create_iteration_field(),
            "Track": self.create_text_field()
        }
        
        # Cache field IDs for performance
        self.field_cache.store(repo.id, fields)
        return fields
```

### Simple Tool Integration
```python
# Just simple tool classes - no complex registry
class GitHubTools:
    def __init__(self, github_token: str):
        self.client = GitHubClient(github_token)
    
    def get_issue(self, issue_id: str) -> Issue:
        return self.client.get_issue(issue_id)
    
    def update_issue(self, issue_id: str, **updates) -> Issue:
        return self.client.update_issue(issue_id, **updates)
    
    def create_pr(self, title: str, body: str, head: str, base: str) -> PullRequest:
        return self.client.create_pr(title, body, head, base)

class SlackTools:
    def __init__(self, slack_token: str):
        self.client = SlackClient(slack_token)
    
    def send_message(self, channel: str, message: str):
        return self.client.send_message(channel, message)
    
    def notify_team(self, team: str, message: str):
        return self.client.notify_team(team, message)

# Workflows just use tools directly - simple and clear
class PlanningWorkflow(BaseWorkflow):
    def create_plan_pr(self, state: Dict) -> Dict:
        # Create PR with plan
        pr = self.github.create_pr(
            title=f"Plan for issue #{state['issue_id']}",
            body=state['plan_content'],
            head="plan-branch",
            base="main"
        )
        
        # Notify team
        self.slack.notify_team(
            team="planning",
            message=f"New plan ready for review: {pr.url}"
        )
        
        return {"pr_created": pr.url, **state}
```

---

## 6. Development Guidelines (Core)

### Code Organization
```
src/
├── agents/                    # AI agent implementations
│   ├── base.py               # Base agent interface
│   ├── planning.py           # Planning agent
│   ├── pm.py                 # PM agent
│   ├── sde.py                # SDE agent
│   └── qa.py                 # QA agent
├── memory/                   # Memory system
│   ├── mem0_client.py        # Mem0 integration
│   ├── graph_store.py        # Graph relationships
│   └── context_builder.py    # Context aggregation
├── llm/                      # LLM integration
│   ├── openrouter.py         # OpenRouter client
│   ├── model_selector.py     # Model selection logic
│   └── fallback.py           # Fallback strategies
├── workflows/                # LangGraph workflows
│   ├── planning.py           # Planning workflow
│   ├── execution.py          # Task execution
│   └── verification.py       # Outcome verification
├── tools/                    # Tool implementations
│   ├── registry.py           # Tool registry
│   ├── github.py             # GitHub tools
│   └── slack.py              # Slack tools
└── core/                     # Core infrastructure
    ├── config.py             # Configuration
    ├── auth.py               # Authentication
    └── audit.py              # Audit logging
```

### Design Patterns

#### **Agent Factory Pattern**
```python
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str, config: AgentConfig) -> Agent:
        if agent_type == "planning":
            return PlanningAgent(config)
        elif agent_type == "human":
            return HumanAgent(config)
        # ... other agent types
```

#### **Memory-First Development**
```python
# Always consider memory in agent decisions
class MemoryAwareAgent(BaseAgent):
    def process_request(self, request: Request) -> Response:
        # 1. Retrieve relevant memories
        memories = self.memory.get_context(request)
        
        # 2. Enrich request with memories
        enriched_request = self.enrich_with_memory(request, memories)
        
        # 3. Process and remember outcome
        response = self.process_enriched_request(enriched_request)
        self.memory.remember_interaction(request, response)
        
        return response
```

#### **Tool-First Integration**
```python
# All external interactions through tool registry
class AgentToolUser:
    def __init__(self, tool_registry: ToolRegistry):
        self.tools = tool_registry
    
    def update_github_issue(self, issue_id: str, updates: Dict):
        return self.tools.execute_tool(
            "github_update_issue",
            agent=self,
            params={"issue_id": issue_id, "updates": updates}
        )
```

### Quality Standards

#### **Agent Quality Guidelines**
- **Explainable Decisions**: All AI decisions must include reasoning
- **Memory Integration**: Agents should learn from past interactions
- **Human Respect**: AI suggestions, human decisions for critical paths
- **Error Recovery**: Graceful handling of LLM failures and tool errors

#### **Memory Guidelines**
- **Privacy**: Sensitive information should not be stored in memory
- **Accuracy**: Memory updates should be validated for correctness
- **Relevance**: Only store information that improves future decisions
- **Cleanup**: Implement memory cleanup for outdated information

#### **Tool Guidelines**
- **Permission Checks**: All tool usage must be permission-validated
- **Audit Logging**: Complete audit trail for all tool interactions
- **Error Handling**: Robust error handling with meaningful messages
- **Testing**: Mock tool interactions for reliable testing

---

## 7. Security & Compliance (Core)

### Security Architecture
```python
class SecurityManager:
    def __init__(self):
        self.permission_manager = PermissionManager()
        self.audit_logger = AuditLogger()
        self.secret_manager = SecretManager()
    
    def validate_agent_action(self, agent: Agent, action: Action) -> bool:
        # Check agent permissions
        if not self.permission_manager.can_perform(agent, action):
            return False
        
        # Log attempted action
        self.audit_logger.log_action_attempt(agent, action)
        return True
```

### Compliance Features
- **Complete Audit Trail**: All agent interactions logged with timestamps
- **Permission Management**: Role-based access control for tools and actions
- **Data Privacy**: Memory system respects data privacy requirements
- **Reversible Actions**: All automated changes can be undone

---

## 8. Testing Strategy (Core)

### Test Architecture
```
Tests/
├── unit/                     # Individual component tests
│   ├── test_agents.py        # Agent behavior tests
│   ├── test_memory.py        # Memory system tests
│   └── test_tools.py         # Tool functionality tests
├── integration/              # Component interaction tests
│   ├── test_workflows.py     # LangGraph workflow tests
│   ├── test_github_api.py    # GitHub integration tests
│   └── test_memory_llm.py    # Memory + LLM integration tests
└── e2e/                      # End-to-end workflow tests
    ├── test_planning_flow.py # Complete planning workflows
    └── test_team_collaboration.py # Team collaboration scenarios
```

### Testing Guidelines
- **Mock LLM Responses**: Use deterministic responses for reproducible tests
- **Memory Isolation**: Each test gets isolated memory context
- **Permission Testing**: Verify all permission checks work correctly
- **Error Scenarios**: Test graceful degradation and error handling

---

## 9. Performance & Scalability (Core)

### Performance Targets
- **CLI Response Time**: < 2 seconds for most operations
- **Memory Retrieval**: < 500ms for context building
- **LLM Calls**: < 10 seconds for complex reasoning
- **GitHub API**: Respect rate limits with intelligent caching

### Scalability Considerations
- **Memory Growth**: Implement memory cleanup strategies
- **LLM Costs**: Model selection based on task complexity
- **GitHub API**: Batch operations and intelligent caching
- **Team Size**: Architecture supports teams of 2-50 members

---

## 10. Deployment & Operations (Core)

### Development Environment
```bash
# Setup development environment
git clone https://github.com/mehulbhardwaj/autonomy.git
cd autonomy
pip install -e .[dev]

# Configure environment
export GITHUB_TOKEN="your_token"
export OPENROUTER_API_KEY="your_key"
export MEM0_API_KEY="your_key"  # Optional for local deployment

# Run development server
autonomy serve --dev
```

### Production Deployment
- **Package Distribution**: `pipx install autonomy` for global CLI
- **Configuration**: Environment-based configuration with validation
- **Monitoring**: Structured logging with metrics collection
- **Updates**: Automated update notifications with changelog

---

## 11. See Also
- The pro repo will contain a separate TECH doc for proprietary/enterprise features.

---

*This TECH doc is for the open source, GPLv3-licensed core only. For advanced, enterprise, and SaaS features, see the future pro TECH doc.*