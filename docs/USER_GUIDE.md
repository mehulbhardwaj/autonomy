# Autonomy User Guide

This guide provides step-by-step usage instructions for the Autonomy CLI.

## Getting Started

1. Install the package following [INSTALLATION](INSTALLATION.md).
2. Run `autonomy init --repo <owner/repo>` to bootstrap your project.
3. Use `autonomy plan <issue>` to run the planning workflow.

## Core Commands

- `autonomy next` – Show the highest priority issue.
- `autonomy breakdown <issue>` – Decompose an issue into tasks.
- `autonomy assign <issue> --to <user>` – Assign an issue to a developer.

For a full command reference see [API documentation](API.md).

## Troubleshooting

If you encounter problems, run `autonomy doctor run` to analyze your backlog.
