# Workflow Documentation

## Generate-Verify Loop Process

This repository follows the Generate-Verify loop workflow:

1. **PM-agent**: Requirements → Design → Test Plan
2. **SDE-agent**: Implementation → Initial Testing
3. **QA-agent**: Comprehensive Testing → Hardening
4. **Human**: Code Review → Approval

## Agent Responsibilities

### PM-agent
- Convert issues into detailed requirements
- Create system design documents
- Generate comprehensive test plans
- Update technical documentation

### SDE-agent
- Implement features according to requirements
- Write initial unit tests
- Ensure code quality and standards
- Create pull requests

### QA-agent
- Design comprehensive test suites
- Achieve target test coverage
- Identify edge cases and risks
- Provide implementation feedback

### Human
- Review code quality and design
- Validate requirements fulfillment
- Add approval flag for merge
- Make final architectural decisions

## Quality Standards

- **Max file size**: 300 lines
- **Max function size**: 40 lines
- **Max PR size**: 500 lines
- **Test coverage**: 60-80%
- **Documentation**: Required for all features

## Workflow States

Issues progress through these states:
- `needs-requirements` → `needs-development` → `needs-testing` → `needs-review` → `approved`

## Branch Protection

- Main branch requires approved flag
- All tests must pass
- No direct pushes allowed
- Human approval required for merge

## Release Process

Stable releases are created from the `main` branch. A testing branch named `testing` is used for pre-release builds. Feature development should occur on separate branches that merge into `testing` before being promoted to `main`. Tags on `main` trigger stable releases, while tags on `testing` create pre-releases.

