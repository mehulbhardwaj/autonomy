# Development Environment Setup

This guide explains how to configure a local development environment for the Autonomy project.

## Requirements

- Python 3.8 or newer
- Git

## Installation

```bash
# Clone the repository
git clone https://github.com/mehulbhardwaj/autonomy.git
cd autonomy

# Install the package and development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

## Running Checks

- **Lint and formatting**:
  ```bash
  pre-commit run --all-files
  ```
- **Type checking**:
  ```bash
  mypy src tests
  ```
- **Tests with coverage**:
  ```bash
  pytest
  ```
The test configuration enforces a minimum of 80% coverage.
