from pathlib import Path

from fastapi.testclient import TestClient

from src.api.server import create_app
from src.audit.logger import AuditLogger
from src.core.secret_vault import SecretVault


class DummyIssueManager:
    owner = "o"
    repo = "r"

    def list_issues(self, state="open"):
        return []


def test_settings_page(tmp_path: Path):
    dummy = DummyIssueManager()
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    app = create_app(dummy, audit_logger=AuditLogger(tmp_path / "log.txt"), vault=vault)
    client = TestClient(app)

    resp = client.get("/settings")
    assert resp.status_code == 200
    assert "<h1>Settings</h1>" in resp.text

    resp = client.post(
        "/api/v1/settings",
        data={
            "openrouter_api_key": "o",
            "mem0_url": "m",
            "github_token": "g",
            "slack_token": "s",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert vault.get_secret("openrouter_api_key") == "o"
    assert vault.get_secret("mem0_url") == "m"
    assert vault.get_secret("github_token") == "g"
    assert vault.get_secret("slack_token") == "s"
