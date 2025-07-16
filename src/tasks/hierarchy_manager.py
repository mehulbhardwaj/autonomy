from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..github.issue_manager import Issue, IssueManager


@dataclass
class IssueNode:
    """Represents an issue in the hierarchy tree."""

    number: int
    title: str
    labels: List[str]
    body: str = ""
    parent: Optional[int] = None
    children: List[int] = field(default_factory=list)


class HierarchyManager:
    """Manage Epic → Feature → Task → Sub-task relationships."""

    def __init__(self, issue_manager: IssueManager, orphan_threshold: int = 3) -> None:
        self.issue_manager = issue_manager
        self.orphan_threshold = orphan_threshold

    # ------------------------------------------------------------------
    def _parse_parent(self, body: str) -> Optional[int]:
        """Extract parent issue number from body text.

        Looks for lines like ``Parent: #12``.
        """
        for line in body.splitlines():
            line = line.strip()
            if line.lower().startswith("parent:"):
                try:
                    return int(line.split("#", 1)[1])
                except (IndexError, ValueError):
                    return None
        return None

    def build_tree(self) -> Dict[int, IssueNode]:
        """Build hierarchy tree for open issues."""
        issues = self.issue_manager.list_issues(state="open")
        nodes: Dict[int, IssueNode] = {}
        for issue in issues:
            labels = [
                lbl["name"] if isinstance(lbl, dict) and "name" in lbl else lbl
                for lbl in issue.get("labels", [])
            ]
            node = IssueNode(
                number=issue["number"],
                title=issue.get("title", ""),
                labels=labels,
                body=issue.get("body", ""),
            )
            node.parent = self._parse_parent(node.body)
            nodes[node.number] = node

        # populate children
        for node in nodes.values():
            if node.parent and node.parent in nodes:
                nodes[node.parent].children.append(node.number)
        return nodes

    # ------------------------------------------------------------------
    def find_orphans(self, nodes: Dict[int, IssueNode]) -> List[IssueNode]:
        """Return tasks or subtasks without parents."""
        orphans = []
        for node in nodes.values():
            if any(
                lbl in node.labels for lbl in ("feature", "task", "sub-task", "subtask")
            ):
                if not node.parent:
                    orphans.append(node)
        return orphans

    def ensure_parents(self, nodes: Dict[int, IssueNode]) -> List[int]:
        """Auto-create missing parents for orphaned nodes.

        Returns a list of newly created issue numbers.
        """
        created: List[int] = []
        for node in list(nodes.values()):
            if not node.parent:
                if "feature" in node.labels:
                    title = f"Auto-created Epic for {node.title}"
                    issue = Issue(
                        title=title, body="", labels=["epic"], epic_parent=None
                    )
                    new_num = self.issue_manager.create_issue(issue)
                    if new_num:
                        node.parent = new_num
                        created.append(new_num)
                        nodes[new_num] = IssueNode(
                            number=new_num, title=title, labels=["epic"]
                        )
                elif (
                    "task" in node.labels
                    and "sub-task" not in node.labels
                    and "subtask" not in node.labels
                ):
                    title = f"Auto-created Feature for {node.title}"
                    issue = Issue(
                        title=title,
                        body=f"Parent: #{node.number}",
                        labels=["feature"],
                        epic_parent=None,
                    )
                    new_num = self.issue_manager.create_issue(issue)
                    if new_num:
                        node.parent = new_num
                        created.append(new_num)
                        nodes[new_num] = IssueNode(
                            number=new_num, title=title, labels=["feature"]
                        )
                elif "sub-task" in node.labels or "subtask" in node.labels:
                    title = f"Auto-created Task for {node.title}"
                    issue = Issue(
                        title=title,
                        body=f"Parent: #{node.number}",
                        labels=["task"],
                        epic_parent=None,
                    )
                    new_num = self.issue_manager.create_issue(issue)
                    if new_num:
                        node.parent = new_num
                        created.append(new_num)
                        nodes[new_num] = IssueNode(
                            number=new_num, title=title, labels=["task"]
                        )
        return created

    # ------------------------------------------------------------------
    def warn_on_orphans(self, nodes: Dict[int, IssueNode]) -> List[IssueNode]:
        """Return list of orphans if count exceeds threshold."""
        orphans = self.find_orphans(nodes)
        if len(orphans) >= self.orphan_threshold:
            return orphans
        return []

    def visualize(self, nodes: Dict[int, IssueNode]) -> str:
        """Return a simple text tree representation."""
        lines: List[str] = []

        def _walk(num: int, depth: int = 0) -> None:
            node = nodes[num]
            indent = "  " * depth
            lines.append(f"{indent}- {node.title} (# {node.number})")
            for child in node.children:
                _walk(child, depth + 1)

        roots = [n.number for n in nodes.values() if not n.parent]
        for r in sorted(roots):
            _walk(r, 0)
        return "\n".join(lines)
