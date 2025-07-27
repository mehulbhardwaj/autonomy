from requests.models import Response

from src.github.board_manager import GraphQLClient
from src.github.client import ResilientGitHubClient


def test_resilient_client_rate_limit(monkeypatch):
    client = ResilientGitHubClient()

    def fake_request(method, url, **kwargs):
        resp = Response()
        resp.status_code = 200
        resp._content = b"{}"
        resp.headers["X-RateLimit-Limit"] = "5000"
        resp.headers["X-RateLimit-Remaining"] = "4999"
        return resp

    monkeypatch.setattr(client.session, "request", fake_request)
    resp = client.make_request("GET", "http://example.com")
    assert resp.status_code == 200
    assert client.rate_limit_info["X-RateLimit-Limit"] == "5000"
    assert client.rate_limit_info["X-RateLimit-Remaining"] == "4999"


def test_graphql_client_cache(monkeypatch):
    calls = []

    def fake_make_request(self, method, url, **kwargs):
        calls.append(1)
        resp = Response()
        resp.status_code = 200
        resp._content = b'{"data": {"ok": true}}'
        resp.headers["X-RateLimit-Remaining"] = "1"
        self.rate_limit_info = {
            "X-RateLimit-Remaining": "1",
            "X-RateLimit-Limit": "5000",
        }
        return resp

    monkeypatch.setattr(ResilientGitHubClient, "make_request", fake_make_request)
    client = GraphQLClient("t", cache_ttl=10)
    assert client.execute("query", {"v": 1}) == {"ok": True}
    assert client.execute("query", {"v": 1}) == {"ok": True}
    assert len(calls) == 1
    assert client.rate_limit_info["X-RateLimit-Remaining"] == "1"
