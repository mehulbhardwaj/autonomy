import hashlib
import hmac

from src.slack.commands import SlashCommandHandler
from src.slack.oauth import SlackOAuth, verify_slack_signature


class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data


def test_slack_oauth_get_install_url():
    oauth = SlackOAuth("cid", "secret")
    url = oauth.get_install_url()
    assert "client_id=cid" in url


def test_slack_oauth_exchange_code(monkeypatch):
    def dummy_post(url, data=None, timeout=10):
        assert url == "https://slack.com/api/oauth.v2.access"
        assert data["code"] == "abc"
        return DummyResponse({"ok": True, "access_token": "tok"})

    monkeypatch.setattr("requests.post", dummy_post)
    oauth = SlackOAuth("cid", "secret")
    data = oauth.exchange_code("abc")
    assert data["access_token"] == "tok"


def test_verify_slack_signature():
    secret = "sec"
    ts = "1"
    body = b"payload"
    sig = hmac.new(
        secret.encode(), f"v0:{ts}:payload".encode(), hashlib.sha256
    ).hexdigest()
    assert verify_slack_signature(ts, f"v0={sig}", body, secret)


def test_slash_command_handler_next():
    class DummyTM:
        def get_next_task(self, assignee=None, team=None):
            return {"number": 1, "title": "task"}

        def update_task(self, *a, **kw):
            return True

    handler = SlashCommandHandler(DummyTM())
    resp = handler.handle_command("/autonomy next", {})
    assert "Next task" in resp["text"]
