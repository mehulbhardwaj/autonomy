from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowState:
    """State shared between workflow steps."""

    data: Dict[str, Any] = field(default_factory=dict)
    issue_id: Optional[str] = None
    human_approval_needed: bool = False
    next_workflows: List[str] = field(default_factory=list)


@dataclass
class WorkflowResult:
    """Result returned by workflow execution."""

    success: bool
    state: WorkflowState
    outputs: Dict[str, Any] = field(default_factory=dict)
    next_action: Optional[str] = None
    requires_security_review: bool = False
    has_code_changes: bool = False


@dataclass
class Issue:
    id: str
    title: str
    body: str
    labels: List[str] = field(default_factory=list)
    assignee: Optional[str] = None
    milestone: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TeamContext:
    repository: str
    team_members: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    workflow_settings: Dict[str, Any] = field(default_factory=dict)
