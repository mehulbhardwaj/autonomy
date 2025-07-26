from typing import Any, Dict, Optional

from .logger import AuditLogger


class UndoManager:
    """Undo operations previously logged by :class:`AuditLogger`."""

    def __init__(self, issue_manager: Any, logger: AuditLogger) -> None:
        self.issue_manager = issue_manager
        self.logger = logger

    def _load_logs(self) -> list[Dict[str, Any]]:
        return list(self.logger.iter_logs())

    def undo(self, hash_value: str) -> bool:
        """Undo a specific operation by its hash."""
        logs = self._load_logs()
        for entry in reversed(logs):
            if entry.get("hash") == hash_value:
                return self._apply(entry)
        return False

    def undo_last(self) -> Optional[str]:
        logs = self._load_logs()
        if not logs:
            return None
        last = logs[-1]
        if self._apply(last):
            return last.get("hash")
        return None

    def _apply(self, entry: Dict[str, Any]) -> bool:
        op = entry.get("operation")
        details = entry.get("details", {})
        if op == "update_labels":
            issue = details.get("issue")
            add = details.get("add_labels") or []
            remove = details.get("remove_labels") or []
            return self.issue_manager.update_issue_labels(
                issue, add_labels=remove, remove_labels=add
            )
        elif op == "update_state":
            issue = details.get("issue")
            prev = details.get("previous")
            if prev:
                return self.issue_manager.update_issue_state(issue, prev)
        elif op == "add_comment":
            issue = details.get("issue")
            comment = details.get("comment")
            if comment:
                # Cannot truly undo a comment via GitHub API; post a note instead
                note = f"Undo: delete previous comment -> {comment}"
                return self.issue_manager.add_comment(issue, note)
        return False
