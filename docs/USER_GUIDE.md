# Autonomy Planning Agent - User Guide

## Overview

Autonomy Planning Agent is an intelligent GitHub planning system that enables human-AI collaboration through a structured Generate-Verify loop. This guide will help you get started with Autonomy and use it effectively in your development workflow.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or newer
- GitHub account with repository access
- (Optional) Slack workspace for notifications

### Install Autonomy

```bash
# Install via pip
pip install autonomy

# Or install with development dependencies
pip install autonomy[dev]
```

### Verify Installation

```bash
# Check if autonomy is installed
autonomy --version

# Test the CLI
autonomy --help
```

## Quick Start

### 1. Set Up GitHub Authentication

```bash
# Authenticate with GitHub
autonomy auth login

# Or use a personal access token
export GITHUB_TOKEN="your_token_here"
```

### 2. Initialize Your Repository

```bash
# Initialize Autonomy for your repository
autonomy init --repo your-org/your-repo

# This will:
# - Set up GitHub Projects v2 board
# - Create necessary fields (Priority, Pinned, Sprint, Track)
# - Configure workflow settings
```

### 3. Start Using Autonomy

```bash
# Get your next task
autonomy next

# Update a task status
autonomy update 123 --done --notes "Completed feature X"

# Check project status
autonomy status
```

## Configuration

### Environment Variables

```bash
# GitHub authentication
export GITHUB_TOKEN="your_github_token"

# Slack integration (optional)
export SLACK_BOT_TOKEN="your_slack_bot_token"
export SLACK_SIGNING_SECRET="your_slack_signing_secret"

# Autonomy configuration
export AUTONOMY_LOG_LEVEL="INFO"
export AUTONOMY_WORKSPACE_PATH="/path/to/your/project"
```

### Configuration File

Create `autonomy.json` in your project root:

```json
{
  "github": {
    "owner": "your-org",
    "repo": "your-repo",
    "token": "your_token"
  },
  "workflow": {
    "autonomy_level": "supervised",
    "max_file_lines": 300,
    "max_function_lines": 40,
    "test_coverage_target": 0.75
  },
  "slack": {
    "enabled": true,
    "channel": "#autonomy-daily"
  }
}
```

## Basic Usage

### Task Management

```bash
# Get next priority task
autonomy next

# Get next task for specific assignee
autonomy next --me

# List all tasks
autonomy list

# Update task status
autonomy update 123 --done --notes "Completed implementation"

# Pin/unpin tasks
autonomy pin 123
autonomy unpin 123
```

### Board Management

```bash
# Initialize GitHub Projects board
autonomy board init

# Rank items by priority
autonomy board rank

# Reorder items
autonomy board reorder
```

### Hierarchy Sync

```bash
# Sync issue hierarchy with GitHub Tasklists
autonomy hierarchy-sync --verbose
```

### Backlog Management

```bash
# Run backlog doctor to clean up issues
autonomy doctor run

# Schedule nightly backlog maintenance
autonomy doctor nightly
```

### Metrics and Reporting

Daily metrics include weekly active users (WAU), approval rates,
time-to-task statistics and other workflow insights.

```bash
# View daily metrics
autonomy metrics daily

# Monitor weekly active users and approval rate
autonomy metrics daily --repos owner/repo

# Export metrics
autonomy metrics export --format json

# View audit log
autonomy audit log
```

## Advanced Features

### AI Agent Workflow

Autonomy uses specialized AI agents for different phases:

1. **PM Agent**: Requirements analysis and planning
2. **SDE Agent**: Implementation and development
3. **QA Agent**: Testing and quality assurance

```bash
# Process issue through PM phase
autonomy process 123 --phase pm

# Process issue through full workflow
autonomy process 123 --phase all
```

### Slack Integration

```bash
# Install Slack app
autonomy auth slack install

# Test Slack integration
autonomy slack test

# Send notification
autonomy slack notify --message "Daily digest ready"
```

### Memory and Learning

```bash
# View memory entries
autonomy memory list

# Learn from override
autonomy memory learn --issue 123 --reason "Priority changed"

# Export memory
autonomy memory export
```


## Examples

Useful templates are provided in the `examples/` directory:

- [`agent.yml`](../examples/agent.yml) — sample planning agent configuration
- [`board_cache.json`](../examples/board_cache.json) — cached board field IDs

Copy these files and adapt them to match your repository.


## Troubleshooting

### Common Issues

#### Authentication Problems

```bash
# Check token scopes
autonomy auth scopes

# Re-authenticate
autonomy auth login --force
```

#### Board Setup Issues


```bash
# Reinitialize board
autonomy board init --force

# Check board status
autonomy board status
```
#### Hierarchy Sync Issues

```bash
# Run a dry-run sync to identify problems
autonomy hierarchy-sync --dry-run

# Force sync if items are out of order
autonomy hierarchy-sync --force
```

#### Performance Issues

```bash
# Check performance metrics
autonomy metrics performance

# Clear cache
autonomy cache clear
```

### Undo Operations

```bash
# Undo the last operation
autonomy undo --last

# Undo specific hash with custom window
autonomy undo abcd1234 --commit-window 3

# Create a shadow PR for recent changes
autonomy audit shadow-pr --limit 3
```

### Debug Mode

```bash
# Enable debug logging
export AUTONOMY_LOG_LEVEL="DEBUG"
autonomy next --debug
```

### Getting Help

```bash
# View all commands
autonomy --help

# Get help for specific command
autonomy next --help

# Check version and dependencies
autonomy version
```

## Best Practices

### Repository Setup

1. **Use meaningful issue titles** that clearly describe the task
2. **Add detailed descriptions** with acceptance criteria
3. **Use labels consistently** for categorization
4. **Set appropriate priorities** (P0-P3)

### Workflow Management

1. **Start with supervised mode** until you're comfortable
2. **Review AI agent outputs** before accepting
3. **Use pin/unpin** for important tasks that shouldn't be reordered
4. **Regularly run backlog doctor** to maintain hygiene

### Team Collaboration

1. **Communicate workflow changes** to team members
2. **Use Slack notifications** for transparency
3. **Review metrics regularly** to optimize workflow
4. **Provide feedback** to improve AI agent performance

## Support

- **Documentation**: [GitHub README](https://github.com/mehulbhardwaj/autonomy)
- **Issues**: [GitHub Issues](https://github.com/mehulbhardwaj/autonomy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mehulbhardwaj/autonomy/discussions)

---

*For more advanced usage and development information, see the [Technical Documentation](ARCHITECTURE.md).* 