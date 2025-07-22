import httpx

from src.llm.openrouter import OpenRouterClient


class DummyResp:
    def __init__(self, status, data):
        self.status_code = status
        self._data = data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=None)

    def json(self):
        return self._data


def test_fallback_and_cost(monkeypatch):
    calls = []

    def dummy_post(self, url, json=None, headers=None):
        calls.append(json["model"])
        if json["model"] == "m1":
            raise httpx.HTTPError("boom")
        return DummyResp(
            200,
            {
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 7},
            },
        )

    monkeypatch.setattr(httpx.Client, "post", dummy_post)
    client = OpenRouterClient(api_key="key")
    result = client.complete_with_fallback(
        [{"role": "user", "content": "hi"}], ["m1", "m2"], operation="analysis"
    )
    assert result == "ok"
    assert calls == ["m1", "m2"]
    assert client.costs["analysis"]["prompt_tokens"] == 3
    assert client.costs["analysis"]["completion_tokens"] == 7
