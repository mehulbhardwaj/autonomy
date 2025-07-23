from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from langgraph.graph import StateGraph

from ..core.models import WorkflowResult, WorkflowState
from ..planning.workflow import PlanningWorkflow


class PlanningState(TypedDict, total=False):
    title: str
    labels: List[str]
    created_at: str
    repository: str
    analysis: str
    priority_score: float
    tasks: List[str]
    requires_security_review: bool
    requires_docs: bool
    assignee: str
    plan: str
    approved: bool


class LangGraphPlanningWorkflow(PlanningWorkflow):
    """Planning workflow implemented with LangGraph."""

    def _build_graph(self):
        graph = StateGraph(PlanningState)

        graph.add_node("analyze_issue", self.analyze_issue)
        graph.add_node("rank_priority", self.rank_priority)
        graph.add_node("decompose", self.decompose)
        graph.add_node("route", self.route)
        graph.add_node("assign", self.assign)
        graph.add_node("plan", self.plan)
        graph.add_node("get_human_approval", self.get_human_approval)
        graph.add_node("approve", self.approve)

        graph.set_entry_point("analyze_issue")
        graph.add_edge("analyze_issue", "rank_priority")
        graph.add_edge("rank_priority", "decompose")
        graph.add_edge("decompose", "route")
        graph.add_edge("route", "assign")
        graph.add_edge("assign", "plan")
        graph.add_edge("plan", "get_human_approval")
        graph.add_edge("get_human_approval", "approve")
        graph.set_finish_point("approve")

        return graph.compile()

    # ------------------------------------------------------------------
    def execute(self, state: Dict[str, Any]) -> WorkflowResult:
        try:
            result_state = self.graph.invoke(state)
            success = True
        except Exception:
            result_state = state
            success = False
        return WorkflowResult(success=success, state=WorkflowState(data=result_state))
