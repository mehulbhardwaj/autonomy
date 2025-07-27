#!/usr/bin/env python3
"""
GitHub Issue Management System
Comprehensive system for creating and managing GitHub issues from task plan documents.
Supports the Generate-Verify loop workflow with PM-agent, SDE-agent, and QA-agent roles.
"""

import argparse
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
import requests

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class Label:
    """GitHub label definition"""

    name: str
    color: str
    description: str


@dataclass
class Milestone:
    """GitHub milestone definition"""

    title: str
    description: str
    due_on: Optional[str] = None
    state: str = "open"


@dataclass
class Issue:
    """GitHub issue definition"""

    title: str
    body: str
    labels: List[str]
    milestone: Optional[str] = None
    assignees: Optional[List[str]] = None
    epic_parent: Optional[str] = None
    story_points: Optional[int] = None
    acceptance_criteria: Optional[List[str]] = None
    agent_role: Optional[str] = None  # PM-agent, SDE-agent, QA-agent
    verification_required: bool = True


class IssueManager:
    """Main class for managing GitHub issues"""

    def __init__(
        self,
        github_token: str,
        owner: str,
        repo: str,
        audit_logger=None,
        session: requests.Session | None = None,
    ):
        self.github_token = github_token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }
        self.session = session

        # Optional audit logger for tracking operations
        self.audit_logger = audit_logger

        # Standard labels for the Generate-Verify loop
        self.standard_labels = [
            Label(
                "epic", "8B5CF6", "Large feature or initiative spanning multiple issues"
            ),
            Label("feature", "0E8A16", "New feature or enhancement"),
            Label("task", "1D76DB", "Individual task or work item"),
            Label("bug", "D73A4A", "Something isn't working"),
            Label(
                "documentation", "0075CA", "Improvements or additions to documentation"
            ),
            Label("enhancement", "A2EEEF", "New feature or request"),
            Label("devops", "F9D0C4", "DevOps and infrastructure related"),
            # Agent roles
            Label("pm-agent", "FF6B6B", "PM-agent: Requirements and planning"),
            Label("sde-agent", "4ECDC4", "SDE-agent: Software development"),
            Label("qa-agent", "45B7D1", "QA-agent: Quality assurance and testing"),
            # Workflow states
            Label("needs-requirements", "FBCA04", "Needs requirements document"),
            Label("needs-design", "FEF2C0", "Needs system design document"),
            Label("needs-tests", "F1C40F", "Needs test plan"),
            Label("in-development", "0052CC", "Currently being developed"),
            Label("needs-review", "5319E7", "Needs code review"),
            Label("approved", "0E8A16", "Approved and ready to merge"),
            Label("blocked", "D73A4A", "Blocked by dependencies"),
            # Priority levels
            Label("priority-critical", "B60205", "Critical priority"),
            Label("priority-high", "D93F0B", "High priority"),
            Label("priority-medium", "FBCA04", "Medium priority"),
            Label("priority-low", "0E8A16", "Low priority"),
        ]

    def create_labels(self) -> None:
        """Create standard labels in the repository"""
        print("Creating standard labels...")

        for label in self.standard_labels:
            try:
                sess = self.session or requests
                response = sess.post(
                    f"{self.base_url}/labels", headers=self.headers, json=asdict(label)
                )

                if response.status_code == 201:
                    print(f"✓ Created label: {label.name}")
                elif response.status_code == 422:
                    # Label already exists, update it
                    sess.patch(
                        f"{self.base_url}/labels/{label.name}",
                        headers=self.headers,
                        json={"color": label.color, "description": label.description},
                    )
                    print(f"✓ Updated label: {label.name}")
                else:
                    print(f"✗ Failed to create label {label.name}: {response.text}")

            except Exception as e:
                print(f"✗ Error creating label {label.name}: {e}")

    def create_milestone(self, milestone: Milestone) -> Optional[int]:
        """Create a milestone and return its number"""
        try:
            milestone_dict = asdict(milestone)
            sess = self.session or requests
            response = sess.post(
                f"{self.base_url}/milestones", headers=self.headers, json=milestone_dict
            )

            if response.status_code == 201:
                milestone_data = response.json()
                print(
                    f"✓ Created milestone: {milestone.title} (#{milestone_data['number']})"
                )
                return milestone_data["number"]
            else:
                print(
                    f"✗ Failed to create milestone {milestone.title}: {response.text}"
                )
                return None

        except Exception as e:
            print(f"✗ Error creating milestone {milestone.title}: {e}")
            return None

    def create_issue(
        self, issue: Issue, milestone_number: Optional[int] = None
    ) -> Optional[int]:
        """Create a GitHub issue and return its number"""

        # Build issue body with structured information
        body_parts = [issue.body]

        if issue.acceptance_criteria:
            body_parts.append("\n## Acceptance Criteria")
            for criteria in issue.acceptance_criteria:
                body_parts.append(f"- {criteria}")

        if issue.story_points:
            body_parts.append(f"\n**Story Points:** {issue.story_points}")

        if issue.agent_role:
            body_parts.append(f"\n**Agent Role:** {issue.agent_role}")

        if issue.epic_parent:
            body_parts.append(f"\n**Epic:** {issue.epic_parent}")

        # Add Generate-Verify loop information
        if issue.verification_required:
            body_parts.append("\n## Generate-Verify Loop")
            body_parts.append("- [ ] Requirements document created (PM-agent)")
            body_parts.append("- [ ] System design document created (PM-agent)")
            body_parts.append("- [ ] Test plan created (PM-agent)")
            body_parts.append("- [ ] Feature implemented (SDE-agent)")
            body_parts.append("- [ ] Tests pass (SDE-agent)")
            body_parts.append("- [ ] Additional test cases written (QA-agent)")
            body_parts.append("- [ ] Code review completed (Human)")
            body_parts.append("- [ ] Approved flag added")

        issue_data = {
            "title": issue.title,
            "body": "\n".join(body_parts),
            "labels": issue.labels or [],
        }

        if milestone_number:
            issue_data["milestone"] = milestone_number

        if issue.assignees:
            issue_data["assignees"] = issue.assignees

        try:
            sess = self.session or requests
            response = sess.post(
                f"{self.base_url}/issues", headers=self.headers, json=issue_data
            )

            if response.status_code == 201:
                issue_response = response.json()
                print(f"✓ Created issue: {issue.title} (#{issue_response['number']})")
                if self.audit_logger:
                    self.audit_logger.log(
                        "create_issue",
                        {
                            "issue": issue_response["number"],
                            "title": issue.title,
                        },
                    )
                return issue_response["number"]
            else:
                print(f"✗ Failed to create issue {issue.title}: {response.text}")
                return None

        except Exception as e:
            print(f"✗ Error creating issue {issue.title}: {e}")
            return None

    def list_issues(self, state: str = "open") -> List[Dict[str, Any]]:
        """Return a list of issues from the repository"""
        try:
            sess = self.session or requests
            response = sess.get(
                f"{self.base_url}/issues",
                headers=self.headers,
                params={"state": state},
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return []

    def get_issue(self, issue_number: int) -> Optional[Dict[str, Any]]:
        """Return a single issue if found."""
        try:
            sess = self.session or requests
            response = sess.get(
                f"{self.base_url}/issues/{issue_number}", headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None

    async def _fetch_issue_async(
        self, client: httpx.AsyncClient, issue_number: int
    ) -> Optional[Dict[str, Any]]:
        try:
            response = await client.get(
                f"{self.base_url}/issues/{issue_number}", headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None

    async def bulk_fetch_issues(
        self, issue_numbers: List[int]
    ) -> List[Optional[Dict[str, Any]]]:
        """Fetch multiple issues concurrently."""
        async with httpx.AsyncClient() as client:
            tasks = [self._fetch_issue_async(client, num) for num in issue_numbers]
            return await asyncio.gather(*tasks)

    def update_issue_state(self, issue_number: int, state: str) -> bool:
        """Update the state of an issue (e.g., open or closed)."""
        try:
            sess = self.session or requests
            response = sess.patch(
                f"{self.base_url}/issues/{issue_number}",
                headers=self.headers,
                json={"state": state},
            )
            success = response.status_code == 200
            if success and self.audit_logger:
                self.audit_logger.log(
                    "update_state",
                    {"issue": issue_number, "new": state},
                )
            return success
        except Exception:
            return False

    def update_issue_labels(
        self,
        issue_number: int,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> bool:
        """Add and remove labels on an issue."""
        issue = self.get_issue(issue_number)
        if not issue:
            return False
        labels = [
            label["name"] if isinstance(label, dict) and "name" in label else label
            for label in issue.get("labels", [])
        ]
        if add_labels:
            labels.extend(add_labels)
        if remove_labels:
            labels = [label for label in labels if label not in remove_labels]
        labels = list(dict.fromkeys(labels))
        try:
            sess = self.session or requests
            response = sess.patch(
                f"{self.base_url}/issues/{issue_number}",
                headers=self.headers,
                json={"labels": labels},
            )
            success = response.status_code == 200
            if success and self.audit_logger:
                self.audit_logger.log(
                    "update_labels",
                    {
                        "issue": issue_number,
                        "add_labels": add_labels,
                        "remove_labels": remove_labels,
                    },
                )
            return success
        except Exception:
            return False

    def update_issue(
        self,
        issue_number: int,
        *,
        title: Optional[str] = None,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        return_response: bool = False,
    ) -> bool | requests.Response:
        """Update basic fields on an issue."""
        payload: Dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        if labels is not None:
            payload["labels"] = labels
        if not payload:
            return False
        try:
            sess = self.session or requests
            response = sess.patch(
                f"{self.base_url}/issues/{issue_number}",
                headers=self.headers,
                json=payload,
            )
            success = response.status_code == 200
            if success and self.audit_logger:
                self.audit_logger.log(
                    "update_issue",
                    {k: payload[k] for k in payload.keys()},
                )
            return response if return_response else success
        except Exception:
            return False

    def assign_issue(self, issue_number: int, assignees: List[str]) -> bool:
        """Assign users to an issue."""
        try:
            sess = self.session or requests
            response = sess.patch(
                f"{self.base_url}/issues/{issue_number}",
                headers=self.headers,
                json={"assignees": assignees},
            )
            success = response.status_code == 200
            if success and self.audit_logger:
                self.audit_logger.log(
                    "assign_issue",
                    {"issue": issue_number, "assignees": assignees},
                )
            return success
        except Exception:
            return False

    # ------------------------------------------------------------------
    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> Optional[int]:
        """Create a pull request and return its number."""
        try:
            sess = self.session or requests
            response = sess.post(
                f"{self.base_url}/pulls",
                headers=self.headers,
                json={"title": title, "body": body, "head": head, "base": base},
            )
            if response.status_code in (200, 201):
                pr = response.json()
                if self.audit_logger:
                    self.audit_logger.log(
                        "create_pr",
                        {
                            "pr": pr.get("number"),
                            "title": title,
                            "head": head,
                            "base": base,
                        },
                    )
                return pr.get("number")
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    def get_open_issues_count(self, repo: str | None = None) -> int:
        """Return the number of open issues for ``repo``."""
        try:
            sess = self.session or requests
            response = sess.get(
                f"{self.base_url}/issues",
                headers=self.headers,
                params={"state": "open"},
            )
            if response.status_code == 200:
                return len(response.json())
        except Exception:
            pass
        return 0

    def calculate_time_to_task(self) -> float:
        """Average hours from issue creation to first assignment."""
        issues = self.list_issues(state="all")
        durations = []
        for issue in issues:
            created = issue.get("created_at")
            if not created:
                continue
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except Exception:
                continue
            try:
                sess = self.session or requests
                events = sess.get(
                    f"{self.base_url}/issues/{issue['number']}/events",
                    headers=self.headers,
                )
                if events.status_code != 200:
                    continue
                for ev in events.json():
                    if ev.get("event") == "assigned":
                        assigned_dt = datetime.fromisoformat(
                            ev["created_at"].replace("Z", "+00:00")
                        )
                        durations.append(
                            (assigned_dt - created_dt).total_seconds() / 3600.0
                        )
                        break
            except Exception:
                continue
        if not durations:
            return 0.0
        return sum(durations) / len(durations)

    def weekly_active_users(self, days: int = 7) -> int:
        """Count unique issue creators in the past ``days``."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        try:
            sess = self.session or requests
            response = sess.get(
                f"{self.base_url}/issues",
                headers=self.headers,
                params={"since": since, "state": "all"},
            )
            if response.status_code != 200:
                return 0
            users = {
                i.get("user", {}).get("login")
                for i in response.json()
                if i.get("user") and i.get("user", {}).get("login")
            }
            return len(users)
        except Exception:
            return 0

    def calculate_sprint_completion(self) -> float:
        """Return percent of issues closed in the nearest open milestone."""
        try:
            sess = self.session or requests
            response = sess.get(
                f"{self.base_url}/milestones",
                headers=self.headers,
                params={"state": "open", "sort": "due_on", "direction": "asc"},
            )
            if response.status_code != 200:
                return 0.0
            milestones = response.json()
            if not milestones:
                return 0.0
            ms = milestones[0]
            closed = ms.get("closed_issues", 0)
            open_cnt = ms.get("open_issues", 0)
            total = closed + open_cnt
            return (closed / total * 100) if total else 0.0
        except Exception:
            return 0.0

    def add_comment(self, issue_number: int, comment: str) -> bool:
        """Add a comment to an issue."""
        try:
            sess = self.session or requests
            response = sess.post(
                f"{self.base_url}/issues/{issue_number}/comments",
                headers=self.headers,
                json={"body": comment},
            )
            success = response.status_code in (200, 201)
            if success and self.audit_logger:
                self.audit_logger.log(
                    "add_comment",
                    {"issue": issue_number, "comment": comment},
                )
            return success
        except Exception:
            return False

    def setup_repository(self) -> None:
        """Perform basic repository bootstrap such as creating labels"""
        self.create_labels()


def main():
    parser = argparse.ArgumentParser(description="GitHub Issue Management System")
    parser.add_argument("--token", required=True, help="GitHub personal access token")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument(
        "--setup", action="store_true", help="Set up repository with labels"
    )

    args = parser.parse_args()

    # Initialize the manager
    manager = IssueManager(args.token, args.owner, args.repo)

    if args.setup:
        manager.create_labels()


if __name__ == "__main__":
    main()
