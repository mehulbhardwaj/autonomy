import hashlib
import hmac
import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.api import create_app
from src.audit.logger import AuditLogger


class DummyIssueManager:
    def __init__(self):
        self.owner = "o"
        self.repo = "r"


def _sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return "sha256=" + digest


def test_github_webhook(tmp_path: Path) -> None:
    secret = "s3"
    overrides = tmp_path / "ovr.log"
    log = tmp_path / "log"
    app = create_app(
        DummyIssueManager(),
        AuditLogger(log),
        webhook_secret=secret,
        overrides_path=overrides,
    )
    client = TestClient(app)

    payload = {"action": "edited", "issue": {"number": 1}}
    body = json.dumps(payload).encode()
    headers = {
        "X-Hub-Signature-256": _sign(secret, body),
        "X-GitHub-Event": "issues",
    }
    r = client.post("/webhook/github", data=body, headers=headers)
    assert r.status_code == 200
    data = overrides.read_text().strip().splitlines()
    assert len(data) == 1
    entry = json.loads(data[0])
    assert entry["event"] == "issues"
    assert entry["payload"]["action"] == "edited"
    logs = list(AuditLogger(log).iter_logs())
    assert logs and logs[0]["operation"] == "github_webhook"


def test_webhook_bad_signature(tmp_path: Path) -> None:
    secret = "s3"
    overrides = tmp_path / "ovr.log"
    app = create_app(
        DummyIssueManager(),
        AuditLogger(tmp_path / "log"),
        webhook_secret=secret,
        overrides_path=overrides,
    )
    client = TestClient(app)
    body = b"{}"
    r = client.post(
        "/webhook/github", data=body, headers={"X-Hub-Signature-256": "wrong"}
    )
    assert r.status_code == 400


def test_webhook_rate_limit(tmp_path: Path) -> None:
    secret = "s3"
    overrides = tmp_path / "ovr.log"
    app = create_app(
        DummyIssueManager(),
        AuditLogger(tmp_path / "log"),
        webhook_secret=secret,
        overrides_path=overrides,
        webhook_rate_limit=2,
    )
    client = TestClient(app)
    body = json.dumps({}).encode()
    headers = {"X-Hub-Signature-256": _sign(secret, body)}
    assert client.post("/webhook/github", data=body, headers=headers).status_code == 200
    assert client.post("/webhook/github", data=body, headers=headers).status_code == 200
    assert client.post("/webhook/github", data=body, headers=headers).status_code == 429


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
    body = json.dumps(payload).encode()
    headers = {
        "X-Hub-Signature-256": _sign(secret, body),
        "X-GitHub-Event": "issues",
    }
    assert client.post("/webhook/github", data=body, headers=headers).status_code == 200
    assert called.get("count", 0) == 1


def test_overrides_webhook(tmp_path: Path) -> None:
    overrides = tmp_path / "ovr.log"
    log = tmp_path / "log"
    app = create_app(
        DummyIssueManager(),
        AuditLogger(log, overrides_path=overrides),
        overrides_path=overrides,
    )
    client = TestClient(app)

    payload = {"field": "priority", "value": "high"}
    resp = client.post("/webhook/overrides", json=payload)
    assert resp.status_code == 200
    data = overrides.read_text().strip().splitlines()
    assert len(data) == 1
    entry = json.loads(data[0])
    assert entry["event"] == "override"
    assert entry["payload"]["field"] == "priority"
    logger = AuditLogger(log, overrides_path=overrides)
    assert logger.count_human_overrides() == 1
