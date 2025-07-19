from pathlib import Path
from types import SimpleNamespace

from src.cli.main import (
    cmd_audit,
    cmd_board_init,
    cmd_doctor,
    cmd_init,
    cmd_list,
    cmd_next,
    cmd_pin,
    cmd_process,
    cmd_setup,
    cmd_status,
    cmd_undo,
    cmd_unpin,
    cmd_update,
)
from src.core.config import WorkflowConfig


class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._data


class DummyIssueManager:
    def __init__(self):
        self.labels = None
        self.state = None
        self.comment = None
        self.issues = {5: {"title": "t"}}

    def update_issue_labels(self, issue_number, add_labels=None, remove_labels=None):
        self.labels = (issue_number, add_labels, remove_labels)
        return True

    def update_issue_state(self, issue_number, state):
        self.state = (issue_number, state)
        return True

    def add_comment(self, issue_number, comment):
        self.comment = (issue_number, comment)
        return True

    def get_issue(self, issue_number):
        return self.issues.get(issue_number)


class DummyManager:
    def __init__(self, workspace: Path):
        self.owner = "owner"
        self.repo = "repo"
        self.workspace_path = workspace
        self.github_token = "token"
        self.setup_called = False
        self.process_issue_called_with = None
        self.config = WorkflowConfig(board_cache_path=str(workspace / "cache.json"))
        from src.audit.logger import AuditLogger

        self.audit_logger = AuditLogger(workspace / "audit.log", use_git=True)
        self.issue_manager = DummyIssueManager()

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
        def get_next_task(self, assignee=None, team=None, explain=False):
            if explain:
                return {"number": 7, "title": "task"}, {"priority": 3, "age_penalty": 0}
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
        def get_next_task(self, assignee=None, team=None, explain=False):
            return (None, {}) if explain else None

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
    args = SimpleNamespace(assignee=None, team=None, mine=False, pinned=False)
    assert cmd_list(manager, args) == 0
    out = capsys.readouterr().out
    assert "#1" in out and "task a" in out


def test_cmd_board_init(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)
    captured = {}

    class DummyBM:
        def __init__(self, token, owner, repo, cache_path=None):
            captured["path"] = cache_path

        def init_board(self):
            return {}

    monkeypatch.setattr("src.github.board_manager.BoardManager", DummyBM)

    args = SimpleNamespace()
    assert cmd_board_init(manager, args) == 0
    assert Path(captured["path"]) == Path(manager.config.board_cache_path)


def test_cmd_board_init_custom_path(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)
    custom = tmp_path / "custom.json"
    manager.config.board_cache_path = str(custom)
    captured = {}

    class DummyBM:
        def __init__(self, token, owner, repo, cache_path=None):
            captured["path"] = cache_path

        def init_board(self):
            Path(captured["path"]).write_text("{}")
            return {}

    monkeypatch.setattr("src.github.board_manager.BoardManager", DummyBM)

    args = SimpleNamespace()
    assert cmd_board_init(manager, args) == 0
    assert Path(captured["path"]) == custom
    assert custom.exists()


def test_cmd_doctor_run(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)
    manager.issue_manager = object()

    class DummyDoctor:
        def __init__(self, mgr):
            pass

        def run(self, **kwargs):
            return {"stale": [1], "duplicates": [], "oversized": []}

    monkeypatch.setattr("src.tasks.backlog_doctor.BacklogDoctor", DummyDoctor)
    args = SimpleNamespace(
        doctor_cmd="run",
        stale_days=14,
        checklist_limit=10,
        stale=False,
        duplicates=False,
        oversized=False,
    )
    assert cmd_doctor(manager, args) == 0


def test_cmd_audit_and_undo(tmp_path: Path):
    manager = DummyManager(tmp_path)
    # simulate an operation by logging directly
    h = manager.audit_logger.log(
        "update_labels", {"issue": 1, "add_labels": ["a"], "remove_labels": None}
    )
    args_log = SimpleNamespace(audit_cmd="log")
    assert cmd_audit(manager, args_log) == 0
    args_undo = SimpleNamespace(hash=h, last=False)
    assert cmd_undo(manager, args_undo) == 0
    assert manager.issue_manager.labels == (1, [], ["a"])


def test_cmd_pin_unpin_and_list(monkeypatch, tmp_path: Path, capsys):
    manager = DummyManager(tmp_path)

    args_pin = SimpleNamespace(issue=5)
    assert cmd_pin(manager, args_pin) == 0
    args_list = SimpleNamespace(assignee=None, team=None, mine=False, pinned=True)
    assert cmd_list(manager, args_list) == 0
    out = capsys.readouterr().out
    assert "#5" in out
    args_unpin = SimpleNamespace(issue=5)
    assert cmd_unpin(manager, args_unpin) == 0
