# Autonomy MCP - Package Summary

## 🎯 Overview

Autonomy MCP is a standalone Python package that implements the Generate-Verify loop workflow for AI-assisted software development, as outlined in the "Writing Software in English" blog post by Mehul Bhardwaj.

## 📦 Package Structure

```
autonomy-mcp/
├── autonomy_mcp/              # Main package
│   ├── __init__.py           # Package exports and convenience functions
│   ├── core/                 # Core workflow components
│   │   ├── workflow_manager.py  # Main WorkflowManager class
│   │   ├── config.py           # WorkflowConfig dataclass
│   │   └── agents.py           # PM, SDE, QA agent classes
│   ├── github/               # GitHub integration
│   │   └── issue_manager.py    # GitHub API wrapper
│   ├── planning/             # Task planning and templates
│   │   └── plan_manager.py     # PlanManager with templates
│   ├── cli/                  # Command-line interface
│   │   └── main.py            # CLI implementation
│   └── templates/            # Project templates
├── tests/                    # Test suite
│   └── test_autonomy_mcp.py   # Comprehensive tests
├── docs/                     # Documentation
│   └── USAGE_GUIDE.md        # Complete usage guide
├── examples/                 # Usage examples
│   ├── basic_usage.py        # Python usage examples
│   └── autonomy.json         # Configuration example
├── scripts/                  # Utility scripts
│   └── extract_to_repo.sh    # Extraction script
├── README.md                 # Main documentation
├── CHANGELOG.md             # Version history
├── LICENSE                  # MIT license
└── pyproject.toml           # Package configuration
```

## 🚀 Key Features

### Generate-Verify Loop
- **PM-agent**: Requirements → Design → Test Plan
- **SDE-agent**: Implementation → Initial Testing
- **QA-agent**: Comprehensive Testing → Hardening
- **Human**: Code Review → Approval → Merge

### Agent Specialization
- Role-specific system prompts and behaviors
- Configurable LLM models (GPT-4, Claude-3-Sonnet)
- Temperature and token limit controls

### GitHub Integration
- Native Issues, Labels, Milestones, and Actions support
- Automated workflow state management
- Branch protection and approval gates

### Quality Constraints
- File size limits (default: 300 lines)
- Function complexity limits (default: 40 lines)
- PR scope limits (default: 500 lines)
- Test coverage requirements (default: 75%)

### Template System
- Pre-built templates: basic, api, web, cli
- Custom template support
- JSON-based task planning

### CLI Interface
```bash
autonomy-mcp init --owner myorg --repo myproject
autonomy-mcp process --owner myorg --repo myproject --issue 42
autonomy-mcp status --owner myorg --repo myproject
```

## 🔧 Configuration

### Basic Configuration
```python
from autonomy_mcp import WorkflowConfig

config = WorkflowConfig(
    max_file_lines=300,
    max_function_lines=40,
    test_coverage_target=0.75,
    autonomy_level="supervised"
)
```

### Advanced Configuration
```python
config = WorkflowConfig(
    pm_agent_model="gpt-4",
    sde_agent_model="claude-3-sonnet",
    qa_agent_model="gpt-4",
    require_human_approval=True,
    enable_branch_protection=True
)
```

## 📋 Usage Patterns

### Quick Setup
```python
from autonomy_mcp import quick_setup

manager = quick_setup(
    github_token="ghp_...",
    owner="myorg",
    repo="myproject",
    template="api"
)
```

### Issue Processing
```python
from autonomy_mcp import WorkflowManager

manager = WorkflowManager(...)

# Process single issue
result = manager.process_issue(issue_number=42)

# Process all ready issues
results = manager.process_ready_issues()

# Phase-specific processing
pm_result = manager.process_issue(42, phase="pm")
```

### Plan Management
```python
from autonomy_mcp.planning import PlanManager

manager = PlanManager()
plan = manager.create_plan_template("api")
manager.save_plan(plan, "my_plan.json")
```

## 🧪 Testing

### Test Coverage
- Unit tests for all core components
- Integration tests for GitHub API
- Mock-based testing for external dependencies
- 80%+ test coverage requirement

### Running Tests
```bash
pip install -e .[dev]
pytest
pytest --cov=autonomy_mcp --cov-report=html
```

