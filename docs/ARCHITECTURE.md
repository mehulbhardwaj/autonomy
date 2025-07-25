# Architecture Deep Dive

This document expands on the high level overview in [TECH](TECH.md) and
provides details about each component of the system.

- **Agents**: coordinate work using LangGraph workflows.
- **Memory**: uses Mem0 to store context and relationships.
- **Tools**: integrate with external services like GitHub and Slack.
