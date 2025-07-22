from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PlanningConfig:
    """Repository specific planning configuration."""

    ranking_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "priority_label": 0.4,
            "sprint_proximity": 0.3,
            "issue_age": 0.1,
            "dependency_urgency": 0.2,
        }
    )
    team_preferences: Dict[str, str] = field(default_factory=dict)
