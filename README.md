# Autonomy MCP

**Enable human-AI collaboration in software development with the Generate-Verify loop.**

Autonomy MCP implements a structured workflow for AI-assisted software development, following the principles outlined in [Writing Software in English](https://mehulbhardwaj.substack.com/p/building-software-in-english). It addresses the core challenge that **human review is the bottleneck** by pushing verification burden onto tests and bots before human review.

## 🎯 Overview

The Generate-Verify loop enables autonomous software development with human oversight:

1. **PM-agent**: Requirements → Design → Test Plan
2. **SDE-agent**: Implementation → Initial Testing  
3. **QA-agent**: Comprehensive Testing → Hardening
4. **Human**: Code Review → Approval → Merge

## 🚀 Key Features

- **🤖 Agent Specialization**: PM, SDE, and QA agents with specific roles and prompts
- **🔄 Generate-Verify Loop**: Structured workflow with human gates
- **📋 GitHub Integration**: Native Issues, Labels, Milestones, and Actions support
- **📚 Living Documentation**: Markdown-based memory system (PRD.md, TECH.md, TEST.md)
- **🎛️ Quality Constraints**: Enforced limits on file size, function complexity, and PR scope
- **🧪 Test-Driven Development**: Comprehensive test coverage requirements and automation
- **🔧 Context Control**: Small repos, bounded scope, controlled complexity
- **👥 Human Oversight**: Approval gates and branch protection

## 📦 Installation

```bash
pip install autonomy-mcp
```

## 🛠️ Quick Start

### 1. Setup GitHub Token
```bash
export GITHUB_TOKEN="your_github_personal_access_token"
```

### 2. Initialize a Repository
```bash
# Setup existing repository
autonomy-mcp init --owner myorg --repo myproject

# Or initialize new project with template
autonomy-mcp init --owner myorg --repo myproject --template api
```

### 3. Process Issues
```bash
# Process an issue through the complete Generate-Verify loop
autonomy-mcp process --owner myorg --repo myproject --issue 42

# Run specific phase only
autonomy-mcp process --owner myorg --repo myproject --issue 42 --phase pm
```

### 4. Check Status
```bash
# Repository status
autonomy-mcp status --owner myorg --repo myproject

# Specific issue status
autonomy-mcp status --owner myorg --repo myproject --issue 42
```

## 🏗️ Architecture

### Core Components

```python
from src import WorkflowManager, WorkflowConfig

# Initialize with configuration
config = WorkflowConfig(
    max_file_lines=300,
    max_function_lines=40,
    test_coverage_target=0.75,
    autonomy_level="supervised"
)

manager = WorkflowManager(
    github_token="your_token",
    owner="myorg", 
    repo="myproject",
    config=config
)

# Setup repository
manager.setup_repository()

# Process issue through Generate-Verify loop
result = manager.process_issue(issue_number=42)
```

### Agent Roles

#### PM-Agent (Product Manager)
- **Input**: GitHub issue description
- **Output**: Requirements document, system design, test plan
- **Focus**: User experience, business value, technical feasibility
- **Model**: GPT-4 (configurable)

#### SDE-Agent (Software Development Engineer)  
- **Input**: Requirements and design documents
- **Output**: Implementation, unit tests, documentation
- **Focus**: Code quality, maintainability, performance
- **Model**: Claude-3-Sonnet (configurable)

#### QA-Agent (Quality Assurance)
- **Input**: Implementation and test plan
- **Output**: Comprehensive test suite, coverage analysis, feedback
- **Focus**: Edge cases, error handling, regression prevention
- **Model**: GPT-4 (configurable)

## 📋 Workflow Process

### Issue Lifecycle

1. **Created** → `needs-requirements`
2. **PM-agent** → `needs-development` 
3. **SDE-agent** → `needs-testing`
4. **QA-agent** → `needs-review`
5. **Human** → `approved` → **Merged**

### Labels System

The package creates standardized labels:

**Issue Types**: `epic`, `feature`, `task`, `bug`, `documentation`, `enhancement`, `devops`

**Agent Roles**: `pm-agent`, `sde-agent`, `qa-agent`

**Workflow States**: `needs-requirements`, `needs-design`, `in-development`, `needs-testing`, `needs-review`, `approved`, `blocked`

**Priorities**: `priority-critical`, `priority-high`, `priority-medium`, `priority-low`

## 🎛️ Configuration

```python
from autonomy_mcp import WorkflowConfig

config = WorkflowConfig(
    # Code quality constraints
    max_file_lines=300,
    max_function_lines=40,
    max_pr_lines=500,
    
    # Testing requirements
    test_coverage_target=0.75,
    require_integration_tests=True,
    require_unit_tests=True,
    
    # Agent models
    pm_agent_model="gpt-4",
    sde_agent_model="claude-3-sonnet", 
    qa_agent_model="gpt-4",
    
    # Autonomy settings
    autonomy_level="supervised",  # supervised | semi-autonomous | autonomous
    require_human_approval=True,
    auto_merge_on_approval=True
)
```

## 🤖 GitHub Actions Integration

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
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Autonomy MCP
        run: pip install autonomy-mcp
      
      - name: Process Issue
        run: |
          autonomy-mcp process \
            --owner ${{ github.repository_owner }} \
            --repo ${{ github.event.repository.name }} \
            --issue ${{ github.event.issue.number }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 📚 Documentation

- **[Usage Guide](docs/USAGE_GUIDE.md)**: Complete setup and usage instructions
- **[MCP Integration](docs/MCP_SETUP.md)**: GitHub MCP server setup
- **[Examples](examples/)**: Project templates and use cases
- **[API Reference](docs/API.md)**: Complete API documentation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/mehulbhardwaj/autonomy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mehulbhardwaj/autonomy/discussions)
- **Documentation**: [Wiki](https://github.com/mehulbhardwaj/autonomy/wiki)

## 🗺️ Roadmap

- [ ] **v0.2.0**: LLM Integration (OpenAI, Anthropic, Local models)
- [ ] **v0.3.0**: GitHub Copilot integration
- [ ] **v0.4.0**: Playwright MCP for UI testing
- [ ] **v0.5.0**: Multi-repository workflow support
- [ ] **v1.0.0**: Production-ready with full automation

---

**Built with ❤️ for autonomous software development**

*Inspired by [Writing Software in English](https://mehulbhardwaj.substack.com/p/building-software-in-english)*
