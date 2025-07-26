# Autonomy Planning Agent (Core)

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://github.com/mehulbhardwaj/autonomy/workflows/CI/badge.svg)](https://github.com/mehulbhardwaj/autonomy/actions)

**Open source platform enabling humans + AI to collaborate for knowledge work** – An intelligent GitHub planning system with configurable AI agents that learn from your team's patterns and coordinate tasks across humans and specialized AI assistants.

---

## 🎯 Vision

Autonomy transforms GitHub into an intelligent collaboration platform where AI agents work alongside human team members to plan, prioritize, and coordinate work. The platform supports configurable AI agents - from core planning agents to specialized domain experts - all configurable through simple YAML files. Instead of replacing human judgment, it augments team decision-making with memory-driven insights and automated task coordination.

---

## 🚀 Quick Start

### Installation
```bash
# Global CLI installation
pipx install autonomy

# Initialize with your GitHub repository
autonomy init --repo your-org/your-repo
```

### Development Setup
```bash
git clone https://github.com/mehulbhardwaj/autonomy.git
cd autonomy
pip install -e .[dev]
pre-commit install
pytest
```

---

## 🏗️ Architecture Overview

- **Agent Orchestration:** Configurable AI agents for different roles (PM, SDE, QA)
- **LLM Integration:** [OpenRouter](https://openrouter.ai) for unified access to 400+ models
- **Memory System:** Repository-scoped memory for intelligent context and relationship tracking
- **GitHub Integration:** GraphQL + REST for comprehensive GitHub automation
- **Team Communication:** Slack integration for notifications and collaboration

---

## 📋 Core Features

- **CLI Interface:** Planning, ranking, assignment, status, and more
- **GitHub Integration:** Issues, Projects v2, authentication, board bootstrap, hierarchy management
- **Slack Integration:** Basic bot, slash commands, notifications
- **Task Management:** Priority ranking, manual override (pin/unpin), breakdown, dependencies
- **Security & Storage:** OS-native secret storage, basic audit logging
- **Documentation:** Comprehensive user and developer docs

---

## 📚 Documentation

### For Users
- **[Installation Guide](docs/INSTALLATION.md)** - How to install and set up Autonomy
- **[User Guide](docs/USER_GUIDE.md)** - How to use Autonomy CLI and features
- **[Configuration](docs/CONFIGURATION.md)** - Configuration options and settings

### For Developers
- **[Development Setup](docs/DEVELOPMENT_SETUP.md)** - Setting up the development environment
- **[Workflow](docs/WORKFLOW.md)** - Development workflow and contribution guidelines

### Internal Documentation
- **[Product Requirements (PRD)](docs/REQUIREMENTS.md)** - Product vision and requirements (internal)
- **[Technical Architecture (TECH)](docs/ARCHITECTURE.md)** - System design and implementation details
- **[Testing Strategy (TEST)](docs/TEST.md)** - Testing approach and coverage strategy

---

## 🎯 Examples

The `examples/` directory contains configuration templates and examples:

- **[`agent.yml`](examples/agent.yml)** - Example AI agent configuration
- **[`board_cache.json`](examples/board_cache.json)** - GitHub Projects field cache example

### Quick Configuration Examples

**Basic Setup:**
```bash
# Install and authenticate
pipx install autonomy
autonomy auth login

# Initialize repository
autonomy init --repo my-org/my-repo

# Get next task
autonomy next
```

**Slack Integration:**
```bash
# Setup Slack bot
autonomy auth slack install

# Use Slack commands
/autonomy next
/autonomy update 123 --done
/autonomy pin 456
```

**Board Management:**
```bash
# Initialize GitHub Projects board
autonomy board init

# Rank items by priority
autonomy board rank

# Reorder items
autonomy board reorder
```

---

## 🤝 Contributing

We welcome contributions from developers interested in AI-human collaboration and intelligent automation!

1. **Read the docs**: Start with [ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. **Setup environment**: Follow [DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
3. **Pick an issue**: Check [good first issues](https://github.com/mehulbhardwaj/autonomy/labels/good%20first%20issue)
4. **Join discussions**: Participate in issue discussions and planning

---

### Release Strategy

Stable releases are tagged from the `main` branch. Testing releases use commits from the `testing` branch and are published as pre-releases. Development work should occur on feature branches that merge into `testing` before stabilizing in `main`.

---

## 📄 License

This project is licensed under the GNU GPLv3 or later - see the [LICENSE](LICENSE) file for details.

---

**Status:** Active open source development. Contributions welcome!
