from pathlib import Path

from fastapi.testclient import TestClient

from src.api import create_app
from src.audit.logger import AuditLogger


class DummyIssueManager:
    def __init__(self, logger: AuditLogger):
        self.owner = "o"
        self.repo = "r"
        self.logger = logger
        self.labels = None
        self.state = None
        self.comment = None

    def list_issues(self, state="open"):
        return [{"number": 1, "title": "T", "labels": []}]

    def update_issue_labels(self, issue_number, add_labels=None, remove_labels=None):
        self.logger.log(
            "update_labels",
            {
                "issue": issue_number,
                "add_labels": add_labels,
                "remove_labels": remove_labels,
            },
        )
        self.labels = (issue_number, add_labels, remove_labels)
        return True

    def update_issue_state(self, issue_number, state):
        self.logger.log(
            "update_state",
            {"issue": issue_number, "previous": "open"},
        )
        self.state = (issue_number, state)
        return True

    def add_comment(self, issue_number, comment):
        self.logger.log(
            "add_comment",
            {"issue": issue_number, "comment": comment},
        )
        self.comment = (issue_number, comment)
        return True


def test_update_and_undo(tmp_path: Path):
    log_path = tmp_path / "audit.log"
    logger = AuditLogger(log_path)
    dummy = DummyIssueManager(logger)
    app = create_app(dummy, audit_logger=logger)
    client = TestClient(app)

    r = client.post(
        "/api/v1/tasks/1/update",
        json={"status": "in-progress", "done": True, "notes": "note"},
    )
    assert r.status_code == 200

    logs = client.get("/api/v1/audit/log").json()
    assert len(logs) >= 3
    h = logs[0]["hash"]

    r = client.post(f"/api/v1/audit/undo/{h}")
    assert r.status_code == 200
    assert dummy.labels == (1, [], ["in-progress"])

    logs = client.get("/api/v1/audit/log").json()
    assert logs[-1]["operation"] == "undo_operation"
