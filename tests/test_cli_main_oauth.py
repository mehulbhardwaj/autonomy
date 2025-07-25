import sys
from types import SimpleNamespace

from src.cli import main
from src.core.secret_vault import SecretVault


class DummyStorage:
    def __init__(self):
        self.token = None

    def store_token(self, *a, **kw):
        self.token = kw.get("token") or a[-1]

    def get_token(self, *a, **kw):
        return self.token


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


class DummyManager:
    def __init__(self, github_token, owner, repo, workspace_path, config, **kw):
        self.github_token = github_token
        self.owner = owner
        self.repo = repo
        self.workspace_path = workspace_path
        self.config = config

    def setup_repository(self):
        pass


def test_main_auto_oauth(monkeypatch, tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    monkeypatch.setattr(main, "SecretVault", lambda: vault)
    storage = DummyStorage()
    monkeypatch.setattr(main, "SecureTokenStorage", lambda: storage)
    monkeypatch.setattr(main, "GitHubDeviceFlow", DummyFlow)
    monkeypatch.setattr(main, "WorkflowManager", DummyManager)
    monkeypatch.setattr(main, "_create_library_template", lambda p: None)
    monkeypatch.setattr(main.click, "confirm", lambda *a, **kw: False)
    monkeypatch.setattr(main.webbrowser, "open", lambda *a, **kw: True)
    monkeypatch.setattr(main, "refresh_token_if_needed", lambda t, c: t)
    monkeypatch.setattr(main, "validate_github_token_scopes", lambda *a, **kw: True)
    monkeypatch.setenv("GITHUB_CLIENT_ID", "cid")
    sys.argv = ["prog", "--owner", "o", "--repo", "r", "init"]
    assert main.main() == 0
    assert vault.get_secret("github_token") == "tok"
