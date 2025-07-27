from requests.models import Response

from src.core.errors import GitHubAPIError, handle_errors
from src.github.client import ResilientGitHubClient


def test_handle_errors_decorator(capsys):
    @handle_errors
    def boom():
        raise GitHubAPIError("fail", suggestion="check token")

    assert boom() == 1
    out = capsys.readouterr().out
    assert "GitHub API Error" in out
    assert "check token" in out


def test_resilient_github_client(monkeypatch):
    client = ResilientGitHubClient()
    called = {}

    def fake_request(method, url, **kwargs):
        called["method"] = method
        called["url"] = url
        resp = Response()
        resp.status_code = 200
        return resp

    monkeypatch.setattr(client.session, "request", fake_request)
    result = client.make_request("GET", "http://example.com")
    assert result.status_code == 200
    assert called["method"] == "GET"
    assert "example.com" in called["url"]
