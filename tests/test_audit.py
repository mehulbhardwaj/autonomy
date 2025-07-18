from pathlib import Path

from src.audit.logger import AuditLogger
from src.audit.undo import UndoManager


class DummyIM:
    def __init__(self):
        self.labels = None

    def update_issue_labels(self, issue_number, add_labels=None, remove_labels=None):
        self.labels = (issue_number, add_labels, remove_labels)
        return True


def test_logger_and_undo(tmp_path: Path) -> None:
    logger = AuditLogger(tmp_path / "audit.log", use_git=True)
    # ensure git repo exists
    assert (tmp_path / ".git").exists()
    dummy = DummyIM()
    h = logger.log(
        "update_labels", {"issue": 2, "add_labels": ["a"], "remove_labels": None}
    )
    undo = UndoManager(dummy, logger)
    assert undo.undo_last() == h
    assert dummy.labels == (2, [], ["a"])
    # verify commit message contains hash
    import subprocess

    log = subprocess.check_output(
        ["git", "-C", str(tmp_path), "log", "-1", "--pretty=%s"],
        text=True,
    ).strip()
    assert h in log
