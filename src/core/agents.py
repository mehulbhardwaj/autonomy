"""
AI Agents for the Generate-Verify Loop

Implements PM-agent, SDE-agent, and QA-agent with specific roles and responsibilities.
"""

import os
import json
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path

from .config import WorkflowConfig


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.name = self.__class__.__name__
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    def _call_llm(self, prompt: str, context: str = "") -> str:
        """
        Call LLM with prompt and context.
        In a real implementation, this would integrate with your preferred LLM API.
        For now, returns a placeholder.
        """
        # This is a placeholder - in real implementation you'd call:
        # - OpenAI API for GPT models
        # - Anthropic API for Claude models
        # - Local models via Ollama
        # - GitHub Copilot API
        
        return f"[LLM Response for {self.name}]\nPrompt: {prompt[:100]}...\nContext: {context[:100]}..."
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def _write_file(self, file_path: str, content: str) -> bool:
        """Write file content safely"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    def _run_command(self, command: str, cwd: str = ".") -> Dict[str, Any]:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }


class PMAgent(BaseAgent):
    """
    Product Manager Agent
    
    Responsibilities:
    - Convert issues into detailed requirements
    - Create system design documents  
    - Generate comprehensive test plans
    - Update technical documentation
    """
    
    def get_system_prompt(self) -> str:
        return f"""You are a PM-agent (Product Manager Agent) in a Generate-Verify loop workflow.

Your role is to:
1. Analyze issues and create detailed requirements documents
2. Design system architecture and technical specifications
3. Create comprehensive test plans
4. Update project documentation

Quality constraints:
- Max file size: {self.config.max_file_lines} lines
- Max function size: {self.config.max_function_lines} lines
- Test coverage target: {self.config.test_coverage_target * 100}%

You work in a team with SDE-agent (implementation) and QA-agent (testing).
Your output will be used by these agents, so be precise and comprehensive.

Always consider:
- User experience and business value
- Technical feasibility and constraints
- Testing requirements and edge cases
- Documentation and maintainability
- Security and performance implications

Format your responses as structured documents with clear sections.
"""
    
    def generate_requirements(self, title: str, description: str, existing_docs: Dict[str, str]) -> str:
        """Generate detailed requirements document"""
        context = f"""
Title: {title}
Description: {description}

Existing Documentation:
{json.dumps(existing_docs, indent=2)}
"""
        
        prompt = """
Generate a comprehensive requirements document for this issue.

Include:
1. Problem Statement - What problem does this solve?
2. Success Metrics - How will success be measured?
3. Functional Requirements - What should the system do?
4. Non-Functional Requirements - Performance, security, usability
5. User Stories - Key user interactions
6. Acceptance Criteria - Specific conditions for completion
7. Dependencies - What this depends on or affects
8. Risks and Assumptions - Potential issues and assumptions

Format as structured Markdown with clear sections.
"""
        
        return self._call_llm(prompt, context)
    
    def generate_design(self, requirements: str, existing_docs: Dict[str, str]) -> str:
        """Generate system design document"""
        context = f"""
Requirements:
{requirements}

Existing Documentation:
{json.dumps(existing_docs, indent=2)}
"""
        
        prompt = f"""
Create a technical design document based on the requirements.

Include:
1. Architecture Overview - High-level system design
2. Component Design - Key components and their responsibilities
3. Data Models - Database schema and data structures
4. API Design - Endpoints, request/response formats
5. Integration Points - External systems and dependencies
6. Security Design - Authentication, authorization, data protection
7. Performance Considerations - Scalability and optimization
8. Implementation Plan - Development phases and milestones

Constraints:
- Max file size: {self.config.max_file_lines} lines
- Max function size: {self.config.max_function_lines} lines
- Follow existing patterns in the codebase

Format as structured Markdown with diagrams where helpful.
"""
        
        return self._call_llm(prompt, context)
    
    def generate_test_plan(self, requirements: str, design: str) -> str:
        """Generate comprehensive test plan"""
        context = f"""
Requirements:
{requirements}

