import pytest

from src.slack import get_slack_auth_info


class DummyResponse:
    def __init__(self, status_code=200, ok=True, data=None):
        self.status_code = status_code
        self._data = {"ok": ok}
        if data:
            self._data.update(data)

    def json(self):
        return self._data


def test_get_slack_auth_info(monkeypatch):
    def dummy_post(url, headers=None, timeout=10):
        assert url == "https://slack.com/api/auth.test"
        return DummyResponse(data={"user": "u", "team": "workspace"})

    monkeypatch.setattr("requests.post", dummy_post)
    info = get_slack_auth_info("token")
    assert info["user"] == "u"
    assert info["team"] == "workspace"


def test_get_slack_auth_info_error(monkeypatch):
    def dummy_post(url, headers=None, timeout=10):
        return DummyResponse(ok=False, data={"error": "bad_auth"})

    monkeypatch.setattr("requests.post", dummy_post)
    with pytest.raises(ValueError):
        get_slack_auth_info("token")
