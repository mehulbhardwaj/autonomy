# Autonomy Documentation

This directory contains documentation for the Autonomy Planning Agent.

## Documentation Structure

### For Users
- **[Installation Guide](INSTALLATION.md)** - How to install and set up Autonomy
- **[User Guide](USER_GUIDE.md)** - How to use Autonomy CLI and features
- **[Configuration](CONFIGURATION.md)** - Configuration options and settings

### For Developers
- **[Development Setup](DEVELOPMENT_SETUP.md)** - Setting up the development environment
- **[Workflow](WORKFLOW.md)** - Development workflow and contribution guidelines

### Internal Documentation
- **[Product Requirements (PRD)](REQUIREMENTS.md)** - Product vision and requirements (internal)
- **[Technical Architecture (TECH)](ARCHITECTURE.md)** - System design and implementation details
- **[Testing Strategy (TEST)](TEST.md)** - Testing approach and coverage strategy

## Removed Documentation

The following documentation has been removed to simplify the project:

- ~~OPERATIONS.md~~ - Kubernetes/enterprise deployment (overkill for CLI tool)
- ~~ENTERPRISE.md~~ - Enterprise features (not needed for open source)
- ~~SELF_HOSTING.md~~ - Complex deployment (simple pip install is sufficient)
- ~~ARCHITECTURE.md~~ - Complex system design (simplified in README)

## Why This Simplification?

Autonomy is a **CLI tool** that helps with GitHub task planning. It doesn't need:
- Enterprise deployment guides
- Kubernetes configurations
- Complex monitoring setups
- Database schemas
- Enterprise security features

The simplified documentation focuses on what users actually need: installation, usage, and basic configuration, while keeping essential internal documentation for development. 