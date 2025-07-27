import json
from datetime import datetime, timedelta
from hashlib import sha1
from pathlib import Path
from typing import Any, Dict


class AuditLogger:
    """Simple append-only JSON lines audit logger.

    Parameters
    ----------
    log_path:
        Path to the audit log file.
    use_git:
        If ``True`` the logger will commit updates to ``log_path`` using Git.
    """

    def __init__(
        self,
        log_path: Path,
        use_git: bool = False,
        *,
        overrides_path: Path | None = None,
    ) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()
        self.overrides_path = (
            Path(overrides_path)
            if overrides_path is not None
            else self.log_path.with_name("overrides.log")
        )
        self.use_git = use_git
        self.repo_path = self.log_path.parent
        if self.use_git:
            self._ensure_repo()

    def log(self, operation: str, details: Dict[str, Any]) -> str:
        """Log an operation and return its unique hash.

        A secondary ``diff_hash`` based only on the operation details is also
        recorded so that external systems can verify the change without caring
        about the timestamp.
        """
        payload = {
            "operation": operation,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }

        diff_hash = sha1(json.dumps(details, sort_keys=True).encode()).hexdigest()[:8]
        payload["diff_hash"] = diff_hash

        digest = sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:8]
        payload["hash"] = digest
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
        if self.use_git:
            message = f"audit: {payload['hash']} {operation}"
            self._git_commit(message)
        return digest

    def iter_logs(self):
        """Yield log entries as dictionaries."""
        if not self.log_path.exists():
            return
        with self.log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    # ------------------------------------------------------------------
    def count_human_overrides(self) -> int:
        """Return the number of manual override events."""
        if not self.overrides_path.exists():
            return 0
        with self.overrides_path.open("r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())

    def count_command_usage(self, cmd: str) -> int:
        """Return count of tool executions matching ``cmd``."""
        count = 0
        for entry in self.iter_logs() or []:
            if entry.get("operation") == "tool_execute":
                details = entry.get("details", {})
                if details.get("tool") == cmd or details.get("action") == cmd:
                    count += 1
        return count

    def count_ai_recommendations(self, days: int = 7) -> int:
        """Return count of automated actions in the last ``days``."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        count = 0
        for entry in self.iter_logs() or []:
            if entry.get("operation") == "tool_execute":
                ts = entry.get("timestamp")
                try:
                    dt = datetime.fromisoformat(ts)
                except Exception:
                    continue
                if dt >= cutoff:
                    count += 1
        return count

    def count_approvals(self, days: int = 7) -> int:
        """Return count of successful automated actions in ``days``."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        count = 0
        for entry in self.iter_logs() or []:
            if entry.get("operation") == "tool_execute":
                ts = entry.get("timestamp")
                try:
                    dt = datetime.fromisoformat(ts)
                except Exception:
                    continue
                if dt >= cutoff and entry.get("details", {}).get("success"):
                    count += 1
        return count

    def count_undo_operations(self, days: int = 7) -> int:
        """Return number of undo events in ``days``."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        cnt = 0
        for entry in self.iter_logs() or []:
            if entry.get("operation") == "undo_operation":
                ts = entry.get("timestamp")
                try:
                    dt = datetime.fromisoformat(ts)
                except Exception:
                    continue
                if dt >= cutoff:
                    cnt += 1
        return cnt

    def weekly_active_users(self, days: int = 7) -> int:
        """Return count of unique agents who executed tools in ``days``."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        users = set()
        for entry in self.iter_logs() or []:
            if entry.get("operation") == "tool_execute":
                ts = entry.get("timestamp")
                try:
                    dt = datetime.fromisoformat(ts)
                except Exception:
                    continue
                if dt >= cutoff:
                    agent = entry.get("details", {}).get("agent")
                    if agent:
                        users.add(agent)
        return len(users)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_repo(self) -> None:
        """Ensure ``repo_path`` is a git repository with basic config."""
        import subprocess

        if (
            subprocess.run(
                ["git", "-C", str(self.repo_path), "rev-parse"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            != 0
        ):
            subprocess.run(["git", "-C", str(self.repo_path), "init"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.repo_path),
                    "config",
                    "user.email",
                    "audit@example.com",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.repo_path),
                    "config",
                    "user.name",
                    "Autonomy Audit",
                ],
                check=True,
            )

    def _git_commit(self, message: str) -> None:
        """Commit the audit log file with ``message``."""
        import subprocess

        subprocess.run(
            ["git", "-C", str(self.repo_path), "add", str(self.log_path.name)],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo_path), "commit", "-m", message],
            check=True,
        )
