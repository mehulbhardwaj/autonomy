# Autonomy Planning Agent (Core)

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://github.com/mehulbhardwaj/autonomy/workflows/CI/badge.svg)](https://github.com/mehulbhardwaj/autonomy/actions)

**Extensible agentic platform enabling humans + AI to collaborate for knowledge work** – An intelligent GitHub planning system with configurable AI agents that learn from your team's patterns and coordinate tasks across humans and specialized AI assistants.

https://autonomyhub.vercel.app
---

## 🎯 Vision

Autonomy transforms GitHub into an extensible intelligent collaboration platform where configurable AI agents work alongside human team members to plan, prioritize, and coordinate work. The platform supports unlimited agent types - from core planning agents to specialized domain experts - all configurable through simple YAML files. Instead of replacing human judgment, it augments team decision-making with memory-driven insights and automated task coordination.

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

- **Agent Orchestration:** [LangGraph](https://github.com/langchain-ai/langgraph) for multi-step workflows
- **LLM Integration:** [OpenRouter](https://openrouter.ai) for unified access to 400+ models
- **Memory System:** [Mem0](https://github.com/mem0ai/mem0) for intelligent context and relationship tracking
- **GitHub Integration:** GraphQL + REST for comprehensive GitHub automation
- **Team Communication:** Slack integration for notifications and collaboration

---

## 📋 Core Features

- **CLI & API:** Planning, ranking, assignment, status, and more
- **GitHub Integration:** Issues, Projects v2, authentication, board bootstrap, hierarchy management
- **Slack Integration:** Basic bot, slash commands, notifications
- **Task Management:** Priority ranking, manual override (pin/unpin), breakdown, dependencies
- **Security & Storage:** OS-native secret storage, basic audit logging
- **Self-hosted Support:** All code and docs needed to run on-premise
- **Documentation:** Comprehensive user and developer docs

---

## 📚 Documentation

- **[Product Requirements](docs/PRD.md)** - Complete product vision and requirements
- **[Technical Architecture](docs/TECH.md)** - System design and implementation details  
- **[Development Setup](docs/DEVELOPMENT_SETUP.md)** - Local development environment setup
- **[Test Strategy](docs/TEST.md)** - Testing approach and coverage strategy

---

## 🤝 Contributing

We welcome contributions from developers interested in AI-human collaboration and intelligent automation!

1. **Read the docs**: Start with [TECH.md](docs/TECH.md)
2. **Setup environment**: Follow [DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
3. **Pick an issue**: Check [good first issues](https://github.com/mehulbhardwaj/autonomy/labels/good%20first%20issue)
4. **Join discussions**: Participate in issue discussions and planning

---

### Release Strategy

Stable releases are tagged from the `main` branch. Testing releases use commits from the `testing` branch and are published as pre-releases. Development work should occur on feature branches that merge into `testing` before stabilizing in `main`.


## 📄 License

This project is licensed under the GNU GPLv3 or later - see the [LICENSE](LICENSE) file for details.

---

**Status:** Active open source development. Contributions welcome!