## 📚 Documentation

### Complete Documentation Set
- **README.md**: Installation and quick start
- **USAGE_GUIDE.md**: Comprehensive usage patterns
- **CHANGELOG.md**: Version history and release notes
- **examples/**: Python usage examples and configurations

### API Documentation
- Docstrings for all public methods
- Type hints throughout codebase
- Configuration reference

## 🔄 GitHub Actions Integration

### Basic Workflow
```yaml
name: Autonomy Generate-Verify Loop
on:
  issues:
    types: [opened, labeled, assigned]
jobs:
  process-issue:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Autonomy MCP
        run: pip install autonomy-mcp
      - name: Process Issue
        run: autonomy-mcp process --owner ${{ github.repository_owner }} --repo ${{ github.event.repository.name }} --issue ${{ github.event.issue.number }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🎛️ Autonomy Levels

### Supervised (Default)
- Human approval required for all phases
- Maximum safety and control
- Ideal for critical projects

### Semi-Autonomous
- Automatic PM and SDE phases
- Human approval for QA and merge
- Balanced automation and oversight

### Autonomous
- Full automation with human monitoring
- Automatic merge on approval
- Maximum efficiency for trusted workflows

## 📈 Roadmap

### v0.2.0 - LLM Integration
- OpenAI and Anthropic API integration
- Local model support (Ollama, etc.)
- Custom model configurations

### v0.3.0 - Advanced Features
- GitHub Copilot integration
- Multi-repository workflow support
- Advanced agent customization

### v0.4.0 - UI Testing
- Playwright MCP integration
- E2E testing automation
- Visual regression testing

### v1.0.0 - Production Ready
- Enterprise features
- Advanced monitoring and analytics
- Full automation capabilities

## 🚢 Deployment Options

### PyPI Package
```bash
pip install autonomy-mcp
```

### GitHub Actions
- Pre-built workflows
- Custom action support
- Enterprise GitHub integration

### Self-Hosted
- Docker containers
- Kubernetes deployments
- Private cloud support

## 🤝 Integration Points

### Existing Tools
- GitHub (native)
- Jira/Linear (via webhooks)
- Slack/Discord (notifications)
- CI/CD pipelines (GitHub Actions, etc.)

### Development Workflow
- Works with existing git workflows
- Respects branch protection rules
- Integrates with code review processes

## 💡 Best Practices

### Repository Structure
```
project/
├── docs/
│   ├── PRD.md      # Product Requirements
│   ├── TECH.md     # Technical Design
│   └── TEST.md     # Test Plan
├── src/            # Source code
├── tests/          # Test files
└── autonomy.json   # Configuration
```

### Issue Management
- Use standardized labels
- Create clear acceptance criteria
- Assign story points
- Define agent roles

### Quality Gates
- Enforce file size limits
- Require test coverage
- Use branch protection
- Mandate human approval

## 🔒 Security Considerations

### GitHub Token
- Use fine-grained personal access tokens
- Limit repository scope
- Rotate tokens regularly

### Branch Protection
- Require status checks
- Enforce review requirements
- Restrict push access

### Agent Prompts
- Review system prompts
- Validate agent outputs
- Monitor for prompt injection

## 📊 Success Metrics

### Development Efficiency
- 50% reduction in feature delivery time
- 60% reduction in review cycle time
- 80% reduction in bug escape rate

### Code Quality
- Consistent test coverage >75%
- Reduced technical debt
- Improved documentation quality

### Team Productivity
- More time for creative work
- Reduced context switching
- Improved work-life balance

---

## 🎉 Getting Started

1. **Install the package**:
   ```bash
   pip install autonomy-mcp
   ```

2. **Set up GitHub token**:
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

3. **Initialize repository**:
   ```bash
   autonomy-mcp init --owner myorg --repo myproject
   ```

4. **Process your first issue**:
   ```bash
   autonomy-mcp process --owner myorg --repo myproject --issue 1
   ```

5. **Watch the Generate-Verify loop in action**! 🚀

---

**Built with ❤️ for autonomous software development**

*Inspired by [Writing Software in English](https://mehulbhardwaj.substack.com/p/building-software-in-english)*