Design:
{design}
"""
        
        prompt = f"""
Create a comprehensive test plan covering all aspects of the feature.

Include:
1. Test Strategy - Overall approach and philosophy
2. Test Types - Unit, integration, e2e, performance tests
3. Test Scenarios - Key user flows and edge cases
4. Test Data - Required test data and setup
5. Coverage Targets - Specific coverage goals
6. Risk-Based Testing - High-risk areas requiring extra attention
7. Automation Strategy - What should be automated
8. Quality Gates - Criteria for each phase

Target Coverage: {self.config.test_coverage_target * 100}%

Format as structured Markdown with specific test cases.
"""
        
        return self._call_llm(prompt, context)


class SDEAgent(BaseAgent):
    """
    Software Development Engineer Agent
    
    Responsibilities:
    - Implement features according to requirements
    - Write initial unit tests
    - Ensure code quality and standards
    - Create pull requests
    """
    
    def get_system_prompt(self) -> str:
        return f"""You are an SDE-agent (Software Development Engineer Agent) in a Generate-Verify loop workflow.

Your role is to:
1. Implement features according to PM-agent requirements and design
2. Write clean, maintainable code following best practices
3. Create initial unit tests to verify functionality
4. Ensure code meets quality standards
5. Create well-documented pull requests

Quality constraints:
- Max file size: {self.config.max_file_lines} lines
- Max function size: {self.config.max_function_lines} lines
- Max PR size: {self.config.max_pr_lines} lines
- Test coverage target: {self.config.test_coverage_target * 100}%

You work with PM-agent (requirements) and QA-agent (comprehensive testing).
Your code will be tested and hardened by QA-agent.

Always:
- Follow DRY principles and avoid code duplication
- Write self-documenting code with clear variable names
- Add comments for complex logic
- Handle errors gracefully
- Consider security implications
- Write tests alongside implementation

Focus on:
- Correctness and reliability
- Performance and efficiency  
- Maintainability and readability
- Security and safety
"""
    
    def implement_feature(self, requirements: str, design: str, repo_path: str) -> Dict[str, Any]:
        """Implement feature based on requirements and design"""
        context = f"""
Requirements:
{requirements}

Design:
{design}

Repository Path: {repo_path}
"""
        
        prompt = f"""
Implement the feature according to the requirements and design.

Implementation guidelines:
- Max file size: {self.config.max_file_lines} lines
- Max function size: {self.config.max_function_lines} lines
- Follow existing code patterns and conventions
- Write unit tests for all new functions
- Handle edge cases and errors
- Add appropriate logging and monitoring
- Consider performance implications

Provide:
1. List of files to create/modify
2. Complete implementation for each file
3. Unit tests for new functionality
4. Documentation updates if needed

Format as structured response with file paths and content.
"""
        
        response = self._call_llm(prompt, context)
        
        # In real implementation, parse response and create files
        return {
            "implementation": response,
            "files_created": [],  # Would contain actual file paths
            "files_modified": [],
            "tests_created": []
        }
    
    def run_tests(self, repo_path: str) -> Dict[str, Any]:
        """Run existing test suite"""
        # Try common test runners
        test_commands = [
            "python -m pytest",
            "npm test",
            "cargo test",
            "go test ./...",
            "python -m unittest discover"
        ]
        
        results = {}
        for cmd in test_commands:
            result = self._run_command(cmd, repo_path)
            if result["success"] or "test" in result["stdout"].lower():
                results[cmd] = result
                break
        
        return results
    
    def check_code_quality(self, repo_path: str) -> Dict[str, Any]:
        """Run code quality checks"""
        quality_commands = [
            "flake8 .",
            "pylint .",
            "eslint .",
            "clippy",
            "golangci-lint run"
        ]
        
        results = {}
        for cmd in quality_commands:
            result = self._run_command(cmd, repo_path)
            results[cmd] = result
        
        return results


class QAAgent(BaseAgent):
    """
    Quality Assurance Agent
    
    Responsibilities:
    - Design comprehensive test suites
    - Achieve target test coverage
    - Identify edge cases and risks
    - Provide implementation feedback
    """
    
    def get_system_prompt(self) -> str:
        return f"""You are a QA-agent (Quality Assurance Agent) in a Generate-Verify loop workflow.

