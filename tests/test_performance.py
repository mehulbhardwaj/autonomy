import os
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from src.cli.main import cmd_next


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
    assert time.time() - start < 3.0


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
