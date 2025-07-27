# Autonomy Planning Agent – Technical Architecture (Core)

**Version:** 2.0   |   **Target:** Simple CLI Tool for Team Collaboration   |   **Design Principle:** Human + AI Collaboration

---

## 1. Vision & Principles

### Core Vision
**Simple CLI tool enabling humans + AI to collaborate for knowledge work**, specifically focused on intelligent GitHub project planning and task coordination.

### Guiding Principles
1. **Human + AI Collaboration** – AI agents augment human decision-making, don't replace it
2. **Memory-Driven Intelligence** – Agents learn from past interactions and team patterns
3. **Simple Workflow Management** – Basic workflow orchestration without over-engineering
4. **GitHub-Native Integration** – Leverage Projects v2, Issues, and native workflows
5. **Transparency & Auditability** – All AI decisions explainable and reversible

---

## 2. Architectural Overview (Core)

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐
│   CLI Client    │    │   Slack Bot     │
│   (Click)       │    │   (Webhooks)    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Workflow Engine │
                    │   (Simple Dict)  │
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
| **Workflow Engine** | Simple Dict-based | Lightweight workflow orchestration |
| **LLM Integration** | OpenRouter | Unified access to 400+ models with fallback capabilities |
| **Memory System** | Mem0 | Simple in-memory store with basic search |
| **CLI Framework** | Python Click | Professional CLI with rich output |
| **GitHub Integration** | GraphQL + REST | Projects v2 for advanced features, REST for simple ops |
| **Slack Integration** | Slack Web API | Team communication and notifications |
| **Secret Management** | OS Keychain + Fernet | Native security with encrypted fallback |

---

## 3. Simplified Workflow Architecture (Core)

### Core Design Philosophy

**Keep it Simple**: Simple dict-based workflows + Mem0 + OpenRouter provides everything we need without over-engineering. Focus on elegant composition over complex abstraction.

#### **Simple Workflow Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    Simple Workflows                        │
│            (Dict-based step execution)                     │
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

### Core Planning Workflow (Out of the Box)

The **Planning Workflow** is the foundational organizational intelligence that ships with the platform.

#### **Planning Workflow Core Responsibilities**
```python
class PlanningWorkflow(BaseWorkflow):
    """Simplified planning workflow with dict-based steps."""
    
    def _build_graph(self):
        return {
            "analyze_issue": self.analyze_issue,
            "rank_priority": self.rank_priority,
            "decompose": self.decompose,
            "route": self.route,
            "assign": self.assign,
            "plan": self.plan,
            "get_approval": self.get_human_approval,
            "approve": self.approve,
        }
    
    def analyze_issue(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze issue using memory context and LLM."""
        title = state.get("title", "")
        repo = state.get("repository", "default")
        context = self.memory.search(
            f"similar:{title}", filter_metadata={"repository": repo}
        )
        prompt = f"Analyze {title}. Context: {context}"
        analysis = self.llm.complete_with_fallback(
            [{"role": "user", "content": prompt}],
            models=["openai/gpt-4o"],
            operation="analysis",
        )
        state["analysis"] = analysis or f"analysis of {title}"
        return state
```

### Simple Workflow Platform

**Simple Inheritance Model** - Users create new workflows by inheriting from `BaseWorkflow`
**Planning Workflow Orchestration** - New workflows integrate with Planning Workflow decisions  
**Repository Customization** - Each repo can tune the Planning Workflow's behavior

### Simple Workflow-Based Implementation

#### **Core Platform Pattern**
```python
class AutonomyPlatform:
    def __init__(self):
        # Shared foundation - simple and elegant
        self.memory = CachedMem0Client()
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
    def __init__(self, memory, llm, github, slack):
        self.memory = memory
        self.llm = llm  
        self.github = github
        self.slack = slack
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Override this to define workflow steps"""
        raise NotImplementedError

    def execute(self, state: Dict[str, Any]) -> WorkflowResult:
        current = state.copy()
        for step, func in self.graph.items():
            current = func(current)
        return WorkflowResult(success=True, state=WorkflowState(data=current))
```

### Memory System (Simplified)

```python
class Mem0Client:
    """Repository-scoped memory backed by mem0."""
    
    def __init__(self, max_entries: int = 50):
        self.max_entries = max_entries
        self.store: dict[str, OrderedDict[str, str]] = {}
    
    def search(self, query: str, filter_metadata: dict | None = None) -> str:
        """Return stored value filtered by repository."""
        repo = filter_metadata.get("repository") if filter_metadata else "default"
        return self.store.get(repo, {}).get(query, "")
    
    def add(self, data: dict[str, str]) -> bool:
        """Add data to repository-specific store with cleanup."""
        repository = data.pop("repository", "default")
        repo_store = self._get_repo_store(repository)
        for key, value in data.items():
            if len(repo_store) >= self.max_entries:
                repo_store.popitem(last=False)  # Remove oldest
            repo_store[key] = value
        return True
```

### LLM Integration (Simplified)

```python
class OpenRouterClient:
    """Simple OpenRouter API client with fallback."""
    
    def complete_with_fallback(
        self,
        messages: List[Dict[str, str]],
        models: List[str],
        operation: str = "default",
    ) -> str:
        """Try models in order until one works."""
        for model in models:
            try:
                return self.complete(messages, model=model, operation=operation)
            except OpenRouterError:
                continue
        raise OpenRouterError("All models failed")
```

---

## 4. Data Architecture (Core)

### Simplified Data Models

