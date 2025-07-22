from src.utils.distribution import check_for_updates, verify_installation


def test_verify_installation():
    assert verify_installation()


def test_check_for_updates(monkeypatch):
    logs = []

    class Resp:
        def __init__(self, version):
            self._version = version

        def json(self):
            return {"info": {"version": self._version}}

        def raise_for_status(self):
            pass

    def dummy_get(url, timeout=5):
        return Resp("9.9.9")

    monkeypatch.setattr("httpx.get", dummy_get)
    monkeypatch.setattr(
        "builtins.print", lambda *a, **k: logs.append(" ".join(map(str, a)))
    )

    check_for_updates()
    assert any("Update available" in line for line in logs)
