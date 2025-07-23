from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..core.models import WorkflowResult
from ..core.platform import BaseWorkflow
from ..tasks.ranking import RankingEngine
from .config import PlanningConfig


class PlanningWorkflow(BaseWorkflow):
    """Simplified planning workflow."""

    def __init__(
        self,
        memory,
        llm,
        github,
        slack,
        config: PlanningConfig | None = None,
        model_selector=None,
    ):
        self.config = config or PlanningConfig()
        self.ranking = RankingEngine()
        self.model_selector = model_selector
        super().__init__(memory, llm, github, slack)

    # ------------------------------------------------------------------
    def _build_graph(self):
        return {
            "analyze_issue": self.analyze_issue,
            "rank_priority": self.rank_priority,
            "decompose": self.decompose,
            "route": self.route,
            "assign": self.assign,
            "plan": self.plan,
            "get_approval": self.get_human_approval,
            "approve": self.approve,
        }

    # Steps -------------------------------------------------------------
    def analyze_issue(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze issue using memory context and LLM."""
        title = state.get("title", "")
        repo = state.get("repository", "default")
        context = self.memory.search(
            f"similar:{title}", filter_metadata={"repository": repo}
        )
        prompt = f"Analyze {title}. Context: {context}"
        models = (
            self.model_selector.get("analysis")
            if self.model_selector
            else ["openai/gpt-4o"]
        )
        analysis = self.llm.complete_with_fallback(
            [{"role": "user", "content": prompt}],
            models=models,
            operation="analysis",
        )
        state["analysis"] = analysis or f"analysis of {title}"
        return state

    def rank_priority(self, state: Dict[str, Any]) -> Dict[str, Any]:
        issue = {
            "labels": state.get("labels", []),
            "created_at": state.get("created_at"),
        }
        score = self.ranking.score_issue(issue)
        state["priority_score"] = score
        return state

    def decompose(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Break down work using LLM and store in memory."""
        analysis = state.get("analysis", "")
        models = (
            self.model_selector.get("decomposition")
            if self.model_selector
            else ["openai/gpt-4o"]
        )
        text = self.llm.complete_with_fallback(
            [{"role": "user", "content": f"Decompose: {analysis}"}],
            models=models,
            operation="decomposition",
        )
        tasks = [t.strip() for t in text.split(";") if t.strip()] or ["task1"]
        state["tasks"] = tasks
        self.memory.add(
            {
                f"tasks:{state.get('title','')}": text,
                "repository": state.get("repository", "default"),
            }
        )
        return state

    def route(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine additional workflows needed."""
        analysis = state.get("analysis", "").lower()
        state["requires_security_review"] = any(
            k in analysis for k in ["auth", "security", "token"]
        )
        state["requires_docs"] = any(k in analysis for k in ["api", "public"])
        return state

    def assign(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest assignment based on team data in memory."""
        repo = state.get("repository", "default")
        members = self.memory.search(
            "team_members", filter_metadata={"repository": repo}
        )
        if isinstance(members, str):
            choices = [m.strip() for m in members.split(",") if m.strip()]
        else:
            choices = []
        state["assignee"] = choices[0] if choices else "alice"
        return state

    def plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final plan description."""
        tasks = ", ".join(state.get("tasks", []))
        models = (
            self.model_selector.get("planning")
            if self.model_selector
            else ["openai/gpt-4o"]
        )
        plan = self.llm.complete_with_fallback(
            [{"role": "user", "content": f"Plan for: {tasks}"}],
            models=models,
            operation="planning",
        )
        state["plan"] = plan or "basic plan"
        return state

    def get_human_approval(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prompt the user for approval."""
        import click

        approved = click.confirm("Approve generated plan?", default=True)
        state["approved"] = approved
        return state

    def approve(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Record approval and learn outcome."""
        if "approved" not in state:
            state = self.get_human_approval(state)

        if state.get("approved"):
            self.memory.add(
                {
                    "last_plan": state.get("plan", ""),
                    "repository": state.get("repository", "default"),
                }
            )
        return state

    def learn_from_override(
        self,
        issue_id: str,
        ai_decision: Dict[str, Any],
        human_decision: Dict[str, Any],
        repository: str = "default",
    ) -> None:
        """Record a human override of the AI's plan."""
        self.memory.add(
            {
                "type": "human_override",
                "issue_id": issue_id,
                "ai_decision": str(ai_decision),
                "human_decision": str(human_decision),
                "timestamp": datetime.now().isoformat(),
                "repository": repository,
            }
        )

    # Public API -------------------------------------------------------
    def run(self, issue: Dict[str, Any]) -> WorkflowResult:
        result = self.execute(issue)
        result.requires_security_review = result.state.data.get(
            "requires_security_review", False
        )
        result.has_code_changes = True
        return result
