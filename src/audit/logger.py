import json
from datetime import datetime
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

    def __init__(self, log_path: Path, use_git: bool = False) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()
        self.use_git = use_git
        self.repo_path = self.log_path.parent
        if self.use_git:
            self._ensure_repo()

    def log(self, operation: str, details: Dict[str, Any]) -> str:
        """Log an operation and return its unique hash."""
        payload = {
            "operation": operation,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
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
