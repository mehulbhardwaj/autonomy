from src.github.token_storage import (
    SecureTokenStorage,
    refresh_token_if_needed,
)


class DummyKeyring:
    def __init__(self):
        self.storage = {}

    def set_password(self, service, user, token):
        self.storage[(service, user)] = token

    def get_password(self, service, user):
        return self.storage.get((service, user))


class DummyFlow:
    def __init__(self, cid):
        self.cid = cid
        self.started = False

    def start_flow(self):
        self.started = True
        return type(
            "Resp",
            (),
            {
                "device_code": "d",
                "user_code": "u",
                "verification_uri": "http://x",
                "interval": 0,
            },
        )

    def poll_for_token(self, device_code: str, interval: int = 5):
        assert device_code == "d"
        return "new"


def test_secure_token_storage(monkeypatch):
    kr = DummyKeyring()
    monkeypatch.setitem(__import__("sys").modules, "keyring", kr)
    storage = SecureTokenStorage(service_name="svc")
    storage.store_token("user", "tok")
    assert storage.get_token("user") == "tok"


def test_refresh_token(monkeypatch):
    monkeypatch.setattr("src.github.token_storage.validate_token", lambda t: False)

    calls = []

    class Resp:
        def __init__(self, data):
            self.status_code = 200
            self._data = data

        def json(self):
            return self._data

    def dummy_post(url, data=None, headers=None, timeout=10):
        calls.append(1)
        if "device" in url:
            return Resp(
                {
                    "device_code": "d",
                    "user_code": "u",
                    "verification_uri": "http://u",
                    "interval": 0,
                }
            )
        return Resp({"access_token": "new"})

    monkeypatch.setattr("httpx.post", dummy_post)
    token = refresh_token_if_needed("old", "cid")
    assert token == "new"
