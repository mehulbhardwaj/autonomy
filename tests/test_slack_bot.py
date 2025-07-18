from src.slack.bot import SlackBot


class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data


def test_post_message_success(monkeypatch):
    def dummy_post(url, json=None, headers=None, timeout=10):
        assert url.endswith("/chat.postMessage")
        assert json["channel"] == "C"
        assert json["text"] == "hi"
        return DummyResponse({"ok": True})

    monkeypatch.setattr("requests.post", dummy_post)
    bot = SlackBot("tok")
    assert bot.post_message("C", "hi")


def test_post_message_failure(monkeypatch):
    def dummy_post(url, json=None, headers=None, timeout=10):
        return DummyResponse({"ok": False}, status_code=400)

    monkeypatch.setattr("requests.post", dummy_post)
    bot = SlackBot("tok")
    assert not bot.post_message("C", "hi")
