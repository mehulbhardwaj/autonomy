from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except Exception:  # pragma: no cover - yaml optional
    yaml = None


@dataclass
class RankingConfig:
    """Configuration for task ranking."""

    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "priority_field": 100.0,
            "sprint_proximity": 3.0,
            "issue_age": 1.0,
            "pinned_boost": 1000.0,
        }
    )
    priority_mapping: Dict[str, int] = field(
        default_factory=lambda: {
            "priority-critical": 4,
            "priority-high": 3,
            "priority-medium": 2,
            "priority-low": 1,
        }
    )
    excluded_labels: List[str] = field(default_factory=lambda: ["blocked"])

    def load_from_file(self, path: Path) -> None:
        """Update configuration from YAML file if present."""
        if not path.exists() or yaml is None:
            return
        try:
            data = yaml.safe_load(path.read_text()) or {}
        except Exception:
            return
        self.weights.update(data.get("weights", {}))
        self.priority_mapping.update(data.get("priority_mapping", {}))
        if "excluded_labels" in data:
            self.excluded_labels = list(data["excluded_labels"])


class RankingEngine:
    """Multi-signal ranking engine for issues."""

    def __init__(self, config: Optional[RankingConfig] = None) -> None:
        self.config = config or RankingConfig()

    # ------------------------------------------------------------------
    def score_issue(
        self, issue: Dict[str, Any], *, pinned: bool = False, explain: bool = False
    ) -> float | tuple[float, Dict[str, Any]]:
        labels = [
            lab["name"] if isinstance(lab, dict) and "name" in lab else lab
            for lab in issue.get("labels", [])
        ]
        if (
            any(lbl in self.config.excluded_labels for lbl in labels)
            or issue.get("state") == "closed"
        ):
            return (float("-inf"), {}) if explain else float("-inf")

        w = self.config.weights
        priority = 0
        for lbl in labels:
            priority = max(priority, self.config.priority_mapping.get(lbl, 0))

        sprint_score = 0
        milestone = issue.get("milestone")
        if isinstance(milestone, dict) and milestone.get("due_on"):
            try:
                due = datetime.fromisoformat(milestone["due_on"].replace("Z", "+00:00"))
                days = (due - datetime.now(timezone.utc)).days
                sprint_score = max(0, 30 - days)
            except Exception:
                pass

        age_days = 0
        created = issue.get("created_at")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - dt).days
            except Exception:
                pass

        score = 0.0
        score += priority * w.get("priority_field", 100)
        score += sprint_score * w.get("sprint_proximity", 3)
        score -= age_days * w.get("issue_age", 1)
        if pinned:
            score += w.get("pinned_boost", 1000)

        if explain:
            return (
                score,
                {
                    "priority": priority,
                    "sprint_proximity": sprint_score,
                    "age_penalty": age_days,
                    "pinned": pinned,
                },
            )
        return score
