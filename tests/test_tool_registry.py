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
