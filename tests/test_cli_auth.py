from types import SimpleNamespace

from src.cli.main import cmd_auth
from src.core.secret_vault import SecretVault


class DummyResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}

    def json(self):
        return self._json


class DummyStorage:
    def __init__(self):
        self.token = None

    def store_token(self, *a, **kw):
        self.token = kw.get("token") or a[-1]

    def get_token(self, *a, **kw):
        return self.token


def test_cmd_auth_slack(monkeypatch, tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    vault.set_secret("slack_token", "tok")

    def dummy_post(url, headers=None, timeout=10):
        return DummyResponse(200, {"ok": True, "team": "workspace"})

    monkeypatch.setattr("requests.post", dummy_post)
    args = SimpleNamespace(action="slack", token=None, slack_token=None, install=False)
    assert cmd_auth(vault, args) == 0


def test_cmd_auth_login(tmp_path, monkeypatch):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")

    class DummyStorage:
        def store_token(self, *a, **kw):
            pass

        def get_token(self, *a, **kw):
            return None

    monkeypatch.setattr("src.cli.main.SecureTokenStorage", lambda: DummyStorage())
    args = SimpleNamespace(action="login", token="g", slack_token="s")
    assert cmd_auth(vault, args) == 0
    assert vault.get_secret("github_token") == "g"
    assert vault.get_secret("slack_token") == "s"


def test_cmd_auth_login_oauth(monkeypatch, tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")

    class DummyFlow:
        def __init__(self, cid):
            self.cid = cid

        def start_flow(self):
            return SimpleNamespace(
                device_code="d", user_code="u", verification_uri="http://u", interval=0
            )

        def poll_for_token(self, device_code: str, interval: int = 5):
            assert device_code == "d"
            return "tok"

    monkeypatch.setattr("src.cli.main.GitHubDeviceFlow", DummyFlow)
    monkeypatch.setattr("src.cli.main.SecureTokenStorage", lambda: DummyStorage())
    monkeypatch.setenv("GITHUB_CLIENT_ID", "cid")
    monkeypatch.setattr("src.cli.main.click.confirm", lambda *a, **kw: False)
    monkeypatch.setattr("src.cli.main.webbrowser.open", lambda *a, **kw: True)
    args = SimpleNamespace(action="login", token=None, slack_token=None)
    assert cmd_auth(vault, args) == 0
    assert vault.get_secret("github_token") == "tok"
