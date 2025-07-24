from datetime import date
from pathlib import Path

from src.metrics import MetricsCollector, MetricsStorage


class DummyGitHub:
    def get_open_issues_count(self, repo: str) -> int:
        assert repo == "owner/repo"
        return 5

    def calculate_time_to_task(self) -> float:
        return 4.2

    def calculate_loc_per_assignee(self) -> int:
        return 320

    def calculate_sprint_completion(self) -> float:
        return 75.0


class DummyAudit:
    def count_command_usage(self, cmd: str) -> int:
        assert cmd == "plan"
        return 3

    def count_human_overrides(self) -> int:
        return 1

    def count_approvals(self, days: int = 7) -> int:
        return 8

    def count_ai_recommendations(self, days: int = 7) -> int:
        return 10

    def weekly_active_users(self) -> int:
        return 5


class DummySlack:
    def __init__(self) -> None:
        self.posted = []

    def post_message(self, channel: str, text: str, blocks=None):
        self.posted.append((channel, text))
        return True


def test_metrics_collection_and_storage(tmp_path: Path) -> None:
    gh = DummyGitHub()
    audit = DummyAudit()
    slack = DummySlack()
    storage = MetricsStorage(tmp_path)
    collector = MetricsCollector(gh, slack, audit, storage)

    report = collector.collect_daily_metrics("owner/repo")
    assert "Daily Team Metrics" in report
    files = list((tmp_path / "metrics").glob("*.json"))
    assert files


def test_storage_filters_personal_data(tmp_path: Path) -> None:
    storage = MetricsStorage(tmp_path)
    metrics = {
        "date": date.today(),
        "repository": "owner/repo",
        "loc_per_contributor": {"a": 100, "b": 200},
    }
    storage.store_daily_metrics("owner/repo", metrics)
    stored = next((tmp_path / "metrics").glob("*.json")).read_text()
    assert "loc_per_contributor" not in stored
    assert "loc_per_assignee" in stored
