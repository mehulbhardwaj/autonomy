from pathlib import Path
from types import SimpleNamespace

from src.cli.main import cmd_assign, cmd_breakdown, cmd_rerank
from src.core.config import WorkflowConfig


class DummyIssueManager:
    def __init__(self):
        self.issues = {
            42: {"title": "t", "labels": [], "created_at": "2025-07-10T00:00:00Z"}
        }
        self.assigned = None

    def get_issue(self, num):
        return self.issues.get(num)

    def assign_issue(self, num, assignees):
        self.assigned = (num, assignees)
        return True


class DummyManager:
    def __init__(self, tmp_path: Path):
        self.owner = "o"
        self.repo = "r"
        self.github_token = "t"
        self.workspace_path = tmp_path
        self.config = WorkflowConfig()
        self.issue_manager = DummyIssueManager()
        from src.audit.logger import AuditLogger

        self.audit_logger = AuditLogger(tmp_path / "audit.log", use_git=True)


def test_cmd_assign(tmp_path: Path):
    manager = DummyManager(tmp_path)
    args = SimpleNamespace(issue=42, to="bob")
    assert cmd_assign(manager, args) == 0
    assert manager.issue_manager.assigned == (42, ["bob"])


def test_cmd_breakdown(monkeypatch, tmp_path: Path, capsys):
    manager = DummyManager(tmp_path)
    args = SimpleNamespace(issue=42)

    class DummyWF:
        def decompose(self, state):
            state["tasks"] = ["a", "b"]
            return state

    class DummyPlatform:
        def create_workflow(self, _):
            return DummyWF()

    monkeypatch.setattr("src.core.platform.AutonomyPlatform", DummyPlatform)
    assert cmd_breakdown(manager, args) == 0
    out = capsys.readouterr().out
    assert "- a" in out and "- b" in out


def test_cmd_rerank(monkeypatch, tmp_path: Path, capsys):
    manager = DummyManager(tmp_path)

    class DummyTM:
        def __init__(self, *a, **kw):
            from src.tasks.ranking import RankingEngine

            self.ranking = RankingEngine()

        def list_tasks(self):
            return [
                {
                    "number": 1,
                    "title": "t",
                    "labels": [],
                    "created_at": "2025-07-10T00:00:00Z",
                }
            ]

    monkeypatch.setattr("src.tasks.task_manager.TaskManager", DummyTM)
    args = SimpleNamespace()
    assert cmd_rerank(manager, args) == 0
    out = capsys.readouterr().out
    assert "#1" in out
