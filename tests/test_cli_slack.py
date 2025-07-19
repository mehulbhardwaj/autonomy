from types import SimpleNamespace

from src.cli.main import cmd_auth, cmd_slack
from src.core.secret_vault import SecretVault


class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._data


def test_cmd_auth_slack_install(monkeypatch, tmp_path, capsys):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    monkeypatch.setenv("SLACK_CLIENT_ID", "cid")
    args = SimpleNamespace(action="slack", token=None, slack_token=None, install=True)
    assert cmd_auth(vault, args) == 0
    out = capsys.readouterr().out
    assert "https://slack.com/oauth/v2/authorize" in out


def test_cmd_auth_slack_token(tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    args = SimpleNamespace(action="slack", token=None, slack_token="tok", install=False)
    assert cmd_auth(vault, args) == 0
    assert vault.get_secret("slack_token") == "tok"


def test_cmd_slack_test(monkeypatch, tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    vault.set_secret("slack_token", "tok")

    def dummy_post(url, headers=None, timeout=10):
        return DummyResponse({"ok": True})

    monkeypatch.setattr("requests.post", dummy_post)
    args = SimpleNamespace(slack_cmd="test", token=None)
    assert cmd_slack(vault, args) == 0


def test_cmd_slack_channels(monkeypatch, tmp_path, capsys):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    vault.set_secret("slack_token", "tok")

    def dummy_get(url, headers=None, timeout=10):
        return DummyResponse({"ok": True, "channels": [{"id": "C", "name": "gen"}]})

    monkeypatch.setattr("requests.get", dummy_get)
    args = SimpleNamespace(slack_cmd="channels", token=None)
    assert cmd_slack(vault, args) == 0
    out = capsys.readouterr().out
    assert "gen" in out


def test_cmd_slack_notify(monkeypatch, tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    vault.set_secret("slack_token", "tok")

    def dummy_post(url, json=None, headers=None, timeout=10):
        return DummyResponse({"ok": True})

    monkeypatch.setattr("requests.post", dummy_post)
    args = SimpleNamespace(slack_cmd="notify", token=None, channel="C", message="hello")
    assert cmd_slack(vault, args) == 0
