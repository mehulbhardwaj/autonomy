from src.core.models import Issue, WorkflowState
from src.core.platform import AutonomyPlatform, BaseWorkflow
from src.planning.config import PlanningConfig


class DummyWorkflow(BaseWorkflow):
    def _build_graph(self):
        return {"step": self.do_step}

    def do_step(self, state):
        state["done"] = True
        return state


def test_platform_and_workflow():
    platform = AutonomyPlatform()
    wf = platform.create_workflow(DummyWorkflow)
    result = wf.execute({"x": 1})
    assert result.success
    assert result.state.data["done"] is True


def test_models():
    issue = Issue(id="1", title="t", body="b")
    state = WorkflowState(issue_id="1")
    cfg = PlanningConfig()
    assert issue.title == "t"
    assert state.issue_id == "1"
    assert "priority_label" in cfg.ranking_weights
