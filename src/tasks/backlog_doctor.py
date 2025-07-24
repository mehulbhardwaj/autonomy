from __future__ import annotations

from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

from ..github.issue_manager import IssueManager


class BacklogDoctor:
    """Analyze and flag backlog issues."""

    STALE_LABEL = "stale"
    DUPLICATE_LABEL = "duplicate-candidate"
    OVERSIZED_LABEL = "oversized"

    def __init__(
        self, issue_manager: IssueManager, slack_client: Optional[Any] = None
    ) -> None:
        self.issue_manager = issue_manager
        self.slack_client = slack_client

    # -------------------------------------------------------------
    def _open_issues(self) -> List[Dict[str, Any]]:
        return self.issue_manager.list_issues(state="open")

    def find_stale_issues(
        self, days: int = 14, issues: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Return issues with no updates for the given number of days."""
        issues = issues or self._open_issues()
        now = datetime.now(timezone.utc)
        stale: List[Dict[str, Any]] = []
        for issue in issues:
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

    def find_oversized_issues(
        self, limit: int = 10, issues: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Return issues with more than ``limit`` checklist items."""
        issues = issues or self._open_issues()
        oversized: List[Dict[str, Any]] = []
        for issue in issues:
            body = issue.get("body", "")
            count = sum(
                1 for line in body.splitlines() if line.strip().startswith("- [")
            )
            if count > limit:
                oversized.append(issue)
        return oversized

    def find_duplicate_candidates(
        self,
        threshold: float = 0.9,
        issues: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any], float]]:
        """Return pairs of issues that look like duplicates."""
        issues = issues or self._open_issues()
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

    # -------------------------------------------------------------
    def calculate_similarity(
        self, issue1: Dict[str, Any], issue2: Dict[str, Any]
    ) -> float:
        """Return a simple similarity score between two issues."""
        text1 = f"{issue1.get('title', '')} {issue1.get('body', '')}".lower()
        text2 = f"{issue2.get('title', '')} {issue2.get('body', '')}".lower()
        return SequenceMatcher(None, text1, text2).ratio()

    def generate_recommendations(
        self,
        stale: List[Dict[str, Any]],
        duplicates: List[Tuple[Dict[str, Any], Dict[str, Any], float]],
        oversized: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Create a list of recommendation dicts for Slack digest."""
        recs: List[Dict[str, Any]] = []
        for issue in stale:
            recs.append(
                {
                    "type": "stale",
                    "issue_number": issue.get("number"),
                    "title": issue.get("title", ""),
                    "action": "Review or close",
                }
            )
        for a, b, _ in duplicates:
            recs.append(
                {
                    "type": "duplicate",
                    "issue_number": a.get("number"),
                    "title": a.get("title", ""),
                    "action": f"Merge with #{b.get('number')}",
                }
            )
        for issue in oversized:
            recs.append(
                {
                    "type": "oversized",
                    "issue_number": issue.get("number"),
                    "title": issue.get("title", ""),
                    "action": "Break into smaller tasks",
                }
            )
        return recs

    def create_digest_message(self, recommendations: List[Dict[str, Any]]) -> str:
        """Return a plain text Slack digest from recommendations."""
        digest = "\U0001f3e5 **Nightly Backlog Doctor Report**\n\n"
        for rec in recommendations:
            digest += (
                f"\u2022 {rec['type']}: #{rec['issue_number']} - {rec['title']}\n"
                f"  \ud83d\udca1 *Recommendation*: {rec['action']}\n\n"
            )
        digest += (
            "\n\ud83d\udcca Run `/autonomy status` for full backlog health metrics"
        )
        return digest

    def run_nightly_diagnosis(
        self,
        channel: str = "#autonomy-daily",
        stale_days: int = 14,
        duplicate_threshold: float = 0.9,
        checklist_limit: int = 10,
    ) -> Dict[str, Any]:
        """Run checks and optionally post a Slack digest."""
        issues = self._open_issues()
        stale = self.find_stale_issues(days=stale_days, issues=issues)
        duplicates = self.find_duplicate_candidates(
            threshold=duplicate_threshold, issues=issues
        )
        oversized = self.find_oversized_issues(limit=checklist_limit, issues=issues)
        recs = self.generate_recommendations(stale, duplicates, oversized)
        message = self.create_digest_message(recs)
        if self.slack_client:
            try:
                self.slack_client.post_message(channel, message)
            except Exception:
                pass
        return {
            "stale_count": len(stale),
            "duplicate_pairs": len(duplicates),
            "oversized_count": len(oversized),
            "recommendations": recs,
        }
