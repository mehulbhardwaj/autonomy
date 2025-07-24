from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Dict


class MetricsStorage:
    """Store metrics data on disk."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = Path(storage_path) / "metrics"
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def store_daily_metrics(self, repository: str, metrics: Dict) -> None:
        """Persist metrics, filtering personal data."""
        safe_metrics = self.filter_personal_data(metrics)
        safe_repo = repository.replace("/", "-")
        filename = f"{safe_repo}_{metrics['date']}.json"
        with open(self.storage_path / filename, "w", encoding="utf-8") as f:
            json.dump(safe_metrics, f, default=str)

    def filter_personal_data(self, metrics: Dict) -> Dict:
        """Remove personal identifiers while keeping useful aggregates."""
        safe = metrics.copy()
        if "loc_per_contributor" in safe:
            safe["loc_per_assignee"] = mean(list(safe["loc_per_contributor"].values()))
            del safe["loc_per_contributor"]
        return safe
