from __future__ import annotations

from pathlib import Path
from typing import Dict

from ..audit.logger import AuditLogger
from ..github.issue_manager import IssueManager
from ..metrics import MetricsCollector, MetricsStorage
from ..slack.bot import SlackBot
from ..slack.notifications import NotificationScheduler


class DailyMetricsService:
    """Schedule daily metrics collection and Slack reporting."""

    def __init__(
        self,
        repo_channels: Dict[str, str],
        github_token: str,
        slack_token: str,
        run_time: str = "09:00",
        *,
        storage_path: Path | str = Path("metrics"),
        log_path: Path | str = Path("audit.log"),
    ) -> None:
        self.scheduler = NotificationScheduler(SlackBot(slack_token))
        for repo, channel in repo_channels.items():
            owner, name = repo.split("/")
            manager = IssueManager(github_token, owner, name)
            audit = AuditLogger(Path(log_path))
            storage = MetricsStorage(Path(storage_path))
            collector = MetricsCollector(
                manager, self.scheduler.slack_client, audit, storage
            )
            self.scheduler.schedule_daily(
                name=repo,
                time=run_time,
                func=lambda ch=channel, c=collector, r=repo: c.send_daily_report(r, ch),
                channel=channel,
            )

    def run(self, forever: bool = False) -> None:
        """Execute scheduled metrics reports."""
        self.scheduler.run_scheduler(block=forever)
