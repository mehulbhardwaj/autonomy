#!/usr/bin/env python3
"""
Create GitHub Issues from Task Plan
Uses the GitHub Issue Management System to create issues from a task plan document.
"""

import argparse
import json
from dataclasses import dataclass
from typing import List, Optional

import requests


@dataclass
class Issue:
    """GitHub issue definition"""

    title: str
    body: str
    labels: List[str]
    milestone: Optional[str] = None
    assignees: Optional[List[str]] = None
    epic_parent: Optional[str] = None
    story_points: Optional[int] = None
    acceptance_criteria: Optional[List[str]] = None
    agent_role: Optional[str] = None
    verification_required: bool = True


class GitHubIssueCreator:
    """Create GitHub issues from task plan"""

    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

    def get_milestone_number(self, title: str) -> Optional[int]:
        """Get milestone number by title"""
        try:
            response = requests.get(f"{self.base_url}/milestones", headers=self.headers)
            if response.status_code == 200:
                milestones = response.json()
                for milestone in milestones:
                    if milestone["title"] == title:
                        return milestone["number"]
            return None
        except Exception as e:
            print(f"✗ Error getting milestone {title}: {e}")
            return None

    def create_milestone(
        self, title: str, description: str, due_on: Optional[str] = None
    ) -> Optional[int]:
        """Create a milestone and return its number"""
        try:
            milestone_data = {
                "title": title,
                "description": description,
                "state": "open",
            }
            if due_on:
                milestone_data["due_on"] = due_on

            response = requests.post(
                f"{self.base_url}/milestones", headers=self.headers, json=milestone_data
            )

            if response.status_code == 201:
                milestone_response = response.json()
                print(f"✓ Created milestone: {title} (#{milestone_response['number']})")
                return milestone_response["number"]
            elif response.status_code == 422:
                # Milestone might already exist, try to get it
                existing_number = self.get_milestone_number(title)
                if existing_number:
                    print(f"✓ Using existing milestone: {title} (#{existing_number})")
                    return existing_number
                else:
                    print(f"✗ Failed to create milestone {title}: {response.text}")
                    return None
            else:
                print(f"✗ Failed to create milestone {title}: {response.text}")
                return None

        except Exception as e:
            print(f"✗ Error creating milestone {title}: {e}")
            return None

    def create_issue(
        self, issue: Issue, milestone_number: Optional[int] = None
    ) -> Optional[int]:
        """Create a GitHub issue and return its number"""

        # Build issue body with structured information
        body_parts = [issue.body]

        if issue.acceptance_criteria:
            body_parts.append("\n## Acceptance Criteria")
            for criteria in issue.acceptance_criteria:
                body_parts.append(f"- {criteria}")

        if issue.story_points:
            body_parts.append(f"\n**Story Points:** {issue.story_points}")

        if issue.agent_role:
            body_parts.append(f"\n**Agent Role:** {issue.agent_role}")

        if issue.epic_parent:
            body_parts.append(f"\n**Epic:** {issue.epic_parent}")

        # Add Generate-Verify loop information
        if issue.verification_required:
            body_parts.append("\n## Generate-Verify Loop")
            body_parts.append("- [ ] Requirements document created (PM-agent)")
            body_parts.append("- [ ] System design document created (PM-agent)")
            body_parts.append("- [ ] Test plan created (PM-agent)")
            body_parts.append("- [ ] Feature implemented (SDE-agent)")
            body_parts.append("- [ ] Tests pass (SDE-agent)")
            body_parts.append("- [ ] Additional test cases written (QA-agent)")
            body_parts.append("- [ ] Code review completed (Human)")
            body_parts.append("- [ ] Approved flag added")

        issue_data = {
            "title": issue.title,
            "body": "\n".join(body_parts),
            "labels": issue.labels or [],
        }

        if milestone_number:
            issue_data["milestone"] = milestone_number

        if issue.assignees:
            issue_data["assignees"] = issue.assignees

        try:
            response = requests.post(
                f"{self.base_url}/issues", headers=self.headers, json=issue_data
            )

            if response.status_code == 201:
                issue_response = response.json()
                print(f"✓ Created issue: {issue.title} (#{issue_response['number']})")
                return issue_response["number"]
            else:
                print(f"✗ Failed to create issue {issue.title}: {response.text}")
                return None

        except Exception as e:
            print(f"✗ Error creating issue {issue.title}: {e}")
            return None

    def create_issues_from_plan(self, plan_file: str) -> None:
        """Create issues from a task plan document"""
        try:
            with open(plan_file, "r") as f:
                plan = json.load(f)
        except Exception as e:
            print(f"✗ Error loading task plan from {plan_file}: {e}")
            return

        if not plan:
            print("✗ No valid task plan found")
            return

        print(f"Creating issues from task plan: {plan_file}")

        # Create milestones first
        milestone_map = {}
        if "milestones" in plan:
            print("\nCreating milestones...")
            for milestone_data in plan["milestones"]:
                milestone_number = self.create_milestone(
                    milestone_data["title"],
                    milestone_data["description"],
                    milestone_data.get("due_on"),
                )
                if milestone_number:
                    milestone_map[milestone_data["title"]] = milestone_number

        # Create issues
        if "issues" in plan:
            print(f"\nCreating {len(plan['issues'])} issues...")
            for issue_data in plan["issues"]:
                # Convert dict to Issue object
                issue = Issue(
                    title=issue_data["title"],
                    body=issue_data["body"],
                    labels=issue_data.get("labels", []),
                    milestone=issue_data.get("milestone"),
                    assignees=issue_data.get("assignees"),
                    epic_parent=issue_data.get("epic_parent"),
                    story_points=issue_data.get("story_points"),
                    acceptance_criteria=issue_data.get("acceptance_criteria"),
                    agent_role=issue_data.get("agent_role"),
                    verification_required=issue_data.get("verification_required", True),
                )

                milestone_number = None
                if issue.milestone and issue.milestone in milestone_map:
                    milestone_number = milestone_map[issue.milestone]

                self.create_issue(issue, milestone_number)

        print("\n✓ Task plan processing complete!")
        print(
            f"Visit https://github.com/{self.owner}/{self.repo}/issues to view created issues"
        )
        print(
            f"Visit https://github.com/{self.owner}/{self.repo}/milestones to view milestones"
        )


def main():
    parser = argparse.ArgumentParser(description="Create GitHub Issues from Task Plan")
    parser.add_argument("--token", required=True, help="GitHub personal access token")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--plan", required=True, help="Path to task plan JSON file")

    args = parser.parse_args()

    # Initialize the creator
    creator = GitHubIssueCreator(args.token, args.owner, args.repo)

    # Create issues from plan
    creator.create_issues_from_plan(args.plan)


if __name__ == "__main__":
    main()
