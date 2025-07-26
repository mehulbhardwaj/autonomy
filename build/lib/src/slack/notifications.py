from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from .bot import SlackBot


@dataclass
class Issue:
    number: int
    title: str
    html_url: str
    stale_days: int = 0


@dataclass
class DuplicatePair:
    issue1: Issue
    issue2: Issue
    similarity: int


@dataclass
class BacklogFindings:
    stale_issues: List[Issue]
    duplicates: List[DuplicatePair]
    oversized: List[Issue]
    health_score: int


@dataclass
class WeeklyMetrics:
    week_start: datetime
    completed_issues: int
    avg_time_to_task: float
    approval_rate: int
    weekly_active_users: int


@dataclass
class UndoOperation:
    description: str
    actor: str
    hash: str


class NotificationTemplates:
    """Reusable Slack message formatting helpers."""

    @staticmethod
    def format_stale_issues(stale_issues: List[Issue]) -> Dict:
        issue_list = []
        for issue in stale_issues[:5]:
            issue_list.append(
                f"\u2022 <{issue.html_url}|#{issue.number}> - {issue.title} (stale for {issue.stale_days} days)"
            )
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*\U0001f578\ufe0f Stale Issues ({len(stale_issues)})*\n"
                + "\n".join(issue_list),
            },
        }

    @staticmethod
    def format_duplicates(duplicates: List[DuplicatePair]) -> Dict:
        duplicate_list = []
        for dup in duplicates[:3]:
            text = (
                f"\u2022 <{dup.issue1.html_url}|#{dup.issue1.number}>"
                f" \u2194 <{dup.issue2.html_url}|#{dup.issue2.number}>"
                f" ({dup.similarity}% similar)"
            )
            duplicate_list.append(text)
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*\U0001f501 Potential Duplicates ({len(duplicates)})*\n"
                + "\n".join(duplicate_list),
            },
        }


class BacklogDoctorNotifier:
    """Send backlog doctor reports to Slack."""

    def __init__(self, slack_client: SlackBot) -> None:
        self.slack_client = slack_client

    def send_nightly_report(self, channel: str, findings: BacklogFindings) -> bool:
        blocks: List[Dict] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "\U0001f3e5 Nightly Backlog Doctor Report",
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Stale Issues:* {len(findings.stale_issues)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Duplicates:* {len(findings.duplicates)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Oversized:* {len(findings.oversized)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Health Score:* {findings.health_score}%",
                    },
                ],
            },
        ]
        if findings.stale_issues:
            blocks.append(
                NotificationTemplates.format_stale_issues(findings.stale_issues)
            )
        if findings.duplicates:
            blocks.append(NotificationTemplates.format_duplicates(findings.duplicates))
        return self.slack_client.post_message(
            channel=channel,
            text="Nightly Backlog Doctor Report",
            blocks=blocks,
        )


class MetricsDashboard:
    """Send weekly metrics summaries."""

    def __init__(self, slack_client: SlackBot) -> None:
        self.slack_client = slack_client

    def send_weekly_metrics(self, channel: str, metrics: WeeklyMetrics) -> bool:
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "\U0001f4ca Weekly Team Metrics",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Week of {metrics.week_start.strftime('%B %d')}*",
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Issues Completed:* {metrics.completed_issues}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Avg Time to Task:* {metrics.avg_time_to_task}s",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Bot Approval Rate:* {metrics.approval_rate}%",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Weekly Active Users:* {metrics.weekly_active_users}",
                    },
                ],
            },
        ]
        return self.slack_client.post_message(
            channel=channel,
            text="Weekly Team Metrics",
            blocks=blocks,
        )


class SystemNotifier:
    """Send system related notifications."""

    def __init__(self, slack_client: SlackBot) -> None:
        self.slack_client = slack_client

    def send_undo_confirmation(self, channel: str, operation: UndoOperation) -> bool:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"\u2705 *Undo Operation Completed*\n{operation.description}",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Performed by: {operation.actor} | Hash: `{operation.hash}`",
                    }
                ],
            },
        ]
        return self.slack_client.post_message(
            channel=channel,
            text="Undo operation completed",
            blocks=blocks,
        )


class NotificationScheduler:
    """Minimal scheduler for Slack notifications."""

    def __init__(self, slack_client: SlackBot) -> None:
        self.slack_client = slack_client
        self.schedule: Dict[str, Dict[str, Any]] = {}

    def schedule_daily(
        self, name: str, time: str, func: Callable[[str], None], channel: str
    ) -> None:
        self.schedule[name] = {
            "frequency": "daily",
            "time": time,
            "func": func,
            "channel": channel,
            "next_run": datetime.now(),
        }

    def schedule_weekly(
        self, name: str, day: str, time: str, func: Callable[[str], None], channel: str
    ) -> None:
        self.schedule[name] = {
            "frequency": "weekly",
            "day": day,
            "time": time,
            "func": func,
            "channel": channel,
            "next_run": datetime.now(),
        }

    def run_scheduler(self, block: bool = False, interval: int = 60) -> None:
        """Run scheduled tasks once or in a loop when ``block`` is True."""

        def _run_due() -> None:
            now = datetime.now()
            for entry in self.schedule.values():
                if entry["next_run"] <= now:
                    entry["func"](entry["channel"])
                    if entry["frequency"] == "daily":
                        entry["next_run"] = now + timedelta(days=1)
                    else:
                        entry["next_run"] = now + timedelta(days=7)

        _run_due()
        while block:
            time.sleep(interval)
            _run_due()
