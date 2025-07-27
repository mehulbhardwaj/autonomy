from src.github.issue_manager import Issue
from src.tools.github import GitHubTools


class DummyIM:
    def __init__(self):
        self.created = None
        self.labeled = None
        self.updated = None

    def create_issue(self, issue: Issue, milestone=None):
        self.created = issue
        return 5

    def list_issues(self, state="open"):
        return [{"number": 1}]

    def get_issue(self, issue_number: int):
        return {"number": issue_number} if issue_number == 1 else None

    def update_issue_labels(self, issue_number, add_labels=None, remove_labels=None):
        self.labeled = (issue_number, add_labels, remove_labels)
        return True

    def update_issue(self, issue_number, title=None, body=None, labels=None):
        self.updated = (issue_number, title, body, labels)
        return True


def test_github_tools_basic():
    im = DummyIM()
    tools = GitHubTools(im)

    issue_id = tools.create_issue({"title": "T", "body": "B", "labels": ["bug"]})
    assert issue_id == 5
    assert isinstance(im.created, Issue)

    assert tools.list_issues() == [{"number": 1}]
    assert tools.get_issue(1) == {"number": 1}

    assert tools.update_issue_labels(1, ["bug"], ["old"])
    assert im.labeled == (1, ["bug"], ["old"])

    assert tools.update_issue(1, title="N")
    assert im.updated == (1, "N", None, None)
