from src.core.platform import AutonomyPlatform
from src.planning.langgraph_workflow import LangGraphPlanningWorkflow


def test_langgraph_workflow_run():
    platform = AutonomyPlatform()
    wf = platform.create_workflow(LangGraphPlanningWorkflow)
    issue = {
        "title": "Add login",
        "labels": ["priority-high"],
        "created_at": "2025-07-10T00:00:00Z",
        "repository": "default",
    }
    result = wf.run(issue)
    data = result.state.data
    assert result.success
    assert data["analysis"].startswith("LLM:")
    assert "priority_score" in data
    assert data["approved"]
    assert platform.memory.store["default"].get("last_plan")


class FailingWorkflow(LangGraphPlanningWorkflow):
    def plan(self, state):
        raise RuntimeError("boom")


def test_langgraph_error_handling():
    platform = AutonomyPlatform()
    wf = platform.create_workflow(FailingWorkflow)
    issue = {"title": "t", "labels": [], "created_at": "", "repository": "default"}
    result = wf.run(issue)
    assert not result.success
    assert result.state.data["title"] == "t"
