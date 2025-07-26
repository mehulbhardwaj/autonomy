# Configuration Guide

## Overview

Autonomy Planning Agent can be configured through environment variables, configuration files, and command-line options. This guide covers all configuration options and their usage.

## Configuration Methods

### 1. Environment Variables

The most common way to configure Autonomy:

```bash
# GitHub Configuration
export GITHUB_TOKEN="your_github_token"
export GITHUB_OWNER="your-org"
export GITHUB_REPO="your-repo"

# Slack Configuration (Optional)
export SLACK_BOT_TOKEN="your_slack_bot_token"
export SLACK_SIGNING_SECRET="your_slack_signing_secret"
export SLACK_CHANNEL="#autonomy-daily"

# Autonomy Configuration
export AUTONOMY_LOG_LEVEL="INFO"
export AUTONOMY_WORKSPACE_PATH="/path/to/project"
export AUTONOMY_AUTONOMY_LEVEL="supervised"
```

### 2. Configuration File

Create `autonomy.json` in your project root:

```json
{
  "github": {
    "token": "your_github_token",
    "owner": "your-org",
    "repo": "your-repo"
  },
  "workflow": {
    "autonomy_level": "supervised",
    "max_file_lines": 300,
    "max_function_lines": 40,
    "test_coverage_target": 0.75,
    "require_human_approval": true
  },
  "slack": {
    "enabled": true,
    "bot_token": "your_slack_bot_token",
    "signing_secret": "your_slack_signing_secret",
    "channel": "#autonomy-daily"
  },
  "llm": {
    "provider": "openrouter",
    "api_key": "your_openrouter_api_key",
    "model": "anthropic/claude-3-sonnet"
  }
}
```

### 3. Command-Line Options

```bash
# Override configuration via command line
autonomy next --autonomy-level autonomous
autonomy process 123 --max-file-lines 500
autonomy init --repo my-org/my-repo --autonomy-level supervised
```

## Configuration Options

### GitHub Configuration

| Option | Environment Variable | Default | Description |
|--------|-------------------|---------|-------------|
| Token | `GITHUB_TOKEN` | Required | GitHub personal access token |
| Owner | `GITHUB_OWNER` | Required | Repository owner/organization |
| Repository | `GITHUB_REPO` | Required | Repository name |
| API URL | `GITHUB_API_URL` | `https://api.github.com` | GitHub API base URL |

### Workflow Configuration

| Option | Environment Variable | Default | Description |
|--------|-------------------|---------|-------------|
| Autonomy Level | `AUTONOMY_LEVEL` | `supervised` | `supervised`, `semi-autonomous`, `autonomous` |
| Max File Lines | `AUTONOMY_MAX_FILE_LINES` | `300` | Maximum lines per file |
| Max Function Lines | `AUTONOMY_MAX_FUNCTION_LINES` | `40` | Maximum lines per function |
| Test Coverage Target | `AUTONOMY_TEST_COVERAGE_TARGET` | `0.75` | Minimum test coverage (0.0-1.0) |
| Human Approval | `AUTONOMY_REQUIRE_HUMAN_APPROVAL` | `true` | Require human approval for changes |

### Slack Configuration

| Option | Environment Variable | Default | Description |
|--------|-------------------|---------|-------------|
| Enabled | `SLACK_ENABLED` | `false` | Enable Slack integration |
| Bot Token | `SLACK_BOT_TOKEN` | None | Slack bot user OAuth token |
| Signing Secret | `SLACK_SIGNING_SECRET` | None | Slack app signing secret |
| Channel | `SLACK_CHANNEL` | `#autonomy-daily` | Default notification channel |

### LLM Configuration

| Option | Environment Variable | Default | Description |
|--------|-------------------|---------|-------------|
| Provider | `LLM_PROVIDER` | `openrouter` | LLM provider (`openrouter`, `openai`, `anthropic`) |
| API Key | `LLM_API_KEY` | None | API key for LLM provider |
| Model | `LLM_MODEL` | `anthropic/claude-3-sonnet` | Model to use for AI agents |
| Temperature | `LLM_TEMPERATURE` | `0.1` | Model temperature (0.0-1.0) |
| Max Tokens | `LLM_MAX_TOKENS` | `4000` | Maximum tokens per request |

### Logging Configuration

| Option | Environment Variable | Default | Description |
|--------|-------------------|---------|-------------|
| Log Level | `AUTONOMY_LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| Log Format | `AUTONOMY_LOG_FORMAT` | `json` | Log format (`json`, `text`) |
| Log File | `AUTONOMY_LOG_FILE` | None | Log file path (optional) |

## Autonomy Levels

### Supervised (Default)

- Human approval required for all phases
- Maximum safety and control
- Ideal for critical projects and teams new to AI collaboration

```bash
export AUTONOMY_LEVEL="supervised"
```

### Semi-Autonomous

- Automatic PM and SDE phases
- Human approval for QA and merge
- Balanced automation and oversight

```bash
export AUTONOMY_LEVEL="semi-autonomous"
```

### Autonomous

- Full automation with human monitoring
- Automatic merge on approval
- Maximum efficiency for trusted workflows

```bash
export AUTONOMY_LEVEL="autonomous"
```

## Quality Constraints

### File Size Limits

```bash
# Set maximum file size
export AUTONOMY_MAX_FILE_LINES="300"

