from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from src.api import create_app
from src.audit.logger import AuditLogger


class DummyIssueManager:
    def __init__(self, issues):
        self._issues = issues
        self.updated = None
        self.state_update = None
        self.comment = None

    def list_issues(self, state="open"):
        return self._issues

    def update_issue_labels(self, issue_number, add_labels=None, remove_labels=None):
        self.updated = (issue_number, add_labels, remove_labels)
        return True

    def update_issue_state(self, issue_number, state):
        self.state_update = (issue_number, state)
        return True

    def add_comment(self, issue_number, comment):
        self.comment = (issue_number, comment)
        return True


def _make_issue(num, prio, days=0):
    return {
        "number": num,
        "title": f"Issue {num}",
        "labels": [{"name": prio}],
        "created_at": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),
    }


def test_tasks_endpoints():
    issues = [_make_issue(1, "priority-low", 5), _make_issue(2, "priority-high", 1)]
    dummy = DummyIssueManager(issues)
    app = create_app(dummy, audit_logger=AuditLogger(Path("test_audit.log")))
    client = TestClient(app)

    resp = client.get("/api/v1/tasks/next")
    assert resp.status_code == 200
    assert resp.json()["number"] == 2

    resp = client.post(
        "/api/v1/tasks/1/update",
        json={"status": "in-progress", "done": True, "notes": "x"},
    )
    assert resp.status_code == 200
    assert dummy.updated == (1, ["in-progress"], None)
    assert dummy.state_update == (1, "closed")
    assert dummy.comment == (1, "x")


def test_backlog_doctor_endpoint(tmp_path):
    body = "\n".join(["- [ ] item" for _ in range(12)])
    issues = [
        {
            "number": 1,
            "title": "T",
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
            "body": body,
        },
    ]
    dummy = DummyIssueManager(issues)
    app = create_app(dummy, audit_logger=AuditLogger(tmp_path / "log.txt"))
    client = TestClient(app)

    resp = client.post("/api/v1/backlog/doctor/run")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stale"] == [1]
    assert data["oversized"] == [1]
