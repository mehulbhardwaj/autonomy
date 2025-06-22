"""
Plan Manager for Autonomy MCP

Handles task planning, milestone management, and issue creation from plans.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class TaskPlan:
    """Represents a task plan with milestones and issues."""
    name: str
    description: str
    milestones: List[Dict[str, Any]]
    issues: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

class PlanManager:
    """Manages task plans and their conversion to GitHub issues."""
    
    def __init__(self, workspace_path: str = "."):
        """
        Initialize PlanManager.
        
        Args:
            workspace_path: Path to the workspace directory
        """
        self.workspace_path = workspace_path
    
    def load_plan(self, plan_file: str) -> TaskPlan:
        """
        Load a task plan from JSON file.
        
        Args:
            plan_file: Path to the plan JSON file
            
        Returns:
            TaskPlan object
            
        Raises:
            FileNotFoundError: If plan file doesn't exist
            ValueError: If plan format is invalid
        """
        plan_path = os.path.join(self.workspace_path, plan_file)
        
        if not os.path.exists(plan_path):
            raise FileNotFoundError(f"Plan file not found: {plan_path}")
        
        try:
            with open(plan_path, 'r') as f:
                plan_data = json.load(f)
            
            return TaskPlan(
                name=plan_data.get('name', 'Unnamed Plan'),
                description=plan_data.get('description', ''),
                milestones=plan_data.get('milestones', []),
                issues=plan_data.get('issues', []),
                metadata=plan_data.get('metadata', {})
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in plan file: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required field in plan: {e}")
    
    def save_plan(self, plan: TaskPlan, plan_file: str) -> None:
        """
        Save a task plan to JSON file.
        
        Args:
            plan: TaskPlan to save
            plan_file: Path to save the plan
        """
        plan_path = os.path.join(self.workspace_path, plan_file)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(plan_path), exist_ok=True)
        
        with open(plan_path, 'w') as f:
            json.dump(asdict(plan), f, indent=2)
    
    def create_plan_template(self, template_type: str = "basic") -> TaskPlan:
        """
        Create a plan template.
        
        Args:
            template_type: Type of template (basic, api, web, cli)
            
        Returns:
            TaskPlan template
        """
        templates = {
            "basic": self._create_basic_template(),
            "api": self._create_api_template(),
            "web": self._create_web_template(),
            "cli": self._create_cli_template(),
        }
        
        return templates.get(template_type, templates["basic"])
    
    def _create_basic_template(self) -> TaskPlan:
        """Create basic project template."""
        return TaskPlan(
            name="Basic Project Plan",
            description="A basic project setup with core features",
            milestones=[
                {
                    "title": "Setup & Foundation",
                    "description": "Initial project setup and core architecture",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Core Features",
                    "description": "Implementation of main functionality",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Testing & Documentation",
                    "description": "Comprehensive testing and documentation",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Release",
                    "description": "Final release preparation",
                    "due_date": None,
                    "state": "open"
                }
            ],
            issues=[
                {
                    "title": "Project Setup",
                    "body": "Set up basic project structure and dependencies",
                    "labels": ["epic", "pm-agent"],
                    "milestone": "Setup & Foundation",
                    "assignee": None,
                    "story_points": 3
                },
                {
                    "title": "Core Implementation",
                    "body": "Implement main functionality",
                    "labels": ["feature", "sde-agent"],
                    "milestone": "Core Features",
                    "assignee": None,
                    "story_points": 8
                },
                {
                    "title": "Test Suite",
                    "body": "Create comprehensive test coverage",
                    "labels": ["task", "qa-agent"],
                    "milestone": "Testing & Documentation",
                    "assignee": None,
                    "story_points": 5
                }
            ]
        )
    
    def _create_api_template(self) -> TaskPlan:
        """Create API project template."""
        return TaskPlan(
            name="API Project Plan",
            description="RESTful API development with authentication and testing",
            milestones=[
                {
                    "title": "API Foundation",
                    "description": "Basic API setup with routing and middleware",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Authentication",
                    "description": "User authentication and authorization",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Core Endpoints",
                    "description": "Main API endpoints and business logic",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Testing & Docs",
                    "description": "API testing and documentation",
                    "due_date": None,
                    "state": "open"
                }
            ],
            issues=[
                {
                    "title": "API Framework Setup",
                    "body": "Set up API framework with basic routing",
                    "labels": ["epic", "pm-agent"],
                    "milestone": "API Foundation",
                    "assignee": None,
                    "story_points": 5
                },
                {
                    "title": "Authentication System",
                    "body": "Implement JWT-based authentication",
                    "labels": ["feature", "sde-agent"],
                    "milestone": "Authentication",
                    "assignee": None,
                    "story_points": 8
                },
                {
                    "title": "API Testing Suite",
                    "body": "Create integration tests for all endpoints",
                    "labels": ["task", "qa-agent"],
                    "milestone": "Testing & Docs",
                    "assignee": None,
                    "story_points": 5
                }
            ]
        )
    
    def _create_web_template(self) -> TaskPlan:
        """Create web application template."""
        return TaskPlan(
            name="Web Application Plan",
            description="Full-stack web application with modern UI/UX",
            milestones=[
                {
                    "title": "Frontend Setup",
                    "description": "React/Vue setup with component library",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Backend API",
                    "description": "Backend API and database integration",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Integration",
                    "description": "Frontend-backend integration",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Deployment",
                    "description": "Production deployment and monitoring",
                    "due_date": None,
                    "state": "open"
                }
            ],
            issues=[
                {
                    "title": "Frontend Framework Setup",
                    "body": "Set up React/Vue with routing and state management",
                    "labels": ["epic", "pm-agent"],
                    "milestone": "Frontend Setup",
                    "assignee": None,
                    "story_points": 5
                },
                {
                    "title": "UI Component Library",
                    "body": "Create reusable UI components",
                    "labels": ["feature", "sde-agent"],
                    "milestone": "Frontend Setup",
                    "assignee": None,
                    "story_points": 8
                },
                {
                    "title": "E2E Testing",
                    "body": "Set up end-to-end testing with Playwright",
                    "labels": ["task", "qa-agent"],
                    "milestone": "Integration",
                    "assignee": None,
                    "story_points": 6
                }
            ]
        )
    
    def _create_cli_template(self) -> TaskPlan:
        """Create CLI application template."""
        return TaskPlan(
            name="CLI Application Plan",
            description="Command-line interface with subcommands and configuration",
            milestones=[
                {
                    "title": "CLI Framework",
                    "description": "Basic CLI setup with argument parsing",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Core Commands",
                    "description": "Implementation of main commands",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Configuration",
                    "description": "Configuration management and plugins",
                    "due_date": None,
                    "state": "open"
                },
                {
                    "title": "Distribution",
                    "description": "Packaging and distribution setup",
                    "due_date": None,
                    "state": "open"
                }
            ],
            issues=[
                {
                    "title": "CLI Framework Setup",
                    "body": "Set up Click/Typer with basic command structure",
                    "labels": ["epic", "pm-agent"],
                    "milestone": "CLI Framework",
                    "assignee": None,
                    "story_points": 3
                },
                {
                    "title": "Core Command Implementation",
                    "body": "Implement main CLI commands and functionality",
                    "labels": ["feature", "sde-agent"],
                    "milestone": "Core Commands",
                    "assignee": None,
                    "story_points": 8
                },
                {
                    "title": "CLI Testing",
                    "body": "Create tests for CLI commands and edge cases",
                    "labels": ["task", "qa-agent"],
                    "milestone": "Core Commands",
                    "assignee": None,
                    "story_points": 4
                }
            ]
        )
    
    def validate_plan(self, plan: TaskPlan) -> List[str]:
        """
        Validate a task plan for common issues.
        
        Args:
            plan: TaskPlan to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for required fields
        if not plan.name:
            errors.append("Plan name is required")
        
        if not plan.milestones:
            errors.append("At least one milestone is required")
        
        if not plan.issues:
            errors.append("At least one issue is required")
        
        # Validate milestones
        milestone_titles = set()
        for i, milestone in enumerate(plan.milestones):
            if not milestone.get('title'):
                errors.append(f"Milestone {i} missing title")
            elif milestone['title'] in milestone_titles:
                errors.append(f"Duplicate milestone title: {milestone['title']}")
            else:
                milestone_titles.add(milestone['title'])
        
        # Validate issues
        for i, issue in enumerate(plan.issues):
            if not issue.get('title'):
                errors.append(f"Issue {i} missing title")
            
            if not issue.get('body'):
                errors.append(f"Issue {i} missing body")
            
            # Check milestone reference
            milestone_ref = issue.get('milestone')
            if milestone_ref and milestone_ref not in milestone_titles:
                errors.append(f"Issue {i} references unknown milestone: {milestone_ref}")
        
        return errors
