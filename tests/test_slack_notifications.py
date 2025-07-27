from datetime import datetime

from src.slack.notifications import (
    BacklogDoctorNotifier,
    BacklogFindings,
    DuplicatePair,
    Issue,
    MetricsDashboard,
    NotificationScheduler,
    SystemNotifier,
    UndoOperation,
    WeeklyMetrics,
)


class DummySlackBot:
    def __init__(self) -> None:
        self.calls = []

    def post_message(self, channel: str, text: str, blocks=None):
        self.calls.append((channel, text, blocks))
        return True


def test_backlog_doctor_notifier():
    bot = DummySlackBot()
    notifier = BacklogDoctorNotifier(bot)  # type: ignore[arg-type]
    findings = BacklogFindings(
        stale_issues=[Issue(1, "Old", "http://i", 10)],
        duplicates=[
            DuplicatePair(Issue(2, "A", "http://a"), Issue(3, "B", "http://b"), 95)
        ],
        oversized=[],
        health_score=80,
    )
    assert notifier.send_nightly_report("C", findings)
    ch, text, blocks = bot.calls[0]
    assert ch == "C"
    assert "Backlog Doctor" in text
    assert blocks[0]["type"] == "header"


def test_metrics_dashboard():
    bot = DummySlackBot()
    dash = MetricsDashboard(bot)  # type: ignore[arg-type]
    metrics = WeeklyMetrics(
        week_start=datetime(2024, 1, 1),
        completed_issues=5,
        avg_time_to_task=1.2,
        approval_rate=90,
        weekly_active_users=3,
    )
    assert dash.send_weekly_metrics("C", metrics)
    assert bot.calls


def test_system_notifier():
    bot = DummySlackBot()
    sysn = SystemNotifier(bot)  # type: ignore[arg-type]
    op = UndoOperation("Did stuff", "me", "h")
    assert sysn.send_undo_confirmation("C", op)
    assert bot.calls


def test_notification_scheduler():
    bot = DummySlackBot()
    sched = NotificationScheduler(bot)  # type: ignore[arg-type]

    called = {}

    def func(channel: str):
        called[channel] = True

    sched.schedule_daily("d", "09:00", func, "C")
    sched.schedule_weekly("w", "mon", "10:00", func, "C")
    sched.run_scheduler()
    assert called["C"]


def test_orphan_notifier():
    bot = DummySlackBot()
    from src.slack.notifications import OrphanNotifier

    notifier = OrphanNotifier(bot)  # type: ignore[arg-type]
    assert notifier.send_orphan_warning("C", 2, [1, 2])
    ch, text, _ = bot.calls[-1]
    assert "Orphans detected" in text
    assert "#1" in text and "#2" in text
