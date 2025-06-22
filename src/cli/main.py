"""
Command Line Interface for GitHub Workflow Manager
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from ..core.workflow_manager import WorkflowManager
from ..core.config import WorkflowConfig


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GitHub Workflow Manager - Generate-Verify Loop with AI Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup repository with labels and documentation
  github-workflow setup --token $GITHUB_TOKEN --owner myorg --repo myproject
  
  # Process an issue through the Generate-Verify loop
  github-workflow process --token $GITHUB_TOKEN --owner myorg --repo myproject --issue 42
  
  # Initialize a new project with workflow
  github-workflow init --token $GITHUB_TOKEN --owner myorg --repo myproject --workspace ./my-project

Environment Variables:
  GITHUB_TOKEN    GitHub personal access token
  WORKSPACE_PATH  Default workspace path (default: current directory)
        """
    )
    
    # Global arguments
    parser.add_argument("--token", help="GitHub personal access token (or set GITHUB_TOKEN)")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--workspace", help="Workspace path (default: current directory)")
    parser.add_argument("--config", help="Path to workflow config file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup repository with labels and documentation")
    setup_parser.add_argument("--skip-docs", action="store_true", help="Skip creating documentation files")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process an issue through Generate-Verify loop")
    process_parser.add_argument("--issue", type=int, required=True, help="Issue number to process")
    process_parser.add_argument("--phase", choices=["pm", "sde", "qa", "all"], default="all", 
                               help="Specific phase to run (default: all)")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize new project with workflow")
    init_parser.add_argument("--template", choices=["web", "api", "cli", "library"], default="library",
                           help="Project template (default: library)")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show workflow status")
    status_parser.add_argument("--issue", type=int, help="Show status for specific issue")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Get GitHub token
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GitHub token required. Use --token or set GITHUB_TOKEN environment variable.")
        return 1
    
    # Get workspace path
    workspace = args.workspace or os.getenv("WORKSPACE_PATH", ".")
    workspace_path = Path(workspace).resolve()
    
    # Load configuration
    config = None
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            import json
            with open(config_path) as f:
                config_data = json.load(f)
            config = WorkflowConfig.from_dict(config_data)
    
    if not config:
        config = WorkflowConfig()
    
    # Initialize workflow manager
    try:
        manager = WorkflowManager(
            github_token=token,
            owner=args.owner,
            repo=args.repo,
            workspace_path=str(workspace_path),
            config=config
        )
    except Exception as e:
        print(f"Error initializing workflow manager: {e}")
        return 1
    
    # Execute command
    try:
        if args.command == "setup":
            return cmd_setup(manager, args)
        elif args.command == "process":
            return cmd_process(manager, args)
        elif args.command == "init":
            return cmd_init(manager, args)
        elif args.command == "status":
            return cmd_status(manager, args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        print(f"Error executing command: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_setup(manager: WorkflowManager, args) -> int:
    """Setup repository command"""
    print(f"Setting up repository {manager.owner}/{manager.repo}...")
    
    try:
        manager.setup_repository()
        print("✓ Repository setup complete")
        return 0
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return 1


def cmd_process(manager: WorkflowManager, args) -> int:
    """Process issue command"""
    print(f"Processing issue #{args.issue} through Generate-Verify loop...")
    
    try:
        result = manager.process_issue(args.issue)
        
        if result.get("error"):
            print(f"✗ Error: {result['error']}")
            return 1
        
        print(f"✓ Issue #{args.issue} processed")
        print(f"  Status: {result.get('status', 'unknown')}")
        print(f"  Phases completed: {', '.join(result.get('phases_completed', []))}")
        
        if result.get("artifacts_created"):
            print(f"  Artifacts created: {len(result['artifacts_created'])}")
            for artifact in result["artifacts_created"]:
                print(f"    - {artifact}")
        
        if result.get("next_action"):
            print(f"  Next action: {result['next_action']}")
        
        return 0
    except Exception as e:
        print(f"✗ Processing failed: {e}")
        return 1


def cmd_init(manager: WorkflowManager, args) -> int:
    """Initialize project command"""
    print(f"Initializing new project with {args.template} template...")
    
    try:
        # Setup repository first
        manager.setup_repository()
        
        # Create template-specific files
        if args.template == "web":
            _create_web_template(manager.workspace_path)
        elif args.template == "api":
            _create_api_template(manager.workspace_path)
        elif args.template == "cli":
            _create_cli_template(manager.workspace_path)
        else:  # library
            _create_library_template(manager.workspace_path)
        
        print("✓ Project initialized successfully")
        print(f"  Template: {args.template}")
        print(f"  Workspace: {manager.workspace_path}")
        
        return 0
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return 1


def cmd_status(manager: WorkflowManager, args) -> int:
    """Show status command"""
    if args.issue:
        print(f"Status for issue #{args.issue}:")
        # In real implementation, would fetch issue status
        print("  Phase: needs-development")
        print("  Agent: sde-agent")
        print("  Last updated: 2 hours ago")
    else:
        print(f"Workflow status for {manager.owner}/{manager.repo}:")
        print("  Active issues: 5")
        print("  Pending review: 2")
        print("  Ready to merge: 1")
    
    return 0


def _create_web_template(workspace_path: Path) -> None:
    """Create web application template"""
    # Create basic web app structure
    (workspace_path / "src").mkdir(exist_ok=True)
    (workspace_path / "tests").mkdir(exist_ok=True)
    (workspace_path / "public").mkdir(exist_ok=True)
    
    # Create package.json
    package_json = {
        "name": workspace_path.name,
        "version": "0.1.0",
        "scripts": {
            "start": "npm run dev",
            "dev": "vite",
            "build": "vite build",
            "test": "vitest",
            "test:coverage": "vitest --coverage"
        },
        "devDependencies": {
            "vite": "^4.0.0",
            "vitest": "^0.28.0",
            "@vitejs/plugin-react": "^3.0.0"
        }
    }
    
    import json
    with open(workspace_path / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)


def _create_api_template(workspace_path: Path) -> None:
    """Create API template"""
    (workspace_path / "src").mkdir(exist_ok=True)
    (workspace_path / "tests").mkdir(exist_ok=True)
    
    # Create requirements.txt
    requirements = [
        "fastapi>=0.68.0",
        "uvicorn[standard]>=0.15.0",
        "pydantic>=1.8.0",
        "pytest>=6.0.0",
        "pytest-asyncio>=0.18.0",
        "httpx>=0.24.0"
    ]
    
    with open(workspace_path / "requirements.txt", "w") as f:
        f.write("\n".join(requirements))


def _create_cli_template(workspace_path: Path) -> None:
    """Create CLI template"""
    (workspace_path / "src").mkdir(exist_ok=True)
    (workspace_path / "tests").mkdir(exist_ok=True)
    
    # Create setup.py template
    setup_content = '''
from setuptools import setup, find_packages

setup(
    name="''' + workspace_path.name + '''",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "''' + workspace_path.name + '''=src.main:main",
        ],
    },
    install_requires=[
        "click>=8.0.0",
    ],
)
'''
    
    with open(workspace_path / "setup.py", "w") as f:
        f.write(setup_content.strip())


def _create_library_template(workspace_path: Path) -> None:
    """Create library template"""
    (workspace_path / "src").mkdir(exist_ok=True)
    (workspace_path / "tests").mkdir(exist_ok=True)
    
    # Create __init__.py
    with open(workspace_path / "src" / "__init__.py", "w") as f:
        f.write(f'"""
{workspace_path.name}

A Python library created with GitHub Workflow Manager.
"""

__version__ = "0.1.0"
')


if __name__ == "__main__":
    sys.exit(main())
