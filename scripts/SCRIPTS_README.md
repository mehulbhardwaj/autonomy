# Scripts

This directory contains helper utilities for the **FocusMate AI** project.  
At the moment it houses one script: `create-github-issues.sh`.

## 1. Purpose

`create-github-issues.sh` automates the creation of **milestones** and **issues** on GitHub, based on the Action-Plan in `docs/PLAN.md`.  
Running it once on a new repository will:

1. Add milestones for each delivery phase (`alpha-0.1`, `beta-0.3`, …).
2. Create epics plus all feature/task issues, pre-labelled and assigned to the correct milestone.
3. Add two “continuous” process issues (weekly dog-fooding & monthly audits).

## 2. Prerequisites

| Requirement | Notes |
|-------------|-------|
| **bash ≥ 4** | The script is POSIX-ish but uses arrays & `[[` |
| **curl** | For REST calls to the GitHub API |
| **jq** | Simple JSON parsing (install with `brew`, `apt`, `choco`, etc.) |
| **GitHub personal access token (PAT)** | Must have `repo` scope (or finer-grained issue/milestone rights) |

## 3. Quick Start

```bash
# 1. Make sure the script is executable
chmod +x scripts/create-github-issues.sh

# 2. Run it
./scripts/create-github-issues.sh <GITHUB_TOKEN> <owner> <repo>
# Example:
./scripts/create-github-issues.sh ghp_xxx123 waw-mehul flow-mate
```

Arguments:

1. **`<GITHUB_TOKEN>`** – your PAT (keep it secret!)
2. **`<owner>`** – GitHub username or organisation
3. **`<repo>`** – target repository name

> Tip: Create a short-lived token just for this bootstrap action.

## 4. What the Script Does

1. **Milestones**  
   It POSTs to `/milestones`, setting a description and quarter-end due-date for each phase.

2. **Issues**  
   For every row in the action-plan table it POSTs to `/issues` with:
   - Title & detailed body
   - `milestone` number (linking to phase)
   - Labels such as `epic`, `feature`, `task`, `documentation`, etc.

3. **Idempotency**  
   The GitHub API will create duplicates if you run the script twice.  
   Run it **only once** per repo or delete dupes manually.

## 5. Customising

Feel free to tweak:

* **Story points** – adjust in the issue bodies.
* **Labels** – edit the JSON array in `create_issue()`.
* **Milestone dates** – change the ISO timestamps near the top.

## 6. Troubleshooting

| Symptom | Fix |
|---------|-----|
| *“Bad credentials”* | Token missing `repo` scope or pasted wrong |
| *Milestone created but no issues* | Check `jq` is installed; ensure rate-limit not exceeded |
| *Duplicates* | Delete duplicated milestones/issues and rerun after patching script |

## 7. Additional Utilities

The following helper scripts streamline package releases and testing:

* `bump-version.sh` – bump the project version and create a git tag
* `release-notes.sh` – generate changelog entries from commit messages
* `test-installation.sh` – verify installation via `pipx` and `pip`

Contributions welcome—open a PR or discussion!
