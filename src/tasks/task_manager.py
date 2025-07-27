from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Dict, Optional

from ..audit.logger import AuditLogger
from ..core.config import WorkflowConfig
from ..github.issue_manager import IssueManager
from .hierarchy_manager import HierarchyManager
from .pinned_items import PinnedItemsStore
from .ranking import RankingConfig, RankingEngine


class TaskManager:
    """Utility for retrieving and updating GitHub issues as tasks."""

    def __init__(
        self,
        github_token: str,
        owner: str,
        repo: str,
        pinned_store: PinnedItemsStore | None = None,
        ranking_config: RankingConfig | None = None,
        config_path: str | None = None,
        *,
        audit_logger: Optional["AuditLogger"] = None,
        config: WorkflowConfig | None = None,
    ) -> None:
        self.config = config or WorkflowConfig()
        self.issue_manager = IssueManager(
            github_token,
            owner,
            repo,
            audit_logger=audit_logger,
            on_change=self._trigger_sync,
        )
        self.audit_logger = audit_logger or getattr(
            self.issue_manager, "audit_logger", None
        )
        self.pinned_store = pinned_store or PinnedItemsStore()
        self.project_id = f"{owner}/{repo}"
        self.ranking = RankingEngine(
            ranking_config, config_path=Path(config_path) if config_path else None
        )
        self.sync_cooldown = getattr(self.config, "hierarchy_sync_cooldown", 60)
        self._last_sync = 0.0

    # -------------------------- retrieval helpers ---------------------------
    def _score_issue(
        self, issue: Dict[str, Any], explain: bool = False
    ) -> float | tuple[float, dict]:
        pinned = self.pinned_store.is_pinned(self.project_id, str(issue.get("number")))
        if pinned:
            return (float("-inf"), {}) if explain else float("-inf")
        return self.ranking.score_issue(issue, pinned=False, explain=explain)

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
        self._trigger_sync()
        return success

    # --------------------------- subtask helpers ---------------------------
    def rollover_subtasks(self, issue_number: int) -> bool:
        """Placeholder for subtask rollover logic."""
        # TODO: implement rollover of incomplete subtasks to new issues
        return True

    def _trigger_sync(self) -> None:
        """Run hierarchy sync asynchronously."""

        import time

        if time.time() - self._last_sync < self.sync_cooldown:
            return

        self._last_sync = time.time()

        def run() -> None:
            cfg = getattr(self, "config", WorkflowConfig())
            hm = HierarchyManager(
                self.issue_manager,
                orphan_threshold=cfg.hierarchy_orphan_threshold,
            )
            hm.maintain_hierarchy()
            if self.audit_logger:
                self.audit_logger.log(
                    "hierarchy_sync_auto",
                    {"project": self.project_id, "created": "auto"},
                )

        threading.Thread(target=run, daemon=True).start()
