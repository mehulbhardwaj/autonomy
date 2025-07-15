# Autonomous MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Autonomous MCP is a Python package that implements the Generate-Verify loop workflow for AI-assisted software development. It provides a structured approach to integrating AI agents into your development workflow while maintaining human oversight.

## 🎯 Core Concept

The Generate-Verify loop implements a structured workflow where:

1. **PM Agent**: Generates requirements and design documents
2. **SDE Agent**: Creates implementation plans and code
3. **QA Agent**: Develops comprehensive test plans  
4. **Human Review**: Provides oversight and approval

## 🚀 Quick Start

### Installation

```bash
pip install autonomy-mcp
```

### Basic Usage

```python
from src import WorkflowManager, WorkflowConfig

# Configure the workflow
config = WorkflowConfig(
    max_file_lines=300,
    max_function_lines=40,
    test_coverage_target=0.75,
    autonomy_level="supervised"
)

# Initialize the workflow manager
manager = WorkflowManager(
    github_token="your_token_here",
    owner="your_org",
    repo="your_repo",
    config=config
)

# Process issues through the Generate-Verify loop
result = manager.process_issue(issue_number=42)
```

## 📋 Key Features

- **Structured Workflow**: Implements the Generate-Verify loop with AI agents
- **GitHub Integration**: Works with GitHub Issues, Labels, and Milestones
- **Quality Constraints**: Enforces file size, function complexity, and test coverage limits
- **Template System**: Provides project templates for common use cases
- **CLI Interface**: Command-line tools for easy integration
- **Configurable**: Flexible configuration for different project needs

## 🔧 Configuration

### Basic Configuration

```python
from src import WorkflowConfig

config = WorkflowConfig(
    max_file_lines=300,
    max_function_lines=40,
    test_coverage_target=0.75,
    autonomy_level="supervised"
)
```

### Autonomy Levels

- **supervised**: Human approval required for all phases (default)
- **semi-autonomous**: Automatic PM and SDE phases, human approval for QA
- **autonomous**: Full automation with human monitoring

## 🏗️ Project Structure

```
autonomous-mcp/
├── src/                     # Main package
│   ├── core/               # Core workflow components
│   ├── github/             # GitHub integration
│   ├── planning/           # Task planning and templates
│   ├── cli/               # Command-line interface
│   └── templates/         # Project templates
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
└── scripts/               # Utility scripts
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/mehulbhardwaj/autonomy.git
cd autonomy

# Install package and development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

For more details see [docs/DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md).

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_autonomy_mcp.py -v
```

## 📚 Documentation

- **[Usage Guide](docs/USAGE_GUIDE.md)**: Comprehensive usage examples
- **[Test Plan](docs/TEST.md)**: Testing strategy and test cases
- **[Examples](examples/)**: Practical usage examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the "Writing Software in English" blog post
- Built for developers who want to leverage AI while maintaining code quality
- Designed for small teams and individual developers

## 🔗 Links

- **GitHub**: https://github.com/mehulbhardwaj/autonomous-mcp
- **Issues**: https://github.com/mehulbhardwaj/autonomous-mcp/issues
- **Documentation**: https://github.com/mehulbhardwaj/autonomous-mcp/tree/main/docs
