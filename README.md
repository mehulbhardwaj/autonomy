# Autonomy Planning Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://github.com/mehulbhardwaj/autonomy/workflows/CI/badge.svg)](https://github.com/mehulbhardwaj/autonomy/actions)

**Extensible agentic platform enabling humans + AI to collaborate for knowledge work** – An intelligent GitHub planning system with configurable AI agents that learn from your team's patterns and coordinate tasks across humans and specialized AI assistants.

---

## 🎯 Vision

Autonomy transforms GitHub into an extensible intelligent collaboration platform where configurable AI agents work alongside human team members to plan, prioritize, and coordinate work. The platform supports unlimited agent types - from core planning agents to specialized domain experts - all configurable through simple YAML files. Instead of replacing human judgment, it augments team decision-making with memory-driven insights and automated task coordination.

### Core Capabilities
- **🧠 Memory-Driven Intelligence**: Learns from past decisions and team patterns
- **🤝 Human + AI Collaboration**: AI agents suggest, humans decide on critical paths
- **🔧 Extensible Agent Platform**: Configure unlimited agent types through YAML files
- **📋 Intelligent Task Management**: Context-aware priority ranking and assignment
- **🔄 Adaptive Planning**: Workflows that evolve based on team feedback
- **📊 GitHub-Native Integration**: Leverages Projects v2, Issues, and native workflows

---

## 🚀 Quick Start

### Installation (Coming Soon)
```bash
# Global CLI installation
pipx install autonomy

# Initialize with your GitHub repository
autonomy init --repo your-org/your-repo
```

### Current Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/mehulbhardwaj/autonomy.git
cd autonomy

# Install in development mode
pip install -e .[dev]

# Configure GitHub authentication
autonomy auth login

# Initialize repository for planning
autonomy board init
```

---

## 🏗️ Architecture Overview

### Agent-Driven Collaboration
```
Human Team Members  ←→  AI Planning Agents  ←→  GitHub Projects v2
       ↓                       ↓                       ↓
   Decision Making      Task Analysis & Planning    Source of Truth
   Quality Gates       Memory-Informed Insights    Issue Management
   Strategic Direction Pattern Recognition         Priority Tracking
```

### Technology Stack
- **Agent Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) for complex multi-step workflows
- **LLM Integration**: [OpenRouter](https://openrouter.ai) for unified access to 400+ models
- **Memory System**: [Mem0](https://github.com/mem0ai/mem0) for intelligent context and relationship tracking
- **GitHub Integration**: GraphQL + REST for comprehensive GitHub automation
- **Team Communication**: Slack integration for notifications and collaboration

---

## 📋 Current Status

### ✅ Phase 0: Foundation (80% Complete)
- **✅ Professional CLI Framework**: Comprehensive command structure with rich output
- **✅ GitHub Integration**: Issues, Projects, authentication, and API management
- **✅ Slack Integration**: Bot setup, OAuth, and notification infrastructure
- **✅ Task Management**: Priority ranking, hierarchy management, manual overrides
- **✅ Security**: OS keychain integration with encrypted fallback
- **🟡 Missing**: Package distribution, OAuth app registration, Projects v2 GraphQL

### 🚧 Phase 1: Extensible Agent Platform MVP (In Planning)
- **❌ Agent Platform Core**: Dynamic agent registration and YAML configuration
- **❌ LLM Integration**: Multi-model support with agent-specific preferences
- **❌ Memory System**: Agent namespace isolation with cross-agent insights
- **❌ Planning Workflows**: LangGraph orchestration with dynamic agent selection
- **❌ Tool Registry**: Agent-aware permissions for GitHub, Slack, and custom tools

---

## 🎨 User Experience

### CLI Commands
```bash
# Planning Agent Commands (Core Value)
autonomy next                    # Get next highest-priority task (AI-ranked)
autonomy next --team frontend    # Team-specific intelligent task retrieval
autonomy plan issue 42           # Full AI planning workflow for issue
autonomy rerank                  # Re-evaluate all priorities with AI
autonomy assign issue 42 --to alice  # AI-suggested optimal assignment

# Task Management
autonomy update 42 --done       # Mark complete, trigger rollover planning
autonomy dependencies 42        # Show AI-detected dependencies
autonomy breakdown 42           # AI task decomposition for complex issues

# Team Collaboration & Learning
autonomy status                  # AI-powered team and project status
autonomy memory --patterns      # Show what the Planning Agent has learned
autonomy explain ranking 42     # Explain why AI ranked this issue here
autonomy tune --priority-weights # Adjust Planning Agent's ranking criteria