Your role is to:
1. Design comprehensive test suites covering all scenarios
2. Achieve target test coverage ({self.config.test_coverage_target * 100}%)
3. Identify edge cases, error conditions, and risks
4. Provide feedback to improve code quality and reliability
5. Ensure the implementation meets requirements

You work with PM-agent (requirements/test plan) and SDE-agent (implementation).
Your job is to harden the implementation before human review.

Focus on:
- Comprehensive test coverage (unit, integration, e2e)
- Edge cases and error conditions
- Performance and load testing
- Security testing
- Usability and accessibility
- Regression prevention

Test types to consider:
- Unit tests for individual functions
- Integration tests for component interactions
- End-to-end tests for user workflows
- Performance tests for scalability
- Security tests for vulnerabilities
- Error handling and recovery tests

Quality gates:
- Test coverage >= {self.config.test_coverage_target * 100}%
- All tests passing
- No critical security issues
- Performance within acceptable limits
"""
    
    def generate_test_suite(self, test_plan: str, repo_path: str) -> Dict[str, Any]:
        """Generate comprehensive test suite"""
        context = f"""
Test Plan:
{test_plan}

Repository Path: {repo_path}
Repository Structure:
{self._get_repo_structure(repo_path)}
"""
        
        prompt = f"""
Create a comprehensive test suite based on the test plan.

Generate:
1. Unit tests for all functions and methods
2. Integration tests for component interactions
3. End-to-end tests for user workflows
4. Error handling tests
5. Edge case tests
6. Performance tests if applicable

Target Coverage: {self.config.test_coverage_target * 100}%

Include:
- Test file structure and organization
- Test data setup and teardown
- Mock/stub strategies for dependencies
- Assertions for expected behavior
- Error condition testing
- Performance benchmarks

Format as structured response with test files and content.
"""
        
        response = self._call_llm(prompt, context)
        
        return {
            "test_suite": response,
            "files_created": [],  # Would contain actual test file paths
            "coverage_estimate": self.config.test_coverage_target
        }
    
    def analyze_test_coverage(self, repo_path: str) -> Dict[str, Any]:
        """Analyze current test coverage"""
        coverage_commands = [
            "python -m pytest --cov=. --cov-report=json",
            "npm run test:coverage",
            "cargo tarpaulin --out Json",
            "go test -coverprofile=coverage.out ./..."
        ]
        
        results = {}
        for cmd in coverage_commands:
            result = self._run_command(cmd, repo_path)
            if result["success"]:
                results[cmd] = result
                break
        
        return results
    
    def generate_feedback(self, test_suite: Dict[str, Any], coverage_report: Dict[str, Any]) -> str:
        """Generate feedback for implementation improvements"""
        context = f"""
Test Suite:
{json.dumps(test_suite, indent=2)}

Coverage Report:
{json.dumps(coverage_report, indent=2)}
"""
        
        prompt = f"""
Analyze the implementation and provide feedback for improvements.

Consider:
1. Test coverage gaps - areas needing more tests
2. Code quality issues - complexity, maintainability
3. Security concerns - potential vulnerabilities
4. Performance issues - optimization opportunities
5. Error handling - robustness improvements
6. Documentation - clarity and completeness

Target Coverage: {self.config.test_coverage_target * 100}%

Provide:
- Specific recommendations for improvement
- Priority levels for each recommendation
- Estimated effort for fixes
- Risk assessment for unaddressed issues

Format as structured Markdown with actionable items.
"""
        
        return self._call_llm(prompt, context)
    
    def _get_repo_structure(self, repo_path: str) -> str:
        """Get repository structure for context"""
        try:
            result = self._run_command(f"find {repo_path} -type f -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.go' -o -name '*.rs' | head -20")
            return result.get("stdout", "")
        except Exception:
            return ""
