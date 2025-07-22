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

    def update_issue_labels(
        self,
        issue_number: int,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> bool:
        return self.manager.update_issue_labels(issue_number, add_labels, remove_labels)

    def add_comment(self, issue_number: int, comment: str) -> bool:
        return self.manager.add_comment(issue_number, comment)
