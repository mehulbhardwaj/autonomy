from pathlib import Path
from types import SimpleNamespace

import src.cli.main as main
from src.cli.main import (
    cmd_audit,
    cmd_board_init,
    cmd_completion,
    cmd_doctor,
    cmd_doctor_nightly,
    cmd_init,
    cmd_interactive,
    cmd_list,
    cmd_metrics_daily,
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
from src.core.secret_vault import SecretVault


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
            issue = {
                "number": 7,
                "title": "task",
                "labels": [],
                "created_at": "2025-07-10T00:00:00Z",
            }
            breakdown = {"priority": 3, "age_penalty": 0}
            return (issue, breakdown) if explain else issue

        def _score_issue(self, issue, explain=False):
            return 5

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

        def _score_issue(self, issue, explain=False):  # pragma: no cover - not called
            return 0

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


def test_cmd_board_init_arg_cache(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)
    captured = {}

    class DummyBM:
        def __init__(self, token, owner, repo, cache_path=None):
            captured["path"] = cache_path

        def init_board(self):
            return {}

    monkeypatch.setattr("src.github.board_manager.BoardManager", DummyBM)

    via_arg = tmp_path / "via_arg.json"
    args = SimpleNamespace(cache=str(via_arg))
    assert cmd_board_init(manager, args) == 0
    assert Path(captured["path"]) == via_arg


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


def test_cmd_doctor_nightly(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)

    class DummyScheduler:
        def __init__(self, bot):
            self.called = False
            self.slack_client = bot

        def schedule_daily(self, name, time, func, channel):
            func(channel)
            self.called = True

        def run_scheduler(self, block=False):
            pass

    class DummyBot:
        pass

    class DummyDoctor:
        def __init__(self, mgr, slack=None):
            pass

        def run_nightly_diagnosis(self, channel="#c"):
            return {}

    monkeypatch.setattr("src.tasks.backlog_doctor.BacklogDoctor", DummyDoctor)
    monkeypatch.setattr("src.slack.notifications.NotificationScheduler", DummyScheduler)
    monkeypatch.setattr("src.slack.bot.SlackBot", DummyBot)

    args = SimpleNamespace(
        doctor_cmd="nightly",
        repos=["owner/repo"],
        channel="#c",
        time="02:00",
        slack_token="t",
        forever=False,
    )
    assert cmd_doctor_nightly(manager, SecretVault(), args) == 0


def test_cmd_metrics_daily(monkeypatch, tmp_path: Path):
    manager = DummyManager(tmp_path)

    class DummyService:
        def __init__(self, mapping, token, slack_token, run_time="09:00", **kw):
            self.called = False

        def run(self, forever=False):
            self.called = True

    monkeypatch.setattr("src.tasks.metrics_service.DailyMetricsService", DummyService)

    args = SimpleNamespace(
        repos=["owner/repo"],
        channel="#m",
        time="09:00",
        slack_token="t",
        forever=False,
    )
    assert cmd_metrics_daily(manager, SecretVault(), args) == 0


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


def test_cmd_completion(tmp_path: Path, capsys):
    parser = main.build_parser()
    args = SimpleNamespace(shell="bash")
    assert cmd_completion(parser, args) == 0
    out = capsys.readouterr().out
    assert "register-python-argcomplete" in out


def test_cmd_interactive(monkeypatch, tmp_path: Path, capsys):
    manager = DummyManager(tmp_path)
    parser = main.build_parser()
    inputs = iter(["help", "quit"])
    monkeypatch.setattr("builtins.input", lambda *a: next(inputs))
    monkeypatch.setattr(main, "_dispatch_command", lambda *a, **kw: 0)
    assert cmd_interactive(manager, parser) == 0
    out = capsys.readouterr().out
    assert "Interactive Shell" in out
