from __future__ import annotations

from typing import Dict

from ..github.issue_manager import IssueManager
from ..slack.bot import SlackBot
from ..slack.notifications import NotificationScheduler
from .backlog_doctor import BacklogDoctor


class NightlyDoctorService:
    """Run BacklogDoctor on multiple repositories nightly."""

    def __init__(
        self,
        repo_channels: Dict[str, str],
        github_token: str,
        slack_token: str,
        run_time: str = "02:00",
    ) -> None:
        self.scheduler = NotificationScheduler(SlackBot(slack_token))
        for repo, channel in repo_channels.items():
            owner, name = repo.split("/")
            manager = IssueManager(github_token, owner, name)
            doctor = BacklogDoctor(manager, self.scheduler.slack_client)
            self.scheduler.schedule_daily(
                name=repo,
                time=run_time,
                func=lambda c=channel, d=doctor: d.run_nightly_diagnosis(channel=c),
                channel=channel,
            )

    def run(self, forever: bool = False) -> None:
        """Execute scheduled runs."""
        self.scheduler.run_scheduler(block=forever)
