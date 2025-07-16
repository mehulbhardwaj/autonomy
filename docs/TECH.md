# Autonomy Planning Agent – Technical Architecture

**Version:** 1.0   |   **Target:** GitHub-native Planning Layer   |   **Design Principle:** Simple, modular, incremental

---
## 1  Guiding Principles
1. **GitHub-native** – use Projects v2, Issues, and native UI workflows
2. **Start simple** – minimal viable architecture, add complexity only when needed
3. **Modular design** – clean interfaces, composable components
4. **Incremental growth** – each phase builds on previous without rewrites
5. **Transparency first** – all operations auditable and reversible

---
## 2  Core Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Client    │    │   Slack Bot     │    │   Web UI        │
│   (Click)       │    │   (Webhook)     │    │   (Future)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Planning API   │
                    │   (FastAPI)     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  GitHub Client  │    │  Task Engine    │    │  Config Store   │
│  (REST+GraphQL) │    │   (Ranking)     │    │   (Files)       │
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

### Phase 0-1 Stack (Simple Start)
| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Distribution** | pipx + PyPI | Professional Python package distribution |
| **CLI** | Python Click | Simple, composable commands |
| **API** | FastAPI | Async, type hints, auto docs |
| **GitHub Auth** | Device-Flow OAuth | Better UX than manual PAT entry |
| **GitHub** | httpx + GraphQL | REST for simple ops, GraphQL for Projects v2 |
| **Slack** | Slack Web API + Webhooks | Slash commands, notifications, OAuth |
| **Config** | Local files + Pydantic | No database complexity initially |
| **Secrets** | OS keychain + file fallback | Native OS security, no external deps |
| **Deployment** | Single Python process | Minimal operational overhead |

---
## 3  Module Structure & Interfaces

### Core Abstractions
```python
# GitHub API Client - unified interface
class GitHubClient:
    def __init__(self, token: str):
        self.rest = RESTClient(token)
        self.graphql = GraphQLClient(token)
    
    # Issues
    def get_issue(self, number: int) -> Issue
    def update_issue(self, number: int, **kwargs) -> Issue
    
    # Projects v2
    def get_project_items(self, project_id: str) -> List[ProjectItem]
    def reorder_item(self, item_id: str, after_id: str = None) -> bool
    def update_item_field(self, item_id: str, field_id: str, value: Any) -> bool

# Task Management - simple and focused
class TaskManager:
    def __init__(self, github_client: GitHubClient):
        self.github = github_client
        self.ranking = RankingEngine()
    
    def get_next_task(self, assignee: str = None) -> Optional[Task]
    def update_task(self, task_id: str, **updates) -> bool
    def list_tasks(self, **filters) -> List[Task]

# Ranking Engine - extensible scoring
class RankingEngine:
    def __init__(self, config: RankingConfig):
        self.config = config
    
    def score_task(self, task: Task, context: RankingContext) -> float
    def rank_tasks(self, tasks: List[Task]) -> List[Task]
    def explain_ranking(self, task: Task) -> str

# Slack Integration - commands and notifications
class SlackBot:
    def __init__(self, bot_token: str):
        self.client = SlackWebClient(token=bot_token)
    
    def handle_slash_command(self, command: str, args: Dict) -> SlackResponse
    def post_notification(self, channel: str, message: str) -> bool
    def send_interactive_message(self, channel: str, blocks: List) -> bool
```

### Module Organization
```
src/
├── core/
│   ├── config.py           # Configuration management
│   ├── secret_vault.py     # Encrypted credential storage
│   └── auth.py             # Authentication flows
├── github/
│   ├── client.py           # Unified GitHub client
│   ├── projects.py         # Projects v2 GraphQL operations
│   └── issues.py           # Issues REST operations
├── tasks/
│   ├── manager.py          # Task retrieval and updates
│   ├── ranking.py          # Priority scoring algorithms
│   └── hierarchy.py        # Issue hierarchy management
├── cli/
│   ├── main.py             # CLI entry point
│   └── commands/           # Command implementations
└── slack/
    ├── bot.py              # Slack bot implementation
    ├── commands.py         # Slash command handlers
    ├── notifications.py    # Notification formatting and sending
    └── oauth.py            # Slack OAuth flow
```

---
## 4  Data Models & Configuration

