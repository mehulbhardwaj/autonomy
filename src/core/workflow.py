from __future__ import annotations

from typing import Any, Callable, Dict

from .models import WorkflowResult, WorkflowState

StateGraph = Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]


class BaseWorkflow:
    """Minimal workflow with sequential step execution."""

    def __init__(self, memory, llm, github, slack):
        self.memory = memory
        self.llm = llm
        self.github = github
        self.slack = slack
        self.graph = self._build_graph()

    # ------------------------------------------------------------------
    def _build_graph(self) -> StateGraph:  # pragma: no cover - abstract
        raise NotImplementedError

    # ------------------------------------------------------------------
    def execute(self, state: Dict[str, Any]) -> WorkflowResult:
        current = state.copy()
        for step, func in self.graph.items():
            current = func(current)
        return WorkflowResult(success=True, state=WorkflowState(data=current))