#### **Core Workflow Models**
```python
@dataclass
class WorkflowState:
    data: Dict[str, Any]

@dataclass
class WorkflowResult:
    success: bool
    state: WorkflowState

# Memory is handled by simple Mem0Client
# LLM calls are handled by OpenRouterClient
# Tools are simple function calls
```

### Simple Memory Integration
```python
class WorkflowWithMemory:
    def __init__(self, memory: Mem0Client, llm: OpenRouterClient):
        self.memory = memory
        self.llm = llm
    
    def analyze_with_context(self, issue: Dict) -> str:
        # Simple: get relevant memories
        context = self.memory.search(f"issues similar to {issue['title']}")
        
        # Simple: make LLM call with context
        response = self.llm.complete_with_fallback(
            [{"role": "user", "content": f"Issue: {issue['title']}\nContext: {context}\nAnalyze and plan."}],
            models=["openai/gpt-4o"]
        )
        
        # Simple: remember this interaction
        self.memory.add({
            "issue_id": issue.get("id"),
            "analysis": response,
            "repository": issue.get("repository", "default"),
        })
        
        return response
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
    def __init__(self, issue_manager):
        self.issue_manager = issue_manager
    
    def get_issue(self, issue_id: str) -> Dict:
        return self.issue_manager.get_issue(issue_id)
    
    def update_issue(self, issue_id: str, **updates) -> Dict:
        return self.issue_manager.update_issue(issue_id, **updates)

class SlackTools:
    def __init__(self, slack_bot):
        self.slack_bot = slack_bot
    
    def send_message(self, channel: str, message: str):
        return self.slack_bot.send_message(channel, message)
```
### API Endpoints & Webhook Integration
Autonomy interacts with GitHub and Slack using a small set of endpoints:

- **GitHub GraphQL** – Projects v2 field creation, board ranking, hierarchy sync
- **GitHub REST** – Issue updates, status checks, and pull request management
- **Slack Web API** – Posting digests and undo confirmations

Webhook listeners capture manual overrides and mirror them into the planning engine. Use the `overrides` webhook endpoint to track field edits and card drags.


---

## 6. Development Guidelines (Core)

### Code Organization
```
src/
├── core/                     # Core infrastructure
│   ├── platform.py          # Shared platform foundation
│   ├── workflow.py          # Base workflow classes
│   ├── models.py            # Data models
│   └── config.py            # Configuration
├── planning/                # Planning workflows
│   ├── workflow.py          # Planning workflow
│   ├── langgraph_workflow.py # LangGraph version (optional)
│   └── config.py            # Planning configuration
├── llm/                     # LLM integration
│   └── openrouter.py        # OpenRouter client
├── tools/                   # Tool implementations
│   ├── github.py            # GitHub tools
│   └── slack.py             # Slack tools
└── cli/                     # CLI interface
    └── main.py              # Main CLI entry point
```

### Design Patterns

#### **Simple Workflow Pattern**
```python
class SimpleWorkflow(BaseWorkflow):
    def _build_graph(self):
        return {
            "step1": self.step1,
            "step2": self.step2,
            "step3": self.step3,
        }
    
    def step1(self, state: Dict) -> Dict:
        # Process state
        return state
```

#### **Memory-First Development**
```python
# Always consider memory in workflow decisions
class MemoryAwareWorkflow(BaseWorkflow):
    def analyze_issue(self, state: Dict) -> Dict:
        # 1. Retrieve relevant memories
        context = self.memory.search(f"similar:{state['title']}")
        
        # 2. Process with LLM
        analysis = self.llm.complete_with_fallback(
            [{"role": "user", "content": f"Analyze: {state['title']}\nContext: {context}"}],
            models=["openai/gpt-4o"]
        )
        
        # 3. Remember outcome
        self.memory.add({
            "analysis": analysis,
            "repository": state.get("repository", "default"),
        })
        
        return {"analysis": analysis, **state}
```

---

## 7. Security & Compliance (Core)

### Security Architecture
```python
class SecurityManager:
    def __init__(self):
        self.audit_logger = AuditLogger()
        self.secret_vault = SecretVault()
    
    def validate_action(self, action: Action) -> bool:
        # Log attempted action
        self.audit_logger.log_action_attempt(action)
        return True
```

### Compliance Features
- **Complete Audit Trail**: All workflow interactions logged with timestamps
- **Permission Management**: Basic permission checks for tools and actions
- **Data Privacy**: Memory system respects data privacy requirements
- **Reversible Actions**: All automated changes can be undone
- **Undo System**: Each change produces a diff hash and can be reverted via the `/api/undo` endpoint or `autonomy undo` command.

---

## 8. Testing Strategy (Core)

### Test Architecture
```
tests/
├── unit/                     # Individual component tests
│   ├── test_workflows.py     # Workflow behavior tests
│   ├── test_memory.py        # Memory system tests
│   └── test_tools.py         # Tool functionality tests
├── integration/              # Component interaction tests
│   ├── test_github_api.py    # GitHub integration tests
│   └── test_memory_llm.py    # Memory + LLM integration tests
└── e2e/                      # End-to-end workflow tests
    └── test_planning_flow.py # Complete planning workflows
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

# Run development server
autonomy --help
```

### Production Deployment
- **Package Distribution**: `pipx install autonomy` for global CLI
- **Configuration**: Environment-based configuration with validation
- **Monitoring**: Structured logging with metrics collection
- **Updates**: Automated update notifications with changelog

---

*This TECH doc covers the open source, GPLv3-or-later licensed core only. The implementation is intentionally simple and focused on providing immediate value for team coordination.*
