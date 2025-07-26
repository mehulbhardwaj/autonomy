from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.github.issue_manager import Issue, IssueManager


class GitHubTools:
    """Wrapper around :class:`IssueManager` exposing simple methods."""

    def __init__(self, manager: IssueManager) -> None:
        self.manager = manager

    def create_issue(
        self, data: Dict[str, Any], milestone: Optional[int] = None
    ) -> Optional[int]:
        issue = Issue(**data)
        return self.manager.create_issue(issue, milestone)

    def list_issues(self, state: str = "open") -> List[Dict[str, Any]]:
        return self.manager.list_issues(state=state)

    def get_issue(self, issue_number: int) -> Optional[Dict[str, Any]]:
        """Return issue data if found."""
        return self.manager.get_issue(issue_number)

    def update_issue_labels(
        self,
        issue_number: int,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> bool:
        return self.manager.update_issue_labels(issue_number, add_labels, remove_labels)

    def update_issue(
        self,
        issue_number: int,
        *,
        title: Optional[str] = None,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> bool:
        """Update basic issue fields."""
        return self.manager.update_issue(
            issue_number, title=title, body=body, labels=labels
        )

    def update_issue_state(self, issue_number: int, state: str) -> bool:
        """Open or close an issue."""
        return self.manager.update_issue_state(issue_number, state)

    def assign_issue(self, issue_number: int, assignees: List[str]) -> bool:
        """Assign users to an issue."""
        return self.manager.assign_issue(issue_number, assignees)

    def add_comment(self, issue_number: int, comment: str) -> bool:
        return self.manager.add_comment(issue_number, comment)
