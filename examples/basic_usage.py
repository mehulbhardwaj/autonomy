#!/usr/bin/env python3
"""
Basic usage example for Autonomy MCP.

This example demonstrates:
1. Setting up a WorkflowManager
2. Processing issues through the Generate-Verify loop
3. Using different autonomy levels
"""

import os

from src import WorkflowConfig, WorkflowManager, quick_setup


def main():
    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Please set GITHUB_TOKEN environment variable")
        return

    # Example 1: Quick setup for new project
    print("=== Quick Setup Example ===")
    manager = quick_setup(
        github_token=github_token, owner="myorg", repo="my-new-project", template="api"
    )
    print("Repository setup complete!")

    # Example 2: Manual configuration
    print("\n=== Manual Configuration Example ===")
    config = WorkflowConfig(
        max_file_lines=250,
        max_function_lines=30,
        test_coverage_target=0.8,
        autonomy_level="supervised",
        require_human_approval=True,
    )

    manager = WorkflowManager(
        github_token=github_token, owner="myorg", repo="my-project", config=config
    )

    # Setup repository if needed
    try:
        manager.setup_repository()
        print("Repository configured successfully!")
    except Exception as e:
        print(f"Repository setup failed: {e}")

    # Example 3: Process a specific issue
    print("\n=== Issue Processing Example ===")
    try:
        # Process issue #42 through the complete Generate-Verify loop
        result = manager.process_issue(issue_number=42)

        print(f"Issue #{result.issue_number} processed")
        print(f"Status: {result.status}")
        print(f"Current phase: {result.current_phase}")

        if result.success:
            print("✅ Issue processed successfully!")
        else:
            print("❌ Issue processing failed:")
            for error in result.errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"Issue processing failed: {e}")

    # Example 4: Process multiple issues
    print("\n=== Batch Processing Example ===")
    try:
        # Process all ready issues
        results = manager.process_ready_issues()

        print(f"Processed {len(results)} issues:")
        for result in results:
            status_icon = "✅" if result.success else "❌"
            print(f"  {status_icon} Issue #{result.issue_number}: {result.status}")

    except Exception as e:
        print(f"Batch processing failed: {e}")

    # Example 5: Phase-specific processing
    print("\n=== Phase-Specific Processing Example ===")
    issue_number = 43

    try:
        # PM phase - requirements and design
        pm_result = manager.process_issue(issue_number, phase="pm")
        print(f"PM phase result: {pm_result.status}")

        # SDE phase - implementation
        sde_result = manager.process_issue(issue_number, phase="sde")
        print(f"SDE phase result: {sde_result.status}")

        # QA phase - testing and validation
        qa_result = manager.process_issue(issue_number, phase="qa")
        print(f"QA phase result: {qa_result.status}")

    except Exception as e:
        print(f"Phase processing failed: {e}")

    # Example 6: Repository status check
    print("\n=== Status Check Example ===")
    try:
        status = manager.get_repository_status()

        print(f"Repository: {status.owner}/{status.repo}")
        print(f"Open issues: {status.open_issues}")
        print(f"In progress: {status.in_progress}")
        print(f"Ready for review: {status.ready_for_review}")
        print(f"Labels configured: {status.labels_configured}")
        print(f"Milestones configured: {status.milestones_configured}")

    except Exception as e:
        print(f"Status check failed: {e}")


if __name__ == "__main__":
    main()
