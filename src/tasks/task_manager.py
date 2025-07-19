from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..github.issue_manager import IssueManager

PRIORITY_WEIGHTS = {
    "priority-critical": 4,
    "priority-high": 3,
    "priority-medium": 2,
    "priority-low": 1,
}


class TaskManager:
    """Utility for retrieving and updating GitHub issues as tasks."""

    def __init__(self, github_token: str, owner: str, repo: str) -> None:
        self.issue_manager = IssueManager(github_token, owner, repo)

    # -------------------------- retrieval helpers ---------------------------
    def _score_issue(
        self, issue: Dict[str, Any], explain: bool = False
    ) -> float | tuple[float, dict]:
        labels = [
            label["name"] if isinstance(label, dict) and "name" in label else label
            for label in issue.get("labels", [])
        ]
        if "blocked" in labels or issue.get("state") == "closed":
            return (float("-inf"), {}) if explain else float("-inf")

        priority = 0
        for label in labels:
            priority = max(priority, PRIORITY_WEIGHTS.get(label, 0))

        created = issue.get("created_at")
        age_days = 0
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - dt).days
            except Exception:
                pass
        score = priority * 100 - age_days
        if explain:
            return score, {"priority": priority, "age_penalty": age_days}
        return score

    def get_next_task(
        self,
        assignee: Optional[str] = None,
        team: Optional[str] = None,
        explain: bool = False,
    ) -> Optional[Dict[str, Any]] | tuple[Optional[Dict[str, Any]], dict]:
        """Return the highest scoring unblocked issue."""
        issues = self.issue_manager.list_issues(state="open")
        candidates = []
        for issue in issues:
            labels = [
                label["name"] if isinstance(label, dict) and "name" in label else label
                for label in issue.get("labels", [])
            ]
            if assignee:
                found = False
                if issue.get("assignee") and issue["assignee"].get("login") == assignee:
                    found = True
                for a in issue.get("assignees", []) or []:
                    if a and a.get("login") == assignee:
                        found = True
                if not found:
                    continue
            if team and not any(
                lbl.lower() == f"team:{team.lower()}" for lbl in labels
            ):
                continue
            score_data = self._score_issue(issue, explain=explain)
            if explain:
                score, breakdown = score_data
            else:
                score = score_data
            if score != float("-inf"):
                candidates.append((score, issue, breakdown if explain else None))

        if not candidates:
            return (None, {}) if explain else None
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_issue, breakdown = candidates[0]
        return (best_issue, breakdown) if explain else best_issue

    def list_tasks(
        self,
        assignee: Optional[str] = None,
        team: Optional[str] = None,
        limit: int = 10,
    ) -> list[Dict[str, Any]]:
        """Return a list of open tasks sorted by priority."""
        issues = self.issue_manager.list_issues(state="open")
        scored = []
        for issue in issues:
            labels = [
                label["name"] if isinstance(label, dict) and "name" in label else label
                for label in issue.get("labels", [])
            ]
            if assignee:
                found = False
                if issue.get("assignee") and issue["assignee"].get("login") == assignee:
                    found = True
                for a in issue.get("assignees", []) or []:
                    if a and a.get("login") == assignee:
                        found = True
                if not found:
                    continue
            if team and not any(
                lbl.lower() == f"team:{team.lower()}" for lbl in labels
            ):
                continue
            score = self._score_issue(issue)
            if score != float("-inf"):
                scored.append((score, issue))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [issue for _, issue in scored[:limit]]

    # --------------------------- update helpers ----------------------------
    def update_task(
        self,
        issue_number: int,
        status: Optional[str] = None,
        done: bool = False,
        notes: Optional[str] = None,
    ) -> bool:
        """Update issue status, closure and add notes."""
        success = True
        if status:
            success &= self.issue_manager.update_issue_labels(
                issue_number, add_labels=[status]
            )
        if done:
            success &= self.issue_manager.update_issue_state(issue_number, "closed")
            self.rollover_subtasks(issue_number)
        if notes:
            self.issue_manager.add_comment(issue_number, notes)
        return success

    # --------------------------- subtask helpers ---------------------------
    def rollover_subtasks(self, issue_number: int) -> bool:
        """Placeholder for subtask rollover logic."""
        # TODO: implement rollover of incomplete subtasks to new issues
        return True
