from pathlib import Path

from src.audit.logger import AuditLogger
from src.audit.undo import UndoManager


class DummyIM:
    def __init__(self):
        self.labels = None
        self.pr = None
        self.comment = None

    def update_issue_labels(self, issue_number, add_labels=None, remove_labels=None):
        self.labels = (issue_number, add_labels, remove_labels)
        return True

    def create_pull_request(self, title, body, head, base="main"):
        self.pr = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        }
        return 1

    def add_comment(self, issue_number, comment):
        self.comment = (issue_number, comment)
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


def test_shadow_branch_pr(tmp_path: Path) -> None:
    logger = AuditLogger(tmp_path / "audit.log", use_git=True)
    dummy = DummyIM()
    logger.log(
        "update_labels", {"issue": 1, "add_labels": ["a"], "remove_labels": None}
    )
    logger.log("update_state", {"issue": 2, "new": "closed"})
    logs = list(logger.iter_logs())
    undo = UndoManager(dummy, logger)
    pr = undo.create_shadow_branch_pr(logs)
    assert pr == 1
    assert dummy.pr and dummy.pr["head"].startswith("shadow-")
    diff_hash = dummy.pr["head"].split("shadow-")[1]
    import subprocess

    files = subprocess.check_output(
        [
            "git",
            "-C",
            str(tmp_path),
            "ls-tree",
            "-r",
            "--name-only",
            f"shadow-{diff_hash}",
        ],
        text=True,
    )
    assert f"undo_{diff_hash}.json" in files


def test_embed_diff_hash(tmp_path: Path) -> None:
    logger = AuditLogger(tmp_path / "audit.log")
    dummy = DummyIM()
    undo = UndoManager(dummy, logger)
    assert undo.embed_diff_hash(2, "abcd1234")
    assert dummy.comment == (2, "diff-hash: `abcd1234`")
