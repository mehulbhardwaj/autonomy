from types import SimpleNamespace
from pathlib import Path

import pytest

from src.cli.main import cmd_init, cmd_process, cmd_setup, cmd_status


class DummyManager:
    def __init__(self, workspace: Path):
        self.owner = "owner"
        self.repo = "repo"
        self.workspace_path = workspace
        self.setup_called = False
        self.process_issue_called_with = None

    def setup_repository(self):
        self.setup_called = True

    def process_issue(self, issue_number: int):
        self.process_issue_called_with = issue_number
        return {"status": "completed", "phases_completed": ["pm_agent"]}


def test_cmd_setup_success(tmp_path: Path):
    manager = DummyManager(tmp_path)
    args = SimpleNamespace(skip_docs=False)
    assert cmd_setup(manager, args) == 0
    assert manager.setup_called


def test_cmd_setup_error(tmp_path: Path):
    manager = DummyManager(tmp_path)

    def fail():
        raise RuntimeError("boom")

    manager.setup_repository = fail
    args = SimpleNamespace(skip_docs=False)
    assert cmd_setup(manager, args) == 1


def test_cmd_process_success(tmp_path: Path):
    manager = DummyManager(tmp_path)
    args = SimpleNamespace(issue=1)
    assert cmd_process(manager, args) == 0
    assert manager.process_issue_called_with == 1


def test_cmd_process_error(tmp_path: Path):
    manager = DummyManager(tmp_path)
    manager.process_issue = lambda n: {"error": "bad"}
    args = SimpleNamespace(issue=1)
    assert cmd_process(manager, args) == 1


def test_cmd_init_success(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)
    monkeypatch.setattr("src.cli.main._create_web_template", lambda p: None)
    monkeypatch.setattr("src.cli.main._create_api_template", lambda p: None)
    monkeypatch.setattr("src.cli.main._create_cli_template", lambda p: None)
    monkeypatch.setattr("src.cli.main._create_library_template", lambda p: None)
    args = SimpleNamespace(template="web")
    assert cmd_init(manager, args) == 0
    assert manager.setup_called


def test_cmd_init_error(tmp_path: Path):
    manager = DummyManager(tmp_path)

    def fail():
        raise RuntimeError("boom")

    manager.setup_repository = fail
    args = SimpleNamespace(template="web")
    assert cmd_init(manager, args) == 1


def test_cmd_status(tmp_path: Path):
    manager = DummyManager(tmp_path)
    args = SimpleNamespace(issue=None)
    assert cmd_status(manager, args) == 0
    args_issue = SimpleNamespace(issue=5)
    assert cmd_status(manager, args_issue) == 0
