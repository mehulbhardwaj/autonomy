# Autonomous MCP Usage Guide

This guide covers practical usage patterns for Autonomous MCP, a Python package that implements AI-assisted software development through the Generate-Verify loop.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Project Templates](#project-templates)
- [GitHub Integration](#github-integration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Installation

```bash
pip install autonomy-mcp
```

### 2. Basic Setup

```python
from src import WorkflowManager, WorkflowConfig

# Create configuration
config = WorkflowConfig(
    max_file_lines=300,
    max_function_lines=40,
    test_coverage_target=0.75,
    autonomy_level="supervised"
)

# Initialize workflow manager
manager = WorkflowManager(
    github_token="your_github_token",
    owner="your_username",
    repo="your_repository",
    workspace_path="./workspace",
    config=config
)
```

### 3. GitHub Token Setup

Create a GitHub Personal Access Token with these permissions:
- `repo` - Repository access
- `issues` - Issue management
- `metadata` - Repository metadata

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

Or set it directly in your code:
```python
import os
github_token = os.getenv('GITHUB_TOKEN')
```

## Configuration

### WorkflowConfig Options

```python
from src import WorkflowConfig

config = WorkflowConfig(
    # Quality constraints
    max_file_lines=300,           # Maximum lines per file
    max_function_lines=40,        # Maximum lines per function
    test_coverage_target=0.75,    # Target test coverage (75%)
    
    # Workflow behavior
    autonomy_level="supervised",  # supervised | semi-autonomous | autonomous
    require_human_approval=True,  # Require approval for actions
    
    # Agent configuration
    pm_agent_model="gpt-4",      # PM agent model
    sde_agent_model="gpt-4",     # SDE agent model
    qa_agent_model="gpt-4",      # QA agent model
    agent_temperature=0.1        # Temperature for AI responses
)
```

### Autonomy Levels

**Supervised (Default)**
- Human approval required for all phases
- Maximum safety and control
- Best for getting started

**Semi-Autonomous**
- Automatic PM and SDE phases
- Human approval for QA and final steps
- Balanced automation

**Autonomous**
- Full automation with monitoring
- Human oversight optional
- Maximum efficiency

## Basic Usage

### Processing Issues

```python
from src import WorkflowManager

# Initialize manager
manager = WorkflowManager(
    github_token="your_token",
    owner="username",
    repo="repository",
    config=config
)

# Process a single issue
result = manager.process_issue(issue_number=42)
print(f"Issue {result.issue_number} processed: {result.status}")

# Process multiple issues
issue_numbers = [1, 2, 3]
for issue_num in issue_numbers:
    result = manager.process_issue(issue_number=issue_num)
    print(f"Issue #{issue_num}: {result.status}")
```

### Working with Agents

```python
from src.core.agents import PMAgent, SDEAgent, QAAgent

# Create agents
pm_agent = PMAgent(config)
sde_agent = SDEAgent(config)
qa_agent = QAAgent(config)

# Get system prompts
print("PM Agent Prompt:", pm_agent.get_system_prompt())
print("SDE Agent Prompt:", sde_agent.get_system_prompt())
print("QA Agent Prompt:", qa_agent.get_system_prompt())
```

## Project Templates

### Using Plan Manager

```python
from src.planning import PlanManager

# Create plan manager
plan_manager = PlanManager()

# Create different template types
basic_plan = plan_manager.create_plan_template("basic")
api_plan = plan_manager.create_plan_template("api")
web_plan = plan_manager.create_plan_template("web")
cli_plan = plan_manager.create_plan_template("cli")

# Save plan to file
plan_manager.save_plan(api_plan, "my_api_plan.json")

# Load plan from file
loaded_plan = plan_manager.load_plan("my_api_plan.json")

# Validate plan
errors = plan_manager.validate_plan(loaded_plan)
if errors:
    print("Plan validation errors:", errors)
else:
    print("Plan is valid!")
```

### Custom Templates

```python
# Create custom plan structure
custom_plan = {
    "metadata": {
        "name": "My Custom Project",
        "description": "A custom project template",
        "template_type": "custom",
        "version": "1.0"
    },
    "phases": {
        "pm": {
            "tasks": [
                "Define user requirements",
                "Create system architecture",
                "Design data models"
            ]
        },
        "sde": {
            "tasks": [
                "Implement core functionality",
                "Create unit tests",
                "Update documentation"
            ]
        },
        "qa": {
            "tasks": [
                "Create integration tests",
                "Perform quality review",
                "Validate test coverage"
            ]
        }
    }
}

# Save and use custom plan
plan_manager.save_plan(custom_plan, "custom_template.json")
```

## GitHub Integration

### Issue Management

```python
from src.github.issue_manager import IssueManager

# Create issue manager
issue_manager = IssueManager(
    github_token="your_token",
    owner="username",
    repo="repository"
)

# Create issue with labels
issue = issue_manager.create_issue(
    title="Implement user authentication",
    body="Add login/logout functionality with JWT tokens",
    labels=["feature", "authentication", "pm-agent"]
)

# Update issue
issue_manager.update_issue(
    issue_number=issue["number"],
    labels=["feature", "authentication", "sde-agent"],
    state="open"
)

# Add comment to issue
issue_manager.add_comment(
    issue_number=issue["number"],
    body="Starting SDE phase - implementing authentication system"
)
```

### Working with Labels

```python
# Setup standard labels for workflow
standard_labels = [
    # Issue types
    {"name": "feature", "color": "84b6eb", "description": "New feature request"},
    {"name": "bug", "color": "d73a4a", "description": "Bug report"},
    {"name": "task", "color": "bfd4f2", "description": "General task"},
    
    # Agent roles
    {"name": "pm-agent", "color": "1d76db", "description": "Product Manager agent"},
    {"name": "sde-agent", "color": "0e8a16", "description": "Software Engineer agent"},
    {"name": "qa-agent", "color": "fbca04", "description": "Quality Assurance agent"},
    
    # Workflow states
    {"name": "needs-requirements", "color": "ff7619", "description": "Needs requirements"},
    {"name": "in-development", "color": "0075ca", "description": "In development"},
    {"name": "needs-testing", "color": "f9d0c4", "description": "Needs testing"},
    {"name": "approved", "color": "0e8a16", "description": "Approved and ready"}
]

# Create labels in repository
for label in standard_labels:
    try:
        issue_manager.create_label(
            name=label["name"],
            color=label["color"],
            description=label["description"]
        )
        print(f"Created label: {label['name']}")
    except Exception as e:
        print(f"Label {label['name']} might already exist: {e}")
```

## Troubleshooting

### Common Issues

**Import Errors**
```python
# If you get import errors, ensure package is installed correctly
try:
    from src import WorkflowManager, WorkflowConfig
    print("✅ Package imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Try: pip install -e . from the package directory")
```

**GitHub API Errors**
```python
# Handle GitHub API rate limiting and errors
try:
    result = manager.process_issue(42)
except Exception as e:
    if "rate limit" in str(e).lower():
        print("GitHub API rate limit exceeded. Wait and try again.")
    elif "not found" in str(e).lower():
        print("Repository or issue not found. Check your configuration.")
    else:
        print(f"GitHub API error: {e}")
```

**Configuration Issues**
```python
# Validate configuration before use
config = WorkflowConfig()
try:
    is_valid = config.validate()
    if is_valid:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration validation failed")
except Exception as e:
    print(f"Configuration error: {e}")
```

### Debug Mode

```python
# Enable detailed logging for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed information about API calls and workflow steps
manager = WorkflowManager(
    github_token="your_token",
    owner="username", 
    repo="repository",
    config=config
)
```

### Testing Configuration

```python
# Test your setup with a simple configuration check
def test_setup():
    try:
        # Test imports
        from src import WorkflowManager, WorkflowConfig
        print("✅ Imports successful")
        
        # Test configuration
        config = WorkflowConfig()
        print("✅ Configuration created")
        
        # Test GitHub token (if available)
        import os
        if os.getenv('GITHUB_TOKEN'):
            print("✅ GitHub token found in environment")
        else:
            print("⚠️  GitHub token not found in environment")
            
        return True
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

# Run test
if test_setup():
    print("🎉 Setup is ready!")
else:
    print("🔧 Setup needs attention")
```

## Best Practices

1. **Start Simple**: Begin with supervised mode and basic configuration
2. **Test Locally**: Validate configuration and GitHub access before processing issues
3. **Use Templates**: Leverage existing templates rather than creating from scratch
4. **Monitor Progress**: Check issue comments and labels to track workflow progress
5. **Human Review**: Always review AI-generated content before approval
6. **Incremental Adoption**: Start with small issues to build confidence

## Getting Help

- **Issues**: Report bugs at https://github.com/mehulbhardwaj/autonomous-mcp/issues
- **Documentation**: Check the docs/ directory for additional information
- **Examples**: See examples/ directory for practical usage patterns
