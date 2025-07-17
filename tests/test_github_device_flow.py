from src.github.device_flow import DeviceFlowResponse, GitHubDeviceFlow


class DummyResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        return self._data


def test_start_flow(monkeypatch):
    def dummy_post(url, data=None, headers=None, timeout=10):
        assert "client_id" in data
        return DummyResponse(
            200,
            {
                "device_code": "d",
                "user_code": "u",
                "verification_uri": "https://github.com/device",
                "interval": 5,
            },
        )

    monkeypatch.setattr("requests.post", dummy_post)
    flow = GitHubDeviceFlow("cid")
    resp = flow.start_flow()
    assert isinstance(resp, DeviceFlowResponse)
    assert resp.user_code == "u"
    assert resp.device_code == "d"


def test_poll_for_token(monkeypatch):
    calls = []

    def dummy_post(url, data=None, headers=None, timeout=10):
        calls.append(1)
        if len(calls) < 2:
            return DummyResponse(200, {"error": "authorization_pending"})
        return DummyResponse(200, {"access_token": "tok"})

    monkeypatch.setattr("requests.post", dummy_post)
    monkeypatch.setattr("time.sleep", lambda x: None)
    flow = GitHubDeviceFlow("cid")
    token = flow.poll_for_token("d", interval=0)
    assert token == "tok"
    assert len(calls) >= 2
