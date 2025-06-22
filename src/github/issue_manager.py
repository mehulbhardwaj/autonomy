#!/usr/bin/env python3
"""
GitHub Issue Management System
Comprehensive system for creating and managing GitHub issues from task plan documents.
Supports the Generate-Verify loop workflow with PM-agent, SDE-agent, and QA-agent roles.
"""

import json
import os
import sys
import argparse
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

try:
    import yaml
except ImportError:
    yaml = None

@dataclass
class Label:
    """GitHub label definition"""
    name: str
    color: str
    description: str

@dataclass
class Milestone:
    """GitHub milestone definition"""
    title: str
    description: str
    due_on: Optional[str] = None
    state: str = "open"

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
    agent_role: Optional[str] = None  # PM-agent, SDE-agent, QA-agent
    verification_required: bool = True

class IssueManager:
    """Main class for managing GitHub issues"""
    
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        # Standard labels for the Generate-Verify loop
        self.standard_labels = [
            Label("epic", "8B5CF6", "Large feature or initiative spanning multiple issues"),
            Label("feature", "0E8A16", "New feature or enhancement"),
            Label("task", "1D76DB", "Individual task or work item"),
            Label("bug", "D73A4A", "Something isn't working"),
            Label("documentation", "0075CA", "Improvements or additions to documentation"),
            Label("enhancement", "A2EEEF", "New feature or request"),
            Label("devops", "F9D0C4", "DevOps and infrastructure related"),
            
            # Agent roles
            Label("pm-agent", "FF6B6B", "PM-agent: Requirements and planning"),
            Label("sde-agent", "4ECDC4", "SDE-agent: Software development"),
            Label("qa-agent", "45B7D1", "QA-agent: Quality assurance and testing"),
            
            # Workflow states
            Label("needs-requirements", "FBCA04", "Needs requirements document"),
            Label("needs-design", "FEF2C0", "Needs system design document"),
            Label("needs-tests", "F1C40F", "Needs test plan"),
            Label("in-development", "0052CC", "Currently being developed"),
            Label("needs-review", "5319E7", "Needs code review"),
            Label("approved", "0E8A16", "Approved and ready to merge"),
            Label("blocked", "D73A4A", "Blocked by dependencies"),
            
            # Priority levels
            Label("priority-critical", "B60205", "Critical priority"),
            Label("priority-high", "D93F0B", "High priority"),
            Label("priority-medium", "FBCA04", "Medium priority"),
            Label("priority-low", "0E8A16", "Low priority"),
        ]
    
    def create_labels(self) -> None:
        """Create standard labels in the repository"""
        print("Creating standard labels...")
        
        for label in self.standard_labels:
            try:
                response = requests.post(
                    f"{self.base_url}/labels",
                    headers=self.headers,
                    json=asdict(label)
                )
                
                if response.status_code == 201:
                    print(f"✓ Created label: {label.name}")
                elif response.status_code == 422:
                    # Label already exists, update it
                    requests.patch(
                        f"{self.base_url}/labels/{label.name}",
                        headers=self.headers,
                        json={"color": label.color, "description": label.description}
                    )
                    print(f"✓ Updated label: {label.name}")
                else:
                    print(f"✗ Failed to create label {label.name}: {response.text}")
                    
            except Exception as e:
                print(f"✗ Error creating label {label.name}: {e}")
    
    def create_milestone(self, milestone: Milestone) -> Optional[int]:
        """Create a milestone and return its number"""
        try:
            milestone_dict = asdict(milestone)
            response = requests.post(
                f"{self.base_url}/milestones",
                headers=self.headers,
                json=milestone_dict
            )
            
            if response.status_code == 201:
                milestone_data = response.json()
                print(f"✓ Created milestone: {milestone.title} (#{milestone_data['number']})")
                return milestone_data['number']
            else:
                print(f"✗ Failed to create milestone {milestone.title}: {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error creating milestone {milestone.title}: {e}")
            return None
    
    def create_issue(self, issue: Issue, milestone_number: Optional[int] = None) -> Optional[int]:
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
            "labels": issue.labels or []
        }
        
        if milestone_number:
            issue_data["milestone"] = milestone_number
        
        if issue.assignees:
            issue_data["assignees"] = issue.assignees
        
        try:
            response = requests.post(
                f"{self.base_url}/issues",
                headers=self.headers,
                json=issue_data
            )
            
            if response.status_code == 201:
                issue_response = response.json()
                print(f"✓ Created issue: {issue.title} (#{issue_response['number']})")
                return issue_response['number']
            else:
                print(f"✗ Failed to create issue {issue.title}: {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error creating issue {issue.title}: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="GitHub Issue Management System")
    parser.add_argument("--token", required=True, help="GitHub personal access token")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--setup", action="store_true", help="Set up repository with labels")
    
    args = parser.parse_args()
    
    # Initialize the manager
    manager = IssueManager(args.token, args.owner, args.repo)
    
    if args.setup:
        manager.create_labels()

if __name__ == "__main__":
    main()