### Core Data Types
```python
@dataclass
class Task:
    id: str
    number: int
    title: str
    labels: List[str]
    assignee: Optional[str]
    priority: Optional[str]
    pinned: bool = False
    created_at: datetime
    updated_at: datetime

@dataclass
class RankingConfig:
    weights: Dict[str, float] = field(default_factory=lambda: {
        'priority_field': 5,
        'sprint_proximity': 3,
        'issue_age': 1,
        'blocked_penalty': -100
    })
    excluded_labels: List[str] = field(default_factory=lambda: ['blocked'])
    priority_mapping: Dict[str, int] = field(default_factory=lambda: {
        'P0': 4, 'P1': 3, 'P2': 2, 'P3': 1
    })
```

### Configuration Strategy
1. **Code defaults** - sensible out-of-the-box behavior
2. **Repository config** - `.autonomy/config.yaml` per repo
3. **User config** - `~/.autonomy/config.yaml` for personal settings
4. **Environment variables** - runtime overrides

---
## 5  Incremental Evolution Path

### Phase 0: Foundation (Weeks 1-2)
- **Instant CLI bootstrap**: `pipx install autonomy` → `autonomy init` → authenticated in <60s
- **Device-Flow OAuth**: Seamless GitHub authentication without manual PAT entry
- **OS-native secret storage**: Keychain integration with file fallback
- **Board bootstrap**: Automated Projects v2 field setup with caching
- **Slack Bot setup**: Basic OAuth and webhook infrastructure
- **Goal**: Professional distribution and frictionless onboarding

### Phase 1: Core Features (Weeks 3-6)
- Basic priority ranking system
- Task retrieval and updates
- Issue hierarchy management
- Simple audit trail
- **Goal**: Functional task management with transparency

### Phase 2: Intelligence (Weeks 7-10)
- Webhook-based override capture
- Multi-queue ranking engine
- Manual pin/unpin functionality
- Pattern recognition for overrides
- **Goal**: Smart automation with human oversight

### Phase 3+: Scale & Polish
- Database storage (when file storage isn't enough)
- Caching layer (when performance requires it)
- Monitoring & alerting (when operations require it)
- **Goal**: Production readiness without premature optimization

---
## 6  Performance & Scalability

### GitHub API Efficiency
- **Batch operations**: Group mutations to minimize API calls
- **Intelligent caching**: Cache field mappings and project metadata
- **Rate limit handling**: Exponential backoff with respect for limits
- **GraphQL optimization**: Use for complex queries, REST for simple ops

### Local Performance
- **Lazy loading**: Load expensive operations only when needed
- **Memory management**: Keep caches focused and bounded
- **Async operations**: Use FastAPI's async capabilities

---
## 7  Testing Strategy

### Test Pyramid
```
    ┌─────────────┐
    │   E2E Tests │  ← CLI workflows, GitHub integration
    │    (Few)    │
    └─────────────┘
           ▲
    ┌─────────────┐
    │ Integration │  ← GitHub API, ranking engine
    │   (Some)    │
    └─────────────┘
           ▲
    ┌─────────────┐
    │ Unit Tests  │  ← Individual functions, mocked APIs
    │   (Many)    │
    └─────────────┘
```

### Test Categories
- **Unit**: Mock GitHub API responses, test ranking logic
- **Integration**: Real GitHub API with test repositories
- **End-to-end**: Full CLI workflows and user scenarios

---
## 8  Security & Compliance

### Security Principles
- **Minimal permissions**: Use least-privilege PAT scopes
- **Credential encryption**: Fernet-based secret storage
- **Audit logging**: All operations logged with timestamps
- **No secret leakage**: Never log or expose credentials

### Compliance Readiness
- **Audit trail**: Complete operation history
- **Data retention**: Configurable log retention periods
- **Access controls**: Repository-level permissions respected
- **Encryption**: At-rest and in-transit encryption

---
## 9  Deployment & Operations

### Development
- **Local development**: Personal GitHub tokens, file-based config
- **Testing**: Pytest with mocked and real GitHub APIs
- **CI/CD**: GitHub Actions with comprehensive test matrix

### Production (Future)
- **Containerization**: Docker for consistent environments
- **Configuration**: Environment-specific config files
- **Monitoring**: Structured logging and metrics collection
- **Scaling**: Horizontal scaling when needed

---
## 10  Anti-Patterns to Avoid

### Over-Engineering
- ❌ Complex ranking algorithms without user validation
- ❌ Microservices before monolith is proven
- ❌ Database optimization before performance issues
- ❌ Custom UI before GitHub-native approach is exhausted

### Under-Engineering
- ❌ No error handling for GitHub API failures
- ❌ No audit trail for automated changes
- ❌ No configuration validation
- ❌ No transparency in ranking decisions

---
**Next Step:** Implement Phase 0 foundation with clean interfaces, then incrementally add intelligence while maintaining simplicity.
