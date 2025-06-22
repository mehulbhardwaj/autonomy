"""
Core GitHub Workflow Manager

Orchestrates the Generate-Verify loop with AI agents and human oversight.
Integrates with GitHub MCP for seamless repository management.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from ..github.issue_manager import IssueManager
from .config import WorkflowConfig
from .agents import PMAgent, SDEAgent, QAAgent


@dataclass
class TaskContext:
    """Context for a task execution"""
    issue_number: int
    title: str
    description: str
    agent_role: str
    current_phase: str
    repo_path: Path
    requirements_doc: Optional[str] = None
    design_doc: Optional[str] = None
    test_plan: Optional[str] = None


class WorkflowManager:
    """
    Main orchestrator for the Generate-Verify loop workflow.
    
    Implements the process:
    PM-agent → SDE-agent → QA-agent → Human → Merge
    """
    
    def __init__(self, 
                 github_token: str,
                 owner: str, 
                 repo: str,
                 workspace_path: str = ".",
                 config: Optional[WorkflowConfig] = None):
        """
        Initialize the workflow manager.
        
        Args:
            github_token: GitHub personal access token
            owner: Repository owner
            repo: Repository name  
            workspace_path: Local workspace path
            config: Optional workflow configuration
        """
        self.github_token = github_token
        self.owner = owner
        self.repo = repo
        self.workspace_path = Path(workspace_path)
        self.config = config or WorkflowConfig()
        
        # Initialize components
        self.issue_manager = IssueManager(github_token, owner, repo)
        self.pm_agent = PMAgent(self.config)
        self.sde_agent = SDEAgent(self.config)
        self.qa_agent = QAAgent(self.config)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Ensure docs directory exists
        self.docs_path = self.workspace_path / "docs"
        self.docs_path.mkdir(exist_ok=True)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the workflow manager"""
        logger = logging.getLogger("github_workflow_manager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def setup_repository(self) -> None:
        """
        Setup repository with labels, milestones, and documentation structure.
        Creates the foundation for the Generate-Verify loop workflow.
        """
        self.logger.info(f"Setting up repository {self.owner}/{self.repo}")
        
        # Create labels and basic milestones
        self.issue_manager.setup_repository()
        
        # Create documentation structure
        self._create_docs_structure()
        
        # Create workflow configuration file
        self._create_workflow_config()
        
        self.logger.info("Repository setup complete")
    
    def _create_docs_structure(self) -> None:
        """Create the living memory documentation structure"""
        docs_files = {
            "PRD.md": self._get_prd_template(),
            "TECH.md": self._get_tech_template(), 
            "TEST.md": self._get_test_template(),
            "WORKFLOW.md": self._get_workflow_template()
        }
        
        for filename, content in docs_files.items():
            file_path = self.docs_path / filename
            if not file_path.exists():
                file_path.write_text(content)
                self.logger.info(f"Created {filename}")
    
    def _create_workflow_config(self) -> None:
        """Create workflow configuration file"""
        config_path = self.workspace_path / ".github-workflow.json"
        if not config_path.exists():
            config_data = {
                "max_file_lines": self.config.max_file_lines,
                "max_function_lines": self.config.max_function_lines,
                "max_pr_lines": self.config.max_pr_lines,
                "test_coverage_target": self.config.test_coverage_target,
                "autonomy_level": self.config.autonomy_level,
                "agents": {
                    "pm_agent": {"model": self.config.pm_agent_model},
                    "sde_agent": {"model": self.config.sde_agent_model},
                    "qa_agent": {"model": self.config.qa_agent_model}
                }
            }
            config_path.write_text(json.dumps(config_data, indent=2))
            self.logger.info("Created workflow configuration")
    
    def process_issue(self, issue_number: int) -> Dict[str, Any]:
        """
        Process an issue through the complete Generate-Verify loop.
        
        Args:
            issue_number: GitHub issue number to process
            
        Returns:
            Dict with processing results and status
        """
        self.logger.info(f"Processing issue #{issue_number}")
        
        # Get issue details
        issue = self.issue_manager.get_issue(issue_number)
        if not issue:
            return {"error": f"Issue #{issue_number} not found"}
        
        # Create task context
        context = TaskContext(
            issue_number=issue_number,
            title=issue["title"],
            description=issue["body"],
            agent_role=self._extract_agent_role(issue["labels"]),
            current_phase=self._extract_current_phase(issue["labels"]),
            repo_path=self.workspace_path
        )
        
        # Execute the Generate-Verify loop
        result = self._execute_generate_verify_loop(context)
        
        self.logger.info(f"Completed processing issue #{issue_number}")
        return result
    
    def _execute_generate_verify_loop(self, context: TaskContext) -> Dict[str, Any]:
        """Execute the complete Generate-Verify loop for a task"""
        results = {
            "issue_number": context.issue_number,
            "phases_completed": [],
            "artifacts_created": [],
            "status": "in_progress"
        }
        
        try:
            # Phase 1: PM-agent (Requirements & Design)
            if context.current_phase in ["new", "needs-requirements"]:
                pm_result = self._execute_pm_phase(context)
                results["phases_completed"].append("pm_agent")
                results["artifacts_created"].extend(pm_result.get("artifacts", []))
                
                # Update issue labels
                self.issue_manager.update_issue_labels(
                    context.issue_number, 
                    add_labels=["needs-development"],
                    remove_labels=["needs-requirements"]
                )
            
            # Phase 2: SDE-agent (Implementation)
            if context.current_phase in ["needs-development", "in-development"]:
                sde_result = self._execute_sde_phase(context)
                results["phases_completed"].append("sde_agent")
                results["artifacts_created"].extend(sde_result.get("artifacts", []))
                
                # Update issue labels
                self.issue_manager.update_issue_labels(
                    context.issue_number,
                    add_labels=["needs-testing"],
                    remove_labels=["in-development"]
                )
            
            # Phase 3: QA-agent (Testing & Hardening)
            if context.current_phase in ["needs-testing"]:
                qa_result = self._execute_qa_phase(context)
                results["phases_completed"].append("qa_agent")
                results["artifacts_created"].extend(qa_result.get("artifacts", []))
                
                # Update issue labels
                self.issue_manager.update_issue_labels(
                    context.issue_number,
                    add_labels=["needs-review"],
                    remove_labels=["needs-testing"]
                )
            
            # Phase 4: Human Review (Manual step)
            if context.current_phase in ["needs-review"]:
                results["next_action"] = "human_review_required"
                results["status"] = "awaiting_human_review"
            
            results["status"] = "completed" if results["status"] != "awaiting_human_review" else results["status"]
            
        except Exception as e:
            self.logger.error(f"Error in Generate-Verify loop: {e}")
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    def _execute_pm_phase(self, context: TaskContext) -> Dict[str, Any]:
        """Execute PM-agent phase: requirements, design, test planning"""
        self.logger.info(f"Executing PM-agent phase for issue #{context.issue_number}")
        
        # Load existing documentation for context
        existing_docs = self._load_existing_docs()
        
        # Generate requirements document
        requirements = self.pm_agent.generate_requirements(
            context.title,
            context.description,
            existing_docs
        )
        
        # Generate system design
        design = self.pm_agent.generate_design(
            requirements,
            existing_docs
        )
        
        # Generate test plan
        test_plan = self.pm_agent.generate_test_plan(
            requirements,
            design
        )
        
        # Save artifacts
        artifacts = []
        if requirements:
            req_path = self.docs_path / f"requirements_issue_{context.issue_number}.md"
            req_path.write_text(requirements)
            artifacts.append(str(req_path))
        
        if design:
            design_path = self.docs_path / f"design_issue_{context.issue_number}.md"
            design_path.write_text(design)
            artifacts.append(str(design_path))
        
        if test_plan:
            test_path = self.docs_path / f"test_plan_issue_{context.issue_number}.md"
            test_path.write_text(test_plan)
            artifacts.append(str(test_path))
        
        return {
            "phase": "pm_agent",
            "artifacts": artifacts,
            "requirements": requirements,
            "design": design,
            "test_plan": test_plan
        }
    
    def _execute_sde_phase(self, context: TaskContext) -> Dict[str, Any]:
        """Execute SDE-agent phase: implementation"""
        self.logger.info(f"Executing SDE-agent phase for issue #{context.issue_number}")
        
        # Load requirements and design docs
        requirements = self._load_artifact(f"requirements_issue_{context.issue_number}.md")
        design = self._load_artifact(f"design_issue_{context.issue_number}.md")
        
        # Generate implementation
        implementation = self.sde_agent.implement_feature(
            requirements,
            design,
            str(context.repo_path)
        )
        
        # Run tests to ensure implementation works
        test_results = self.sde_agent.run_tests(str(context.repo_path))
        
        return {
            "phase": "sde_agent",
            "artifacts": implementation.get("files_created", []),
            "implementation": implementation,
            "test_results": test_results
        }
    
    def _execute_qa_phase(self, context: TaskContext) -> Dict[str, Any]:
        """Execute QA-agent phase: testing and hardening"""
        self.logger.info(f"Executing QA-agent phase for issue #{context.issue_number}")
        
        # Load test plan
        test_plan = self._load_artifact(f"test_plan_issue_{context.issue_number}.md")
        
        # Generate comprehensive tests
        test_suite = self.qa_agent.generate_test_suite(
            test_plan,
            str(context.repo_path)
        )
        
        # Run tests and analyze coverage
        coverage_report = self.qa_agent.analyze_test_coverage(str(context.repo_path))
        
        # Generate feedback for improvements
        feedback = self.qa_agent.generate_feedback(
            test_suite,
            coverage_report
        )
        
        return {
            "phase": "qa_agent",
            "artifacts": test_suite.get("files_created", []),
            "test_suite": test_suite,
            "coverage_report": coverage_report,
            "feedback": feedback
        }
    
    def _load_existing_docs(self) -> Dict[str, str]:
        """Load existing documentation for context"""
        docs = {}
        doc_files = ["PRD.md", "TECH.md", "TEST.md"]
        
        for doc_file in doc_files:
            doc_path = self.docs_path / doc_file
            if doc_path.exists():
                docs[doc_file] = doc_path.read_text()
        
        return docs
    
    def _load_artifact(self, filename: str) -> Optional[str]:
        """Load a specific artifact file"""
        artifact_path = self.docs_path / filename
        if artifact_path.exists():
            return artifact_path.read_text()
        return None
    
    def _extract_agent_role(self, labels: List[str]) -> str:
        """Extract agent role from issue labels"""
        for label in labels:
            if label in ["pm-agent", "sde-agent", "qa-agent"]:
                return label
        return "unknown"
    
    def _extract_current_phase(self, labels: List[str]) -> str:
        """Extract current workflow phase from issue labels"""
        phase_labels = [
            "needs-requirements", "needs-design", "needs-tests",
            "in-development", "needs-testing", "needs-review", "approved"
        ]
        
        for label in labels:
            if label in phase_labels:
                return label
        return "new"
    
    def _get_prd_template(self) -> str:
        """Get PRD template"""
        return """# Product Requirements Document (PRD)

## Problem Statement
[Describe the customer problem this feature solves]

## Success Metrics
[Define how success will be measured]

## Key Features
[List the main features and capabilities]

## User Stories
[Describe user interactions and workflows]

## Non-Functional Requirements
[Performance, security, scalability requirements]

## Dependencies
[External dependencies and integrations]

## Timeline
[Key milestones and deadlines]
"""
    
    def _get_tech_template(self) -> str:
        """Get TECH template"""
        return """# Technical Design Document

## Architecture Overview
[High-level system architecture]

## Technology Stack
[Languages, frameworks, libraries, tools]

## Design Decisions
[Key technical decisions and rationale]

## Data Models
[Database schema and data structures]

## API Design
[Endpoint specifications and contracts]

## Security Considerations
[Authentication, authorization, data protection]

## Performance Requirements
[Latency, throughput, resource usage]

## Deployment Strategy
[Infrastructure and deployment approach]
"""
    
    def _get_test_template(self) -> str:
        """Get TEST template"""
        return """# Test Strategy Document

## Testing Approach
[Overall testing philosophy and strategy]

## Coverage Targets
[Code coverage and feature coverage goals]

## Test Types
[Unit, integration, e2e, performance tests]

## Edge Cases
[Known edge cases and error conditions]

## Test Data
[Test data requirements and management]

## Automation Strategy
[CI/CD integration and automation approach]

## Quality Gates
[Criteria for release readiness]

## Risk Areas
[High-risk areas requiring extra attention]
"""
    
    def _get_workflow_template(self) -> str:
        """Get workflow documentation template"""
        return """# Workflow Documentation

## Generate-Verify Loop Process

This repository follows the Generate-Verify loop workflow:

1. **PM-agent**: Requirements → Design → Test Plan
2. **SDE-agent**: Implementation → Initial Testing
3. **QA-agent**: Comprehensive Testing → Hardening
4. **Human**: Code Review → Approval

## Agent Responsibilities

### PM-agent
- Convert issues into detailed requirements
- Create system design documents
- Generate comprehensive test plans
- Update technical documentation

### SDE-agent
- Implement features according to requirements
- Write initial unit tests
- Ensure code quality and standards
- Create pull requests

### QA-agent
- Design comprehensive test suites
- Achieve target test coverage
- Identify edge cases and risks
- Provide implementation feedback

### Human
- Review code quality and design
- Validate requirements fulfillment
- Add approval flag for merge
- Make final architectural decisions

## Quality Standards

- **Max file size**: 300 lines
- **Max function size**: 40 lines
- **Max PR size**: 500 lines
- **Test coverage**: 60-80%
- **Documentation**: Required for all features

## Workflow States

Issues progress through these states:
- `needs-requirements` → `needs-development` → `needs-testing` → `needs-review` → `approved`

## Branch Protection

- Main branch requires approved flag
- All tests must pass
- No direct pushes allowed
- Human approval required for merge
""" 