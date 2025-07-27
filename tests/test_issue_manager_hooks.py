from src.github.issue_manager import IssueManager
from src.tasks.task_manager import TaskManager


class DummyResponse:
    status_code = 200

    def json(self):
        return {}


def _dummy_patch(*args, **kwargs):
    return DummyResponse()


def test_on_change_called_update_labels(monkeypatch):
    called = {}
    mgr = IssueManager(
        "t",
        "o",
        "r",
        on_change=lambda: called.setdefault("cnt", 0)
        or called.update(cnt=called["cnt"] + 1),
    )
    monkeypatch.setattr(mgr, "get_issue", lambda n: {"labels": []})
    monkeypatch.setattr("requests.patch", _dummy_patch)
    assert mgr.update_issue_labels(1, add_labels=["x"]) is True
    assert called.get("cnt", 0) == 1


def test_on_change_called_update_state(monkeypatch):
    called = {}
    mgr = IssueManager(
        "t",
        "o",
        "r",
        on_change=lambda: called.setdefault("cnt", 0)
        or called.update(cnt=called["cnt"] + 1),
    )
    monkeypatch.setattr("requests.patch", _dummy_patch)
    assert mgr.update_issue_state(1, "closed") is True
    assert called.get("cnt", 0) == 1


def test_task_manager_auto_sync_on_issue_update(monkeypatch):
    called = {}
    tm = TaskManager("t", "o", "r")
    tm.sync_cooldown = 0
    tm._last_sync = 0
    monkeypatch.setattr(tm.issue_manager, "get_issue", lambda n: {"labels": []})
    monkeypatch.setattr("requests.patch", _dummy_patch)

    def fake_sync(self):
        called.setdefault("cnt", 0)
        called["cnt"] += 1
        return {"created": [], "orphans": []}

    monkeypatch.setattr(
        "src.tasks.hierarchy_manager.HierarchyManager.maintain_hierarchy",
        fake_sync,
    )
    import types

    monkeypatch.setattr(
        "threading.Thread",
        lambda target, daemon=False: types.SimpleNamespace(start=lambda: target()),
    )
    tm.issue_manager.update_issue_labels(1, add_labels=["x"])
    assert called.get("cnt", 0) == 1
