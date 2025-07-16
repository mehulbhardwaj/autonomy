from src.github.issue_manager import Issue
from src.tasks.hierarchy_manager import HierarchyManager


class DummyIssueManager:
    def __init__(self, issues):
        self._issues = issues
        self.created = []

    def list_issues(self, state="open"):
        return self._issues

    def create_issue(self, issue: Issue, milestone_number=None):
        num = 100 + len(self.created)
        self.created.append((num, issue))
        return num


def _make_issue(num, label, body=""):
    return {
        "number": num,
        "title": f"Issue {num}",
        "labels": [label],
        "body": body,
    }


def test_build_tree_and_auto_create_parents():
    issues = [_make_issue(1, "feature"), _make_issue(2, "task", "Parent: #1")]
    dummy = DummyIssueManager(issues)
    hm = HierarchyManager(dummy)
    nodes = hm.build_tree()
    created = hm.ensure_parents(nodes)
    # A new epic should be created for the feature without parent
    assert created
    assert dummy.created[0][1].labels == ["epic"]
    # After creation parent should be set
    assert nodes[1].parent == 100


def test_find_orphans():
    issues = [
        _make_issue(1, "task"),
        _make_issue(2, "task"),
        _make_issue(3, "task"),
        _make_issue(4, "task"),
    ]
    dummy = DummyIssueManager(issues)
    hm = HierarchyManager(dummy, orphan_threshold=3)
    nodes = hm.build_tree()
    orphans = hm.warn_on_orphans(nodes)
    assert len(orphans) == 4


def test_subtask_parent_creation_and_visualize():
    issues = [
        _make_issue(1, "sub-task"),
    ]
    dummy = DummyIssueManager(issues)
    hm = HierarchyManager(dummy)
    nodes = hm.build_tree()
    created = hm.ensure_parents(nodes)
    # Should create a task parent
    assert created
    assert dummy.created[0][1].labels == ["task"]
    text = hm.visualize(nodes)
    assert "Issue 1" in text


def test_build_tree_relationships_and_visualize():
    issues = [
        _make_issue(1, "epic"),
        _make_issue(2, "feature", "Parent: #1"),
        _make_issue(3, "task", "Parent: #2"),
        _make_issue(4, "sub-task", "Parent: #3"),
    ]
    hm = HierarchyManager(DummyIssueManager(issues))
    nodes = hm.build_tree()

    assert nodes[2].parent == 1
    assert nodes[3].parent == 2
    assert nodes[4].parent == 3
    assert nodes[1].children == [2]
    assert nodes[2].children == [3]
    assert nodes[3].children == [4]
    tree = hm.visualize(nodes)
    assert "Issue 4" in tree


def test_auto_create_feature_for_orphan_task():
    issues = [_make_issue(1, "task")]
    dummy = DummyIssueManager(issues)
    hm = HierarchyManager(dummy)
    nodes = hm.build_tree()
    created = hm.ensure_parents(nodes)
    assert created
    assert dummy.created[0][1].labels == ["feature"]
    assert nodes[1].parent == 100


def test_warn_on_orphans_below_threshold():
    issues = [_make_issue(1, "task"), _make_issue(2, "task")]
    hm = HierarchyManager(DummyIssueManager(issues), orphan_threshold=3)
    nodes = hm.build_tree()
    orphans = hm.warn_on_orphans(nodes)
    assert orphans == []
