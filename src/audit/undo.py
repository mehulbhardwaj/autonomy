from typing import Any, Dict, Optional

from .logger import AuditLogger


class UndoManager:
    """Undo operations previously logged by :class:`AuditLogger`."""

    def __init__(
        self, issue_manager: Any, logger: AuditLogger, *, commit_window: int = 5
    ) -> None:
        self.issue_manager = issue_manager
        self.logger = logger
        self.commit_window = commit_window

    def _load_logs(self) -> list[Dict[str, Any]]:
        logs = list(self.logger.iter_logs())
        if self.commit_window > 0:
            logs = logs[-self.commit_window :]  # noqa: E203
        return logs

    def undo(self, hash_value: str) -> bool:
        """Undo a specific operation by its hash."""
        logs = self._load_logs()
        for entry in reversed(logs):
            if entry.get("hash") == hash_value or entry.get("diff_hash") == hash_value:
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

    # ------------------------------------------------------------------
    def create_shadow_branch_pr(
        self, logs: list[Dict[str, Any]], base_branch: str = "main"
    ) -> Optional[int]:
        """Create a shadow branch PR for the provided logs."""
        import json
        import subprocess
        from hashlib import sha1
        from pathlib import Path

        diff_hash = sha1(json.dumps(logs, sort_keys=True).encode()).hexdigest()[:8]
        branch = f"shadow-{diff_hash}"
        if getattr(self.logger, "use_git", False):
            repo = self.logger.repo_path
            try:
                current = subprocess.check_output(
                    ["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"],
                    text=True,
                ).strip()
                subprocess.run(
                    ["git", "-C", str(repo), "checkout", "-b", branch],
                    check=True,
                )
                fpath = Path(repo) / f"undo_{diff_hash}.json"
                fpath.write_text(json.dumps(logs, indent=2))
                subprocess.run(["git", "-C", str(repo), "add", fpath.name], check=True)
                subprocess.run(
                    ["git", "-C", str(repo), "commit", "-m", f"shadow {diff_hash}"],
                    check=True,
                )
                subprocess.run(
                    ["git", "-C", str(repo), "checkout", current], check=True
                )
            except Exception:
                return None

        pr_number = self.issue_manager.create_pull_request(
            title=f"Undo operations {diff_hash}",
            body=f"Automated undo operations\n\nDiff hash: `{diff_hash}`",
            head=branch,
            base=base_branch,
        )
        if pr_number and self.logger:
            self.logger.log(
                "shadow_pr",
                {"hash": diff_hash, "pr": pr_number, "branch": branch},
            )
        return pr_number

    def embed_diff_hash(self, pr_number: int, diff_hash: str) -> bool:
        """Embed ``diff_hash`` as a comment on ``pr_number``."""
        comment = f"diff-hash: `{diff_hash}`"
        success = self.issue_manager.add_comment(pr_number, comment)
        if success and self.logger:
            self.logger.log(
                "embed_diff_hash", {"pr": pr_number, "diff_hash": diff_hash}
            )
        return success
