from pathlib import Path
from types import SimpleNamespace

from src.cli.main import cmd_explain, cmd_memory, cmd_plan, cmd_tune
from src.core.config import WorkflowConfig


class DummyIssueManager:
    def __init__(self):
        self.issues = {42: {"labels": [], "created_at": "2025-07-10T00:00:00Z"}}

    def get_issue(self, num):
        return self.issues.get(num)


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


def test_cmd_plan(tmp_path: Path):
    manager = DummyManager(tmp_path)
    args = SimpleNamespace(issue=42)
    assert cmd_plan(manager, args) == 0


def test_cmd_explain(tmp_path: Path, capsys):
    manager = DummyManager(tmp_path)
    args = SimpleNamespace(issue=42)
    assert cmd_explain(manager, args) == 0
    out = capsys.readouterr().out
    assert "Score" in out


def test_cmd_tune(tmp_path: Path):
    manager = DummyManager(tmp_path)
    args = SimpleNamespace(weights=["priority_label=1.0"])
    assert cmd_tune(manager, args) == 0
    assert Path(".autonomy.yml").exists()
    Path(".autonomy.yml").unlink()


def test_cmd_memory(tmp_path: Path, capsys, monkeypatch):
    manager = DummyManager(tmp_path)
    args = SimpleNamespace()

    class DummyMem:
        def __init__(self):
            self.store = {"default": {"k": "v"}}

    class DummyPlatform:
        def __init__(self):
            self.memory = DummyMem()

    monkeypatch.setattr("src.core.platform.AutonomyPlatform", DummyPlatform)
    assert cmd_memory(manager, args) == 0
    out = capsys.readouterr().out
    assert "Repository: default" in out
    assert "k: v" in out
