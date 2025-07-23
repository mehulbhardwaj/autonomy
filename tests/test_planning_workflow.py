import click
import pytest

from src.core.platform import AutonomyPlatform
from src.planning.workflow import PlanningWorkflow


def test_planning_workflow_run():
    platform = AutonomyPlatform()
    wf = platform.create_workflow(PlanningWorkflow)
    issue = {
        "title": "Add login",
        "labels": ["priority-high"],
        "created_at": "2025-07-10T00:00:00Z",
        "repository": "default",
    }
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(click, "confirm", lambda *a, **k: True)
    result = wf.run(issue)
    monkeypatch.undo()
    data = result.state.data
    assert result.success
    assert data["analysis"].startswith("LLM:")
    assert "priority_score" in data
    assert data["approved"]
    assert platform.memory.store["default"].get("last_plan")


def test_security_routing_and_assignment():
    platform = AutonomyPlatform()
    platform.memory.add({"team_members": "bob", "repository": "default"})
    wf = platform.create_workflow(PlanningWorkflow)
    issue = {
        "title": "Fix auth token leak",
        "labels": ["bug"],
        "created_at": "2025-07-10T00:00:00Z",
        "repository": "default",
    }
    result = wf.run(issue)
    data = result.state.data
    assert data["requires_security_review"]
    assert data["assignee"] == "bob"
