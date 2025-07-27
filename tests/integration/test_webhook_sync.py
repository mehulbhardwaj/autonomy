import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.api import create_app
from src.audit.logger import AuditLogger


class DummyIssueManager:
    def __init__(self):
        self.owner = "o"
        self.repo = "r"


def test_webhook_triggers_sync(tmp_path: Path, monkeypatch) -> None:
    secret = "s3"
    overrides = tmp_path / "ovr.log"
    log = tmp_path / "log"
    called = {}

    def fake_sync(self):
        called.setdefault("count", 0)
        called["count"] += 1

    monkeypatch.setattr(
        "src.tasks.task_manager.TaskManager._trigger_sync",
        fake_sync,
    )
    app = create_app(
        DummyIssueManager(),
        AuditLogger(log),
        webhook_secret=secret,
        overrides_path=overrides,
    )
    client = TestClient(app)
    payload = {"action": "labeled", "issue": {"number": 1}}
    import hashlib
    import hmac

    body = json.dumps(payload).encode()
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {
        "X-Hub-Signature-256": "sha256=" + sig,
        "X-GitHub-Event": "issues",
    }
    resp = client.post("/webhook/github", data=body, headers=headers)
    assert resp.status_code == 200
    assert called.get("count", 0) == 1
