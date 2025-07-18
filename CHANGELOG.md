# Changelog

All notable changes to Autonomy MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-repository workflow support
- GitHub Copilot integration
- Playwright MCP for UI testing
- Advanced agent customization

## [0.1.1] - 2025-07-16
### Added
- PyPI packaging workflow and install verification utility

## [0.1.0] - 2024-01-XX

### Added
- Initial release of Autonomy MCP
- Core WorkflowManager with Generate-Verify loop implementation
- PM-agent, SDE-agent, and QA-agent with specialized prompts
- GitHub integration with Issues, Labels, Milestones, and Actions
- Planning system with task templates (basic, api, web, cli)
- Command-line interface with init, process, and status commands
- Configuration management with WorkflowConfig
- Comprehensive test coverage and documentation
- Examples and usage guides
- Support for supervised, semi-autonomous, and autonomous modes
- Branch protection and human approval gates
- Living documentation system (PRD.md, TECH.md, TEST.md)

### Features
- **Generate-Verify Loop**: Structured AI workflow with human oversight
- **Agent Specialization**: Role-specific prompts and behaviors
- **Quality Constraints**: File size, function complexity, and PR scope limits
- **Test-Driven Development**: Automated test coverage and validation
- **GitHub Native**: Full integration with GitHub's collaboration features
- **Template System**: Pre-built project templates for common use cases
- **CLI Interface**: Easy command-line usage and automation
- **Configuration**: Flexible configuration for different project needs

### Dependencies
- requests>=2.25.0
- click>=8.0.0
- pydantic>=1.8.0
- rich>=10.0.0
- jinja2>=3.0.0

### Documentation
- Complete README with installation and usage instructions
- Usage guide with examples and best practices
- API reference documentation
- MCP integration guide
- GitHub Actions workflow examples

### Testing
- Comprehensive test suite with pytest
- Unit tests for all core components
- Integration tests for GitHub API
- Mock-based testing for external dependencies
- Test coverage reporting with coverage.py

---

## Release Notes

### v0.1.0 - Initial Release

This is the first release of Autonomy MCP, implementing the core concepts from the "Writing Software in English" blog post. The package enables human-AI collaboration in software development through a structured Generate-Verify loop.

**Key Highlights:**
- 🤖 Three specialized AI agents (PM, SDE, QA) with distinct roles
- 🔄 Generate-Verify loop workflow with human approval gates
- 📋 Native GitHub integration for seamless collaboration
- 🎛️ Quality constraints to maintain code standards
- 🧪 Test-driven development with coverage requirements
- 📚 Living documentation system for project memory

**Getting Started:**
```bash
pip install autonomy-mcp
export GITHUB_TOKEN="your_token"
autonomy-mcp init --owner myorg --repo myproject
autonomy-mcp process --owner myorg --repo myproject --issue 42
```

**What's Next:**
The roadmap includes LLM integration, GitHub Copilot support, multi-repository workflows, and production-ready automation features.

---

For more details, see the [full documentation](https://github.com/mehulbhardwaj/autonomy#readme).
