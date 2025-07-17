from pathlib import Path
from types import SimpleNamespace

from src.cli.main import (
    cmd_board_init,
    cmd_init,
    cmd_list,
    cmd_next,
    cmd_process,
    cmd_setup,
    cmd_status,
    cmd_update,
)


class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._data


class DummyManager:
    def __init__(self, workspace: Path):
        self.owner = "owner"
        self.repo = "repo"
        self.workspace_path = workspace
        self.github_token = "token"
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


def test_cmd_next(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)

    class DummyTM:
        def get_next_task(self, assignee=None, team=None):
            return {"number": 7, "title": "task"}

    monkeypatch.setattr(
        "src.tasks.task_manager.TaskManager", lambda *a, **kw: DummyTM()
    )
    args = SimpleNamespace(assignee=None, team=None)
    assert cmd_next(manager, args) == 0


def test_cmd_update(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)

    class DummyTM:
        def __init__(self):
            self.called = None

        def update_task(self, issue_number, status=None, done=False, notes=None):
            self.called = (issue_number, status, done, notes)
            return True

    dummy = DummyTM()
    monkeypatch.setattr("src.tasks.task_manager.TaskManager", lambda *a, **kw: dummy)
    args = SimpleNamespace(issue=3, status="in-progress", done=False, notes=None)
    assert cmd_update(manager, args) == 0
    assert dummy.called == (3, "in-progress", False, None)


def test_cmd_next_none(monkeypatch, tmp_path: Path, capsys):
    manager = DummyManager(tmp_path)

    class DummyTM:
        def get_next_task(self, assignee=None, team=None):
            return None

    monkeypatch.setattr(
        "src.tasks.task_manager.TaskManager", lambda *a, **kw: DummyTM()
    )
    args = SimpleNamespace(assignee=None, team=None)
    assert cmd_next(manager, args) == 0
    out = capsys.readouterr().out
    assert "No tasks found" in out


def test_cmd_list(monkeypatch, tmp_path: Path, capsys):
    manager = DummyManager(tmp_path)

    class DummyTM:
        def list_tasks(self, assignee=None, team=None):
            return [
                {"number": 1, "title": "task a"},
                {"number": 2, "title": "task b"},
            ]

    monkeypatch.setattr(
        "src.tasks.task_manager.TaskManager", lambda *a, **kw: DummyTM()
    )
    args = SimpleNamespace(assignee=None, team=None, mine=False)
    assert cmd_list(manager, args) == 0
    out = capsys.readouterr().out
    assert "#1" in out and "task a" in out


def test_cmd_board_init(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)

    calls = []

    def dummy_post(url, headers=None, json=None, timeout=10):
        query = json["query"]
        calls.append(query)
        if "RepoProjects" in query:
            return DummyResponse(
                {"data": {"repository": {"id": "rid", "projectsV2": {"nodes": []}}}}
            )
        if "CreateProject" in query:
            return DummyResponse(
                {"data": {"createProjectV2": {"projectV2": {"id": "pid"}}}}
            )
        if "GetFields" in query:
            return DummyResponse({"data": {"node": {"fields": {"nodes": []}}}})
        if "CreateField" in query:
            return DummyResponse(
                {"data": {"createProjectV2Field": {"projectV2Field": {"id": "fid"}}}}
            )
        if "FieldOptions" in query:
            return DummyResponse({"data": {"node": {"options": {"nodes": []}}}})
        if "AddFieldOption" in query:
            return DummyResponse(
                {
                    "data": {
                        "addProjectV2FieldOption": {
                            "projectV2SingleSelectFieldOption": {"id": "oid"}
                        }
                    }
                }
            )
        return DummyResponse({"data": {}})

    monkeypatch.setattr("requests.post", dummy_post)
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    args = SimpleNamespace()
    assert cmd_board_init(manager, args) == 0
    assert any("CreateProject" in q for q in calls)
