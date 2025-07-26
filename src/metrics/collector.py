from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..audit.logger import AuditLogger
from ..slack.bot import SlackBot
from .storage import MetricsStorage


class MetricsCollector:
    """Collect basic team metrics and generate Slack reports."""

    def __init__(
        self,
        github_client: Any,
        slack_client: SlackBot,
        audit_logger: AuditLogger,
        storage: MetricsStorage,
    ) -> None:
        self.github = github_client
        self.slack = slack_client
        self.audit = audit_logger
        self.storage = storage

    # ------------------------------------------------------------------
    def collect_daily_metrics(self, repository: str) -> str:
        """Collect metrics, store them and return a Slack report."""
        metrics = {
            "date": datetime.now().date(),
            "repository": repository,
            "time_to_task_avg": self.calculate_time_to_task(),
            "approval_rate": self.calculate_approval_rate(),
            "weekly_active_users": self.calculate_wau(),
            "loc_per_assignee": self.calculate_loc_per_assignee(),
            "sprint_completion_rate": self.calculate_sprint_completion(),
            "open_issues_count": self.github.get_open_issues_count(repository),
            "orphan_issues_count": self.calculate_orphan_count(),
            "planning_commands_used": self.audit.count_command_usage("plan"),
            "human_overrides_count": self.audit.count_human_overrides(),
        }
        self.storage.store_daily_metrics(repository, metrics)
        return self.generate_slack_report(metrics)

    def send_daily_report(self, repository: str, channel: str) -> bool:
        """Collect metrics and post the report to Slack."""
        report = self.collect_daily_metrics(repository)
        return self.slack.post_message(channel, report)

    # ------------------------------------------------------------------
    def calculate_time_to_task(self) -> float:
        func = getattr(self.github, "calculate_time_to_task", lambda: 0.0)
        return float(func())

    def calculate_wau(self) -> int:
        if hasattr(self.audit, "weekly_active_users"):
            return int(self.audit.weekly_active_users())
        func = getattr(self.github, "weekly_active_users", lambda: 0)
        return int(func())

    def calculate_loc_per_assignee(self) -> int:
        func = getattr(self.github, "calculate_loc_per_assignee", lambda: 0)
        return int(func())

    def calculate_sprint_completion(self) -> float:
        func = getattr(self.github, "calculate_sprint_completion", lambda: 0.0)
        return float(func())

    def calculate_orphan_count(self) -> int:
        from ..tasks.hierarchy_manager import HierarchyManager

        hm = HierarchyManager(self.github)
        nodes = hm.build_tree()
        return len(hm.find_orphans(nodes))

    def calculate_approval_rate(self) -> float:
        approvals = self.audit.count_approvals(days=7)
        total = self.audit.count_ai_recommendations(days=7)
        return (approvals / total * 100) if total > 0 else 0.0

    # ------------------------------------------------------------------
    def generate_slack_report(self, metrics: Dict[str, Any]) -> str:
        """Format metrics into a Slack-friendly message."""
        return (
            f"📊 **Daily Team Metrics** - {metrics['repository']}\n\n"
            f"**🎯 Planning Efficiency**\n"
            f"• Time to task assignment: {metrics['time_to_task_avg']:.1f} hours\n"
            f"• AI approval rate: {metrics['approval_rate']:.1f}%\n"
            f"• Sprint completion: {metrics['sprint_completion_rate']:.1f}%\n\n"
            f"**👥 Team Activity**\n"
            f"• Weekly active users: {metrics['weekly_active_users']} team members\n"
            f"• Planning commands used: {metrics['planning_commands_used']} today\n"
            f"• Human overrides: {metrics['human_overrides_count']} (learning opportunities)\n\n"
            f"**📈 Development Velocity**\n"
            f"• LOC per assignee: {metrics['loc_per_assignee']} avg\n"
            f"• Open issues: {metrics['open_issues_count']}\n"
            f"• Orphan issues: {metrics['orphan_issues_count']}\n\n"
            "💡 Use `/autonomy status` for detailed metrics"
        )
