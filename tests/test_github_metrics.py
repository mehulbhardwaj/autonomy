from datetime import datetime

import pytest

from src.github.issue_manager import IssueManager


class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._data


def test_issue_manager_metrics(monkeypatch):
    events_called = []

    def dummy_get(url, headers=None, params=None):
        if url.endswith("/issues") and params.get("state") in {"open", "all"}:
            return DummyResponse(
                [{"number": 1, "created_at": datetime.utcnow().isoformat()}]
            )
        if url.endswith("/issues") and params.get("since"):
            return DummyResponse(
                [
                    {
                        "user": {"login": "a"},
                        "number": 1,
                        "created_at": datetime.utcnow().isoformat(),
                    }
                ]
            )
        if url.endswith("/milestones"):
            return DummyResponse([{"closed_issues": 3, "open_issues": 1}])
        if "/events" in url:
            events_called.append(url)
            return DummyResponse(
                [{"event": "assigned", "created_at": datetime.utcnow().isoformat()}]
            )
        return DummyResponse([])

    monkeypatch.setattr("requests.get", dummy_get)

    mgr = IssueManager("t", "o", "r")
    assert mgr.get_open_issues_count("o/r") == 1
    assert mgr.weekly_active_users() >= 0
    assert mgr.calculate_sprint_completion() == pytest.approx(75.0)
    assert mgr.calculate_time_to_task() >= 0
    assert events_called
