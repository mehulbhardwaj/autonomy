from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from src.audit.logger import AuditLogger


class ToolRegistry:
    """Registry for tools with basic permission validation."""

    def __init__(self, audit_logger: Optional[AuditLogger] = None) -> None:
        self._tools: Dict[str, Any] = {}
        self._permissions: Dict[str, str] = {}
        self.audit_logger = audit_logger

    def register_tool(self, name: str, tool: Any, permission: str = "read") -> None:
        """Register ``tool`` with required ``permission``."""
        self._tools[name] = tool
        self._permissions[name] = permission

    def execute_tool(
        self,
        name: str,
        action: str,
        *,
        agent: Any,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Execute a tool action with permission and audit checks."""
        params = params or {}
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        required = self._permissions.get(name, "read")
        agent_perms = set(getattr(agent, "permissions", []))
        levels = {"read": 0, "write": 1, "admin": 2}
        req_level = levels.get(required, 0)
        agent_level = max((levels.get(p, 0) for p in agent_perms), default=-1)
        if agent_level < req_level:
            raise PermissionError(f"Agent lacks permission for {name}")

        tool = self._tools[name]
        func: Callable = getattr(tool, action)
        success = True
        try:
            result = func(**params)
            return result
        except Exception as e:  # pragma: no cover - unexpected errors
            success = False
            error = str(e)
            raise
        finally:
            if self.audit_logger:
                details = {
                    "tool": name,
                    "action": action,
                    "agent": getattr(agent, "id", None),
                    "params": params,
                    "success": success,
                }
                if not success:
                    details["error"] = error
                self.audit_logger.log("tool_execute", details)
