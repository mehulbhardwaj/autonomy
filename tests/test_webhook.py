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
    app = create_app(
        DummyIssueManager(),
        AuditLogger(tmp_path / "log"),
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
