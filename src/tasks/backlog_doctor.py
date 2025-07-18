from __future__ import annotations

from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple

from ..github.issue_manager import IssueManager


class BacklogDoctor:
    """Analyze and flag backlog issues."""

    STALE_LABEL = "stale"
    DUPLICATE_LABEL = "duplicate-candidate"
    OVERSIZED_LABEL = "oversized"

    def __init__(self, issue_manager: IssueManager) -> None:
        self.issue_manager = issue_manager

    # -------------------------------------------------------------
    def _open_issues(self) -> List[Dict[str, Any]]:
        return self.issue_manager.list_issues(state="open")

    def find_stale_issues(self, days: int = 14) -> List[Dict[str, Any]]:
        """Return issues with no updates for the given number of days."""
        now = datetime.now(timezone.utc)
        stale: List[Dict[str, Any]] = []
        for issue in self._open_issues():
            ts = issue.get("updated_at") or issue.get("created_at")
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                continue
            if (now - dt).days > days:
                stale.append(issue)
        return stale

    def find_oversized_issues(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return issues with more than ``limit`` checklist items."""
        oversized: List[Dict[str, Any]] = []
        for issue in self._open_issues():
            body = issue.get("body", "")
            count = sum(
                1 for line in body.splitlines() if line.strip().startswith("- [")
            )
            if count > limit:
                oversized.append(issue)
        return oversized

    def find_duplicate_candidates(
        self, threshold: float = 0.9
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any], float]]:
        """Return pairs of issues that look like duplicates."""
        issues = self._open_issues()
        dupes: List[Tuple[Dict[str, Any], Dict[str, Any], float]] = []
        for i in range(len(issues)):
            for j in range(i + 1, len(issues)):
                a, b = issues[i], issues[j]
                title_sim = SequenceMatcher(
                    None, a.get("title", "").lower(), b.get("title", "").lower()
                ).ratio()
                body_sim = SequenceMatcher(
                    None, a.get("body", "").lower(), b.get("body", "").lower()
                ).ratio()
                sim = max(title_sim, body_sim)
                if sim >= threshold:
                    dupes.append((a, b, sim))
        return dupes

    # -------------------------------------------------------------
    def run(
        self,
        stale_days: int = 14,
        checklist_limit: int = 10,
        check_stale: bool = True,
        check_duplicates: bool = True,
        check_oversized: bool = True,
    ) -> Dict[str, Any]:
        """Run selected checks and apply labels."""
        results = {"stale": [], "duplicates": [], "oversized": []}

        if check_stale:
            stale = self.find_stale_issues(days=stale_days)
            results["stale"] = [i["number"] for i in stale]
            for issue in stale:
                self.issue_manager.update_issue_labels(
                    issue["number"], add_labels=[self.STALE_LABEL]
                )

        if check_oversized:
            oversized = self.find_oversized_issues(limit=checklist_limit)
            results["oversized"] = [i["number"] for i in oversized]
            for issue in oversized:
                self.issue_manager.update_issue_labels(
                    issue["number"], add_labels=[self.OVERSIZED_LABEL]
                )

        if check_duplicates:
            duplicates = self.find_duplicate_candidates()
            results["duplicates"] = [
                (a["number"], b["number"]) for a, b, _ in duplicates
            ]
            for a, b, _ in duplicates:
                self.issue_manager.update_issue_labels(
                    a["number"], add_labels=[self.DUPLICATE_LABEL]
                )
                self.issue_manager.update_issue_labels(
                    b["number"], add_labels=[self.DUPLICATE_LABEL]
                )

        return results
