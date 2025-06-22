# Autonomy MCP Usage Guide

This guide covers common usage patterns and scenarios for Autonomy MCP.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Repository Setup](#repository-setup)
- [Issue Processing](#issue-processing)
- [Agent Customization](#agent-customization)
- [Templates](#templates)
- [GitHub Actions Integration](#github-actions-integration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Installation

```bash
pip install autonomy-mcp
```

### 2. GitHub Token Setup

Create a GitHub Personal Access Token with the following permissions:
- `repo` (Full control of private repositories)
- `workflow` (Update GitHub Action workflows)

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

### 3. Initialize Repository

```bash
# For existing repository
autonomy-mcp init --owner myorg --repo myproject

# For new project with template
autonomy-mcp init --owner myorg --repo myproject --template api
```

### 4. Process Issues

```bash
# Process all ready issues
autonomy-mcp process --owner myorg --repo myproject

# Process specific issue
autonomy-mcp process --owner myorg --repo myproject --issue 42
```

## Configuration

### Basic Configuration

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
    
    # Autonomy level
    autonomy_level="supervised"  # supervised | semi-autonomous | autonomous
)
```

### Advanced Configuration

```python
config = WorkflowConfig(
    # Agent models
    pm_agent_model="gpt-4",
    sde_agent_model="claude-3-sonnet",
    qa_agent_model="gpt-4",
    
    # Workflow settings
    require_human_approval=True,
    auto_merge_on_approval=False,
    max_concurrent_issues=3,
    
    # Documentation requirements
    require_prd=True,
    require_tech_doc=True,
    require_test_plan=True,
    
    # Branch protection
    enable_branch_protection=True,
    required_status_checks=["ci", "tests", "lint"]
)
```

## Repository Setup

### Automatic Setup

```python
from autonomy_mcp import quick_setup

# Quick setup with defaults
manager = quick_setup(
    github_token="ghp_...",
    owner="myorg",
    repo="myproject",
    template="api"
)
```

### Manual Setup

```python
from autonomy_mcp import WorkflowManager, WorkflowConfig

config = WorkflowConfig(autonomy_level="supervised")
manager = WorkflowManager(
    github_token="ghp_...",
    owner="myorg",
    repo="myproject",
    config=config
)

# Setup repository structure
manager.setup_repository()

# Create labels and milestones
manager.setup_labels()
manager.setup_milestones()
```

## Issue Processing

### Process Single Issue

```python
from autonomy_mcp import WorkflowManager

manager = WorkflowManager(...)

# Process issue through complete Generate-Verify loop
result = manager.process_issue(issue_number=42)

print(f"Issue {result.issue_number} processed")
print(f"Status: {result.status}")
print(f"Phase: {result.current_phase}")
```

### Process Multiple Issues

```python
# Process all ready issues
results = manager.process_ready_issues()

for result in results:
    print(f"Issue #{result.issue_number}: {result.status}")
```

### Phase-Specific Processing

```python
# Run only PM phase
result = manager.process_issue(issue_number=42, phase="pm")

# Run SDE phase
result = manager.process_issue(issue_number=42, phase="sde")

# Run QA phase
result = manager.process_issue(issue_number=42, phase="qa")
```

## Agent Customization

### Custom Agent Prompts

```python
from autonomy_mcp.core.agents import PMAgent

class CustomPMAgent(PMAgent):
    def __init__(self, config):
        super().__init__(config)
        self.system_prompt = """
        You are a specialized PM agent for fintech applications.
        Focus on regulatory compliance and security requirements.
        
        Always consider:
        - PCI DSS compliance
        - GDPR requirements
        - Financial regulations
        - Security best practices
        """

# Use custom agent
manager.pm_agent = CustomPMAgent(config)
```

### Agent Configuration

```python
from autonomy_mcp import WorkflowConfig

config = WorkflowConfig(
    # Model selection
    pm_agent_model="gpt-4",
    sde_agent_model="claude-3-sonnet",
    qa_agent_model="gpt-4",
    
    # Agent behavior
    agent_temperature=0.1,
    agent_max_tokens=4000,
    agent_timeout=300
)
```

## Templates

### Using Built-in Templates

```python
from autonomy_mcp.planning import PlanManager

manager = PlanManager()

# Available templates: basic, api, web, cli
plan = manager.create_plan_template("api")

# Save template
manager.save_plan(plan, "my_api_plan.json")
```

### Custom Templates

```python
from autonomy_mcp.planning.plan_manager import TaskPlan

custom_plan = TaskPlan(
    name="ML Pipeline Project",
    description="Machine learning pipeline with MLOps",
    milestones=[
        {
            "title": "Data Pipeline",
            "description": "Data ingestion and preprocessing",
            "due_date": None,
            "state": "open"
        },
        {
            "title": "Model Training",
            "description": "ML model development and training",
            "due_date": None,
            "state": "open"
        }
    ],
    issues=[
        {
            "title": "Data Ingestion Setup",
            "body": "Set up data ingestion from various sources",
            "labels": ["epic", "pm-agent"],
            "milestone": "Data Pipeline",
            "story_points": 8
        }
    ]
)
```

## GitHub Actions Integration

### Basic Workflow

```yaml
name: Autonomy Generate-Verify Loop

on:
  issues:
    types: [opened, labeled, assigned]
  issue_comment:
    types: [created]

jobs:
  process-issue:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'needs-requirements') || 
        contains(github.event.issue.labels.*.name, 'needs-development') ||
        contains(github.event.issue.labels.*.name, 'needs-testing')
    
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

### Advanced Workflow with Matrix

```yaml
name: Autonomy Multi-Agent Processing

on:
  workflow_dispatch:
    inputs:
      issue_numbers:
        description: 'Comma-separated issue numbers'
        required: true

jobs:
  process-issues:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        issue: ${{ fromJson(github.event.inputs.issue_numbers) }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Process Issue ${{ matrix.issue }}
        run: |
          autonomy-mcp process \
            --owner ${{ github.repository_owner }} \
            --repo ${{ github.event.repository.name }} \
            --issue ${{ matrix.issue }} \
            --config config/autonomy.json
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## CLI Usage

### Basic Commands

```bash
# Initialize repository
autonomy-mcp init --owner myorg --repo myproject

# Process issues
autonomy-mcp process --owner myorg --repo myproject

# Check status
autonomy-mcp status --owner myorg --repo myproject

# Setup with custom config
autonomy-mcp init --owner myorg --repo myproject --config my-config.json
```

### Advanced CLI Usage

```bash
# Process specific phase only
autonomy-mcp process --owner myorg --repo myproject --issue 42 --phase pm

# Process with custom workspace
autonomy-mcp process --owner myorg --repo myproject --workspace /path/to/workspace

# Dry run mode
autonomy-mcp process --owner myorg --repo myproject --dry-run

# Verbose output
autonomy-mcp process --owner myorg --repo myproject --verbose

# Process multiple issues
autonomy-mcp process --owner myorg --repo myproject --issues 42,43,44
```

## Troubleshooting

### Common Issues

#### 1. GitHub API Rate Limits

```python
from autonomy_mcp import WorkflowConfig

config = WorkflowConfig(
    github_api_delay=1.0,  # Add delay between API calls
    max_retries=3,         # Retry failed requests
    backoff_factor=2       # Exponential backoff
)
```

#### 2. Agent Timeouts

```python
config = WorkflowConfig(
    agent_timeout=600,     # Increase timeout to 10 minutes
    agent_max_tokens=8000  # Increase token limit
)
```

#### 3. Branch Protection Issues

```bash
# Check branch protection status
autonomy-mcp status --owner myorg --repo myproject --check-protection

# Fix protection rules
autonomy-mcp init --owner myorg --repo myproject --fix-protection
```

### Debug Mode

```python
import logging
from autonomy_mcp import WorkflowManager

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

manager = WorkflowManager(...)
result = manager.process_issue(42)
```

### Environment Variables

```bash
# Required
export GITHUB_TOKEN="ghp_..."

# Optional
export AUTONOMY_LOG_LEVEL="DEBUG"
export AUTONOMY_WORKSPACE="/path/to/workspace"
export AUTONOMY_CONFIG_FILE="/path/to/config.json"

# Agent API keys (if using external LLMs)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."
```

## Best Practices

### 1. Repository Structure

```
project/
├── docs/
│   ├── PRD.md           # Product Requirements
│   ├── TECH.md          # Technical Design
│   └── TEST.md          # Test Plan
├── src/
│   └── ...              # Source code
├── tests/
│   └── ...              # Test files
├── .github/
│   └── workflows/       # GitHub Actions
└── autonomy.json        # Autonomy config
```

### 2. Issue Templates

Create issue templates in `.github/ISSUE_TEMPLATE/`:

```markdown
---
name: Feature Request
about: Request a new feature
title: '[FEATURE] '
labels: ['feature', 'needs-requirements']
assignees: ''
---

## Feature Description
Brief description of the feature

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Story Points
Estimated effort (1-13)

## Agent Assignment
- [ ] PM-agent for requirements
- [ ] SDE-agent for implementation  
- [ ] QA-agent for testing
```

### 3. Configuration Management

```json
{
  "max_file_lines": 300,
  "max_function_lines": 40,
  "test_coverage_target": 0.8,
  "autonomy_level": "supervised",
  "require_human_approval": true,
  "pm_agent_model": "gpt-4",
  "sde_agent_model": "claude-3-sonnet",
  "qa_agent_model": "gpt-4"
}
```

## Integration Examples

### With Existing CI/CD

```yaml
# Integrate with existing workflow
- name: Run Autonomy Processing
  if: contains(github.event.issue.labels.*.name, 'auto-process')
  run: |
    autonomy-mcp process \
      --owner ${{ github.repository_owner }} \
      --repo ${{ github.event.repository.name }} \
      --issue ${{ github.event.issue.number }}
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

- name: Run Tests
  run: npm test

- name: Deploy
  if: success()
  run: npm run deploy
```

### With Project Management Tools

```python
# Sync with Jira/Linear
from autonomy_mcp import WorkflowManager

class JiraIntegratedManager(WorkflowManager):
    def process_issue(self, issue_number):
        result = super().process_issue(issue_number)
        
        # Sync with Jira
        self.sync_to_jira(issue_number, result)
        
        return result
```

This usage guide covers the most common scenarios. For more advanced use cases, see the [API Reference](API.md) and [Examples](../examples/).
