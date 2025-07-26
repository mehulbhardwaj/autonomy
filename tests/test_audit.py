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

    # verify diff hash is stored
    entry = next(logger.iter_logs())
    expected_diff = (
        __import__("hashlib")
        .sha1(
            __import__("json")
            .dumps(
                {"issue": 2, "add_labels": ["a"], "remove_labels": None}, sort_keys=True
            )
            .encode()
        )
        .hexdigest()[:8]
    )
    assert entry.get("diff_hash") == expected_diff


def test_commit_window_limit(tmp_path: Path) -> None:
    logger = AuditLogger(tmp_path / "audit.log")
    dummy = DummyIM()
    hashes = [
        logger.log(
            "update_labels", {"issue": i, "add_labels": ["a"], "remove_labels": None}
        )
        for i in range(3)
    ]
    undo = UndoManager(dummy, logger, commit_window=2)
    # first hash should be out of window
    assert not undo.undo(hashes[0])
    assert undo.undo(hashes[2])
