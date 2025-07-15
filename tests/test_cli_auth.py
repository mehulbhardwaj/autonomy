from types import SimpleNamespace

import pytest

from src.cli.main import cmd_auth
from src.core.secret_vault import SecretVault


class DummyResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}

    def json(self):
        return self._json


def test_cmd_auth_slack(monkeypatch, tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    vault.set_secret("slack_token", "tok")

    def dummy_post(url, headers=None, timeout=10):
        return DummyResponse(200, {"ok": True, "team": "workspace"})

    monkeypatch.setattr("requests.post", dummy_post)
    args = SimpleNamespace(action="slack", token=None, slack_token=None)
    assert cmd_auth(vault, args) == 0


def test_cmd_auth_login(tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    args = SimpleNamespace(action="login", token="g", slack_token="s")
    assert cmd_auth(vault, args) == 0
    assert vault.get_secret("github_token") == "g"
    assert vault.get_secret("slack_token") == "s"
