from datetime import datetime, timedelta, timezone

from src.tasks.ranking import RankingConfig, RankingEngine


def _make_issue(num: int, prio: str, days: int = 0):
    return {
        "number": num,
        "title": f"Issue {num}",
        "labels": [{"name": prio}],
        "created_at": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),
    }


def test_score_ordering():
    eng = RankingEngine()
    high = _make_issue(1, "priority-high", 1)
    low = _make_issue(2, "priority-low", 0)
    assert eng.score_issue(high) > eng.score_issue(low)


def test_explain_score():
    eng = RankingEngine()
    issue = _make_issue(3, "priority-high", 0)
    score, breakdown = eng.score_issue(issue, explain=True)
    assert score == eng.score_issue(issue)
    assert breakdown["priority"] == 3
    assert "age_penalty" in breakdown


def test_custom_weights():
    cfg = RankingConfig(weights={"priority_field": 1, "issue_age": 10})
    eng = RankingEngine(cfg)
    newer = _make_issue(4, "priority-low", 0)
    older = _make_issue(5, "priority-low", 5)
    assert eng.score_issue(newer) > eng.score_issue(older)