# Set maximum function size
export AUTONOMY_MAX_FUNCTION_LINES="40"

# Set maximum PR size
export AUTONOMY_MAX_PR_LINES="500"
```

### Test Coverage

```bash
# Set minimum test coverage
export AUTONOMY_TEST_COVERAGE_TARGET="0.75"

# Enable coverage enforcement
export AUTONOMY_ENFORCE_COVERAGE="true"
```

## Advanced Configuration

### Custom Ranking Weights

Create `ranking_weights.json`:

```json
{
  "priority": 0.4,
  "sprint_proximity": 0.2,
  "issue_age": 0.15,
  "assignee_availability": 0.1,
  "dependency_impact": 0.1,
  "complexity": 0.05
}
```

### Custom Agent Prompts

Create `agent_prompts.yaml`:

```yaml
pm_agent:
  system_prompt: |
    You are a Product Manager agent. Your role is to:
    - Analyze requirements and create detailed specifications
    - Break down complex features into manageable tasks
    - Ensure alignment with business objectives
    
sde_agent:
  system_prompt: |
    You are a Software Development Engineer agent. Your role is to:
    - Implement features according to specifications
    - Write clean, maintainable code
    - Ensure code quality and standards
    
qa_agent:
  system_prompt: |
    You are a Quality Assurance agent. Your role is to:
    - Design comprehensive test strategies
    - Identify edge cases and risks
    - Ensure quality standards are met
```

### Memory Configuration

```bash
# Enable memory learning
export AUTONOMY_MEMORY_ENABLED="true"

# Set memory retention period (days)
export AUTONOMY_MEMORY_RETENTION_DAYS="30"

# Enable pattern mining
export AUTONOMY_PATTERN_MINING_ENABLED="true"
```

## Environment-Specific Configuration

### Development Environment

```bash
# Development settings
export AUTONOMY_LOG_LEVEL="DEBUG"
export AUTONOMY_AUTONOMY_LEVEL="supervised"
export AUTONOMY_TEST_COVERAGE_TARGET="0.8"
```

### Production Environment

```bash
# Production settings
export AUTONOMY_LOG_LEVEL="INFO"
export AUTONOMY_AUTONOMY_LEVEL="semi-autonomous"
export AUTONOMY_REQUIRE_HUMAN_APPROVAL="true"
```

### CI/CD Environment

```bash
# CI/CD settings
export AUTONOMY_LOG_LEVEL="WARNING"
export AUTONOMY_AUTONOMY_LEVEL="autonomous"
export AUTONOMY_REQUIRE_HUMAN_APPROVAL="false"
```

## Configuration Validation

### Validate Configuration

```bash
# Validate current configuration
autonomy config validate

# Show current configuration
autonomy config show

# Test configuration
autonomy config test
```

### Configuration Commands

```bash
# Set configuration value
autonomy config set workflow.autonomy_level supervised

# Get configuration value
autonomy config get workflow.autonomy_level

# Reset configuration
autonomy config reset
```

## Troubleshooting

### Common Configuration Issues

#### Missing Required Variables

```bash
# Check required environment variables
autonomy config check

# Set missing variables
export GITHUB_TOKEN="your_token"
export GITHUB_OWNER="your-org"
export GITHUB_REPO="your-repo"
```

#### Invalid Configuration Values

```bash
# Validate configuration file
autonomy config validate --file autonomy.json

# Check for configuration errors
autonomy config show --verbose
```

#### Permission Issues

```bash
# Check GitHub token scopes
autonomy auth scopes

# Verify Slack permissions
autonomy slack test
```

## Best Practices

### Security

1. **Use environment variables** for sensitive data
2. **Rotate tokens regularly** (GitHub, Slack, API keys)
3. **Use minimal required scopes** for GitHub tokens
4. **Store secrets securely** (use keychain or vault)

### Performance

1. **Set appropriate log levels** (DEBUG for development, INFO for production)
2. **Configure memory retention** based on your needs
3. **Use caching** for frequently accessed data
4. **Monitor resource usage** and adjust limits

### Maintainability

1. **Document custom configurations** in your project
2. **Use version control** for configuration files
3. **Test configuration changes** before deploying
4. **Backup configuration** regularly

## Next Steps

- **Read the [User Guide](USER_GUIDE.md)** for usage examples
- **Check the [User Guide](USER_GUIDE.md)** for programmatic configuration
- **Review [Technical Architecture](ARCHITECTURE.md)** for system understanding 