# Repository Management
autonomy board init              # Setup Projects v2 integration
autonomy doctor --check         # Backlog health analysis
autonomy sync --with-slack      # Sync with team Slack workspace
```

### Slack Integration
```bash
# Slash Commands (Coming Soon)
/autonomy next                   # Get next task in current channel
/autonomy status                 # Show team status
/autonomy assign @alice issue-42 # Assign tasks with context
```

---

## 🧠 Intelligent Features

### Memory-Driven Decision Making
- **Issue Context**: Remembers similar issues and successful solutions
- **Team Patterns**: Learns individual and team working preferences
- **Decision History**: Tracks outcomes of planning decisions for improvement
- **Tool Usage**: Optimizes tool selection based on past success rates

### Adaptive Priority Ranking
- **Multi-Signal Scoring**: Priority labels, sprint proximity, issue age, dependencies
- **Manual Override Learning**: Learns when humans override rankings and adapts
- **Team Context**: Considers team capacity and individual strengths
- **Temporal Awareness**: Adjusts priorities based on deadlines and milestones

### Human + AI Collaboration Patterns
- **AI Suggests, Human Decides**: AI provides analysis, humans make critical decisions
- **Approval Gates**: Configurable checkpoints for human oversight
- **Explainable Decisions**: All AI recommendations include clear reasoning
- **Reversible Actions**: Complete audit trail with one-click undo capabilities

---

## 📚 Documentation

### For Developers
- **[Technical Architecture](docs/TECH.md)**: System design and development guidelines
- **[Development Setup](docs/DEVELOPMENT_SETUP.md)**: Local development environment
- **[Test Strategy](docs/TEST.md)**: Comprehensive testing approach for AI systems

### For Product Teams
- **[Planning Agent PRD](docs/Autonomy_Planning_Agent_PRD.md)**: Product requirements and vision
- **[Implementation Roadmap](https://github.com/mehulbhardwaj/autonomy/issues/52)**: Development sequence and milestones
- **[Workflow Documentation](docs/WORKFLOW.md)**: Team collaboration patterns

---

## 🛠️ Development

### Setup Development Environment
```bash
# Install dependencies
pip install -e .[dev]

# Setup pre-commit hooks for code quality
pre-commit install

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Architecture Principles
1. **Memory-First Development**: All agents consider past interactions
2. **Tool-First Integration**: External interactions through standardized tool registry
3. **Human Respect**: AI augments human decision-making, doesn't replace it
4. **Explainable AI**: All decisions include clear reasoning and context
5. **Reversible Actions**: Complete audit trail with undo capabilities

### Code Quality Standards
- **Type Safety**: Full type hints throughout codebase
- **Test Coverage**: >90% unit test coverage, >80% integration coverage
- **Security**: Permission-based tool access with complete audit logging
- **Performance**: <2s CLI response times, <500ms memory retrieval

---

## 🎯 Roadmap

### 🚀 Phase 1: Extensible Agent Platform MVP (Weeks 1-6)
**Goal**: Configurable agent platform with intelligent orchestration

**Key Features**:
- Agent Platform Core with YAML-based agent configuration
- OpenRouter multi-LLM integration with agent-specific preferences
- Mem0 memory system with agent namespace isolation
- LangGraph workflows with dynamic agent selection and coordination
- Tool registry with agent-aware permissions for GitHub/Slack/custom tools

### 🏢 Phase 2: Production Readiness (Month 2)
**Goal**: Enterprise-ready agentic platform

**Key Features**:
- Advanced learning from team patterns and user overrides
- Multi-repository coordination and cross-team workflows
- Enterprise security (SSO/SAML, audit streaming, policy gates)
- Performance optimization and 99.9% uptime SLO

### 🌐 Phase 3+: Agent Ecosystem & Scale (Month 3+)
**Goal**: Platform for knowledge work automation with agent marketplace

**Key Features**:
- Plugin SDK for custom agent development and distribution
- Agent marketplace with community-contributed specialized agents
- Web interface for visual workflow management and agent configuration
- Advanced analytics and team performance insights with agent metrics
- Integration ecosystem (Linear, Jira, monitoring tools)

---

## 🤝 Contributing

We welcome contributions from developers interested in AI-human collaboration and intelligent automation!

### Getting Started
1. **Read the docs**: Start with [TECH.md](docs/TECH.md) for architecture overview
2. **Setup environment**: Follow [DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
3. **Pick an issue**: Check [good first issues](https://github.com/mehulbhardwaj/autonomy/labels/good%20first%20issue)
4. **Join discussions**: Participate in issue discussions and planning

### Development Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Follow code quality standards (`pre-commit run --all-files`)
6. Submit a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Vision**: Inspired by the need for intelligent human-AI collaboration in knowledge work
- **Community**: Built for teams who want AI that augments rather than replaces human judgment
- **Technology**: Leveraging cutting-edge agent frameworks and memory systems for production use

---

## 🔗 Links

- **📋 Project Board**: [GitHub Issues](https://github.com/mehulbhardwaj/autonomy/issues)
- **📖 Documentation**: [docs/](docs/)
- **🗺️ Roadmap**: [Implementation Roadmap](https://github.com/mehulbhardwaj/autonomy/issues/52)
- **💬 Discussions**: [GitHub Discussions](https://github.com/mehulbhardwaj/autonomy/discussions)

---

**Status**: Active development of intelligent GitHub planning agent. Contributions welcome!