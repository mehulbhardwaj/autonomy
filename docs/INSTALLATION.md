# Installation Guide

## System Requirements

- **Python**: 3.8 or newer
- **Operating System**: macOS, Linux, or Windows
- **Git**: For repository cloning and version control
- **GitHub Account**: For authentication and repository access

## Installation Methods

### Method 1: PyPI (Recommended)

```bash
# Install the latest stable version
pip install autonomy

# Install with development dependencies
pip install autonomy[dev]

# Install with all optional dependencies
pip install autonomy[dev,llm]
```

### Method 2: Development Installation

```bash
# Clone the repository
git clone https://github.com/mehulbhardwaj/autonomy.git
cd autonomy

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Method 3: Using pipx (Isolated Environment)

```bash
# Install pipx if you don't have it
python -m pip install --user pipx
python -m pipx ensurepath

# Install autonomy globally
pipx install autonomy

# Upgrade to latest version
pipx upgrade autonomy
```

## Verification

After installation, verify that Autonomy is working correctly:

```bash
# Check version
autonomy --version

# Test CLI help
autonomy --help

# Test basic functionality
autonomy auth --help
```

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# GitHub authentication
export GITHUB_TOKEN="your_github_personal_access_token"

# Optional: Slack integration
export SLACK_BOT_TOKEN="your_slack_bot_token"
export SLACK_SIGNING_SECRET="your_slack_signing_secret"

# Optional: Logging level
export AUTONOMY_LOG_LEVEL="INFO"
```

### GitHub Token Setup

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with the following scopes:
   - `repo` (Full control of private repositories)
   - `issues` (Full control of issues)
   - `read:org` (Read organization data)
   - `read:user` (Read user data)

### First-Time Setup

```bash
# Authenticate with GitHub
autonomy auth login

# Initialize your repository
autonomy init --repo your-org/your-repo

# Test the setup
autonomy status
```

## Troubleshooting

### Common Installation Issues

#### Python Version Issues

```bash
# Check your Python version
python --version

# If you need to upgrade Python, use pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

#### Permission Issues

```bash
# If you get permission errors, use --user flag
pip install --user autonomy

# Or use a virtual environment
python -m venv autonomy-env
source autonomy-env/bin/activate  # On Windows: autonomy-env\Scripts\activate
pip install autonomy
```

#### Missing Dependencies

```bash
# Update pip first
pip install --upgrade pip

# Install with all dependencies
pip install autonomy[dev,llm]
```

### Platform-Specific Instructions

#### macOS

```bash
# Using Homebrew
brew install python
pip install autonomy

# Using pyenv
pyenv install 3.11.0
pyenv global 3.11.0
pip install autonomy
```

#### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install autonomy
pip3 install autonomy
```

#### Windows

```bash
# Using PowerShell
python -m pip install autonomy

# Using Command Prompt
pip install autonomy
```

### Development Setup

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/mehulbhardwaj/autonomy.git
cd autonomy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
pre-commit run --all-files
```

## Next Steps

After successful installation:

1. **Read the [User Guide](USER_GUIDE.md)** for basic usage
2. **Check the [Configuration Guide](CONFIGURATION.md)** for advanced setup
3. **Explore the [User Guide](USER_GUIDE.md)** for programmatic usage
4. **Review [Technical Architecture](ARCHITECTURE.md)** for system understanding

## Support

If you encounter installation issues:

- **Check the [troubleshooting section](#troubleshooting)** above
- **Search existing issues** on [GitHub](https://github.com/mehulbhardwaj/autonomy/issues)
- **Create a new issue** with detailed error information
- **Join discussions** on [GitHub Discussions](https://github.com/mehulbhardwaj/autonomy/discussions) 