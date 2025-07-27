import os
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from src.cli.main import cmd_next
from src.tasks.pinned_items import PinnedItemsStore
from src.tasks.task_manager import TaskManager


class DummyTM:
    def get_next_task(self, assignee=None, team=None, explain=False):
        return (
            {
                "number": 1,
                "title": "t",
                "labels": [],
                "created_at": "2025-01-01T00:00:00Z",
            },
            {},
        )

    def _score_issue(self, issue, explain=False):
        return 1.0


@pytest.mark.usefixtures("tmp_path")
def test_cli_startup_time():
    start = time.time()
    env = {
        **os.environ,
        "POSTHOG_DISABLED": "1",
        "MEM0_TELEMETRY": "False",
    }
    env.pop("COVERAGE_PROCESS_START", None)
    subprocess.run(
        [sys.executable, "-m", "src.cli.main", "--help"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
        env=env,
    )
    assert time.time() - start < 7.0


@pytest.mark.usefixtures("tmp_path")
def test_next_command_performance(monkeypatch):
    monkeypatch.setattr(
        "src.tasks.task_manager.TaskManager", lambda *a, **kw: DummyTM()
    )
    manager = SimpleNamespace(github_token="t", owner="o", repo="r")
    start = time.time()
    rc = cmd_next(manager, SimpleNamespace(assignee=None, team=None))
    duration = time.time() - start
    assert rc == 0
    assert duration < 3.0


def test_get_next_task_large_repo_performance(monkeypatch):
    """Ensure TaskManager can handle large numbers of issues quickly."""

    issues = [
        {
            "number": i,
            "title": f"t{i}",
            "labels": [],
            "created_at": "2025-01-01T00:00:00Z",
        }
        for i in range(1000)
    ]

    class LargeDummyIM:
        def list_issues(self, state="open"):
            return issues

    tm = TaskManager.__new__(TaskManager)
    tm.issue_manager = LargeDummyIM()
    tm.pinned_store = PinnedItemsStore()
    tm.project_id = "o/r"
    tm.ranking = SimpleNamespace(score_issue=lambda *a, **kw: 1.0)
    tm.sync_cooldown = 0
    tm._last_sync = 0
    tm.audit_logger = None

    start = time.time()
    issue = tm.get_next_task()
    duration = time.time() - start

    assert issue is not None
    assert duration < 1.0
