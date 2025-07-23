from pathlib import Path

import pytest

from src.audit.logger import AuditLogger
from src.tools import ToolRegistry


class DummyTool:
    def __init__(self) -> None:
        self.called_with = None

    def do(self, value: int) -> int:
        self.called_with = value
        return value * 2


class DummyAgent:
    def __init__(self, agent_id: str, permissions: list[str]):
        self.id = agent_id
        self.permissions = permissions


def test_permission_enforcement(tmp_path: Path) -> None:
    registry = ToolRegistry(audit_logger=AuditLogger(tmp_path / "audit.log"))
    tool = DummyTool()
    registry.register_tool("dummy", tool, permission="write")
    agent = DummyAgent("a1", ["read"])
    with pytest.raises(PermissionError):
        registry.execute_tool("dummy", "do", agent=agent, params={"value": 1})


def test_audit_logging(tmp_path: Path) -> None:
    registry = ToolRegistry(audit_logger=AuditLogger(tmp_path / "audit.log"))
    tool = DummyTool()
    registry.register_tool("dummy", tool, permission="write")
    agent = DummyAgent("a2", ["write"])
    result = registry.execute_tool("dummy", "do", agent=agent, params={"value": 2})
    assert result == 4
    entries = list(registry.audit_logger.iter_logs())
    assert len(entries) == 1
    entry = entries[0]
    assert entry["details"]["tool"] == "dummy"
    assert entry["details"]["agent"] == "a2"
    assert entry["details"]["success"] is True


def test_admin_permission_and_error_logging(tmp_path: Path) -> None:
    registry = ToolRegistry(audit_logger=AuditLogger(tmp_path / "audit.log"))

    class FailingTool:
        def do(self) -> None:
            raise RuntimeError("boom")

    registry.register_tool("failing", FailingTool(), permission="admin")
    agent_write = DummyAgent("aw", ["write"])
    with pytest.raises(PermissionError):
        registry.execute_tool("failing", "do", agent=agent_write)

    agent_admin = DummyAgent("aa", ["admin"])
    with pytest.raises(RuntimeError):
        registry.execute_tool("failing", "do", agent=agent_admin)

    logs = list(registry.audit_logger.iter_logs())
    assert len(logs) == 1
    entry = logs[0]
    assert entry["details"]["tool"] == "failing"
    assert entry["details"]["agent"] == "aa"
    assert entry["details"]["success"] is False
    assert "boom" in entry["details"]["error"]
