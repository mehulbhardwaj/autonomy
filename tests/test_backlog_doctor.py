from datetime import datetime, timedelta, timezone

from src.tasks.backlog_doctor import BacklogDoctor


class DummyIssueManager:
    def __init__(self, issues):
        self._issues = issues
        self.labeled = []

    def list_issues(self, state="open"):
        return self._issues

    def update_issue_labels(self, issue_number, add_labels=None, remove_labels=None):
        self.labeled.append((issue_number, add_labels, remove_labels))
        return True


def _make_issue(num, title="Issue", days=0, body=""):
    ts = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    return {"number": num, "title": title, "updated_at": ts, "body": body}


def test_find_stale_issues():
    issues = [_make_issue(1, days=15), _make_issue(2, days=5)]
    doctor = BacklogDoctor(DummyIssueManager(issues))
    stale = doctor.find_stale_issues(days=14)
    assert [i["number"] for i in stale] == [1]


def test_find_oversized_issues():
    body = "\n".join(["- [ ] item" for _ in range(11)])
    issues = [_make_issue(1, body=body), _make_issue(2, body="- [ ] one")]
    doctor = BacklogDoctor(DummyIssueManager(issues))
    over = doctor.find_oversized_issues(limit=10)
    assert [i["number"] for i in over] == [1]


def test_find_duplicate_candidates():
    issues = [
        _make_issue(1, title="Add login"),
        _make_issue(2, title="Add login page"),
        _make_issue(3, title="Different"),
    ]
    doctor = BacklogDoctor(DummyIssueManager(issues))
    dupes = doctor.find_duplicate_candidates(threshold=0.8)
    pairs = {(a["number"], b["number"]) for a, b, _ in dupes}
    assert (1, 2) in pairs


def test_run_applies_labels():
    body = "\n".join(["- [ ] item" for _ in range(12)])
    issues = [_make_issue(1, days=20, body=body)]
    mgr = DummyIssueManager(issues)
    doctor = BacklogDoctor(mgr)
    result = doctor.run()
    assert result["stale"] == [1]
    assert result["oversized"] == [1]
    assert mgr.labeled  # labels applied
