"""
Command Line Interface for GitHub Workflow Manager
"""

import argparse
import os
import sys
import webbrowser
from pathlib import Path

import click
import requests
from rich.console import Console

from ..core.config import WorkflowConfig
from ..core.secret_vault import SecretVault
from ..core.workflow_manager import WorkflowManager
from ..github import REQUIRED_GITHUB_SCOPES, validate_github_token_scopes
from ..github.device_flow import GitHubDeviceFlow
from ..github.token_storage import (
    SecureTokenStorage,
    refresh_token_if_needed,
    validate_token,
)


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
        """,
    )

    # Global arguments
    parser.add_argument(
        "--token", help="GitHub personal access token (or set GITHUB_TOKEN)"
    )
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument(
        "--workspace", help="Workspace path (default: current directory)"
    )
    parser.add_argument("--config", help="Path to workflow config file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    setup_parser = subparsers.add_parser(
        "setup", help="Setup repository with labels and documentation"
    )
    setup_parser.add_argument(
        "--skip-docs", action="store_true", help="Skip creating documentation files"
    )

    # Process command
    process_parser = subparsers.add_parser(
        "process", help="Process an issue through Generate-Verify loop"
    )
    process_parser.add_argument(
        "--issue", type=int, required=True, help="Issue number to process"
    )
    process_parser.add_argument(
        "--phase",
        choices=["pm", "sde", "qa", "all"],
        default="all",
        help="Specific phase to run (default: all)",
    )

    # Init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize new project with workflow"
    )
    init_parser.add_argument(
        "--template",
        choices=["web", "api", "cli", "library"],
        default="library",
        help="Project template (default: library)",
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show workflow status")
    status_parser.add_argument(
        "--issue", type=int, help="Show status for specific issue"
    )

    # Next command
    next_parser = subparsers.add_parser(
        "next", help="Get highest-priority unblocked issue"
    )
    next_parser.add_argument("--assignee", help="Filter by assignee")
    next_parser.add_argument("--team", help="Filter by team")

    # Update command
    update_parser = subparsers.add_parser(
        "update", help="Update issue status and notes"
    )
    update_parser.add_argument("issue", type=int, help="Issue number to update")
    update_parser.add_argument("--status", help="Status label to add")
    update_parser.add_argument("--done", action="store_true", help="Close issue")
    update_parser.add_argument("--notes", help="Add a comment to the issue")

    # List command
    list_parser = subparsers.add_parser("list", help="List current tasks")
    list_parser.add_argument("--assignee", help="Filter by assignee")
    list_parser.add_argument("--team", help="Filter by team")
    list_parser.add_argument(
        "--mine", action="store_true", help="List tasks assigned to the caller"
    )
    list_parser.add_argument("--pinned", action="store_true", help="List pinned tasks")

    # Pin/Unpin commands
    pin_parser = subparsers.add_parser("pin", help="Pin an issue")
    pin_parser.add_argument("issue", type=int, help="Issue number to pin")
    unpin_parser = subparsers.add_parser("unpin", help="Unpin an issue")
    unpin_parser.add_argument("issue", type=int, help="Issue number to unpin")

    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Backlog doctor tools")
    doctor_sub = doctor_parser.add_subparsers(dest="doctor_cmd")
    run_parser = doctor_sub.add_parser("run", help="Run backlog checks")
    run_parser.add_argument("--stale-days", type=int, default=14)
    run_parser.add_argument("--checklist-limit", type=int, default=10)
    run_parser.add_argument(
        "--stale", action="store_true", help="Check only stale issues"
    )
    run_parser.add_argument(
        "--duplicates", action="store_true", help="Check only duplicate issues"
    )
    run_parser.add_argument(
        "--oversized", action="store_true", help="Check only oversized issues"
    )

    # Board command
    board_parser = subparsers.add_parser("board", help="Manage project board")
    board_sub = board_parser.add_subparsers(dest="board_cmd")
    board_init_parser = board_sub.add_parser("init", help="Initialize board fields")
    board_init_parser.add_argument(
        "--cache",
        help="Path to field cache file",
    )

    # Planning commands
    plan_parser = subparsers.add_parser("plan", help="Run planning workflow")
    plan_parser.add_argument("issue", type=int, help="Issue number")

    explain_parser = subparsers.add_parser(
        "explain", help="Explain ranking for an issue"
    )
    explain_parser.add_argument("issue", type=int, help="Issue number")

    tune_parser = subparsers.add_parser("tune", help="Customize ranking weights")
    tune_parser.add_argument("--weights", nargs="*", help="key=value pairs")

    subparsers.add_parser("memory", help="Show Planning Agent learning patterns")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit related commands")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd")
    audit_sub.add_parser("log", help="Show audit log")

    # Undo command
    undo_parser = subparsers.add_parser("undo", help="Undo operations")
    undo_parser.add_argument("hash", nargs="?", help="Operation hash")
    undo_parser.add_argument("--last", action="store_true", help="Undo last operation")

    # Slack command
    slack_parser = subparsers.add_parser("slack", help="Slack related commands")
    slack_parser.add_argument("--token", help="Slack API token")
    slack_sub = slack_parser.add_subparsers(dest="slack_cmd")
    slack_sub.add_parser("test", help="Test Slack authentication")
    slack_sub.add_parser("channels", help="List Slack channels")
    notify_parser = slack_sub.add_parser("notify", help="Send Slack notification")
    notify_parser.add_argument("channel", help="Channel ID")
    notify_parser.add_argument("message", help="Message text")

    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Manage authentication")
    auth_parser.add_argument(
        "action",
        choices=["login", "logout", "status", "github", "slack"],
        help="Auth action",
    )
    auth_parser.add_argument("--token", help="GitHub personal access token")
    auth_parser.add_argument("--slack-token", help="Slack API token")
    auth_parser.add_argument(
        "--install",
        action="store_true",
        help="Show Slack OAuth install URL (with action=slack)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize secret vault
    vault = SecretVault()

    # Authentication commands do not require a token upfront
    token = None
    storage = SecureTokenStorage()
    client_id = os.getenv("GITHUB_CLIENT_ID", "")
    if args.command != "auth":
        token = (
            args.token
            or os.getenv("GITHUB_TOKEN")
            or storage.get_token("github")
            or vault.get_secret("github_token")
        )

        # If no token and OAuth client id available, start device flow
        if not token and client_id:
            try:
                console = Console()
                console.print(
                    "\N{LOCK WITH INK PEN} [bold]Authenticating with GitHub...[/bold]"
                )
                flow = GitHubDeviceFlow(client_id)
                resp = flow.start_flow()
                console.print(
                    f"\n📋 Your device code: [bold cyan]{resp.user_code}[/bold cyan]"
                )
                console.print(
                    f"🌐 Please visit: [bold blue]{resp.verification_uri}[/bold blue]"
                )
                if click.confirm("Open browser automatically?", default=True):
                    webbrowser.open(resp.verification_uri)
                console.print("\n⏳ Waiting for authentication...")
                token = flow.poll_for_token(resp.device_code, resp.interval)
                vault.set_secret("github_token", token)
                storage.store_token("github", token)
            except Exception as e:
                print(f"Error: {e}")
                return 1

        if not token:
            print(
                "Error: GitHub token required. Use --token, set GITHUB_TOKEN, or store via 'autonomy auth login'."
            )
            return 1

        # Refresh/validate token when client id is available
        if client_id:
            try:
                new_token = refresh_token_if_needed(token, client_id)
                if new_token != token:
                    token = new_token
                    vault.set_secret("github_token", token)
                    storage.store_token("github", token)
            except Exception as e:
                print(f"Error: {e}")
                return 1

        # Validate PAT scopes
        try:
            validate_github_token_scopes(token, REQUIRED_GITHUB_SCOPES)
        except Exception as e:
            print(f"Error: {e}")
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

    manager = None
    if args.command != "auth":
        try:
            manager = WorkflowManager(
                github_token=token,
                owner=args.owner,
                repo=args.repo,
                workspace_path=str(workspace_path),
                config=config,
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
        elif args.command == "next":
            return cmd_next(manager, args)
        elif args.command == "update":
            return cmd_update(manager, args)
        elif args.command == "list":
            return cmd_list(manager, args)
        elif args.command == "pin":
            return cmd_pin(manager, args)
        elif args.command == "unpin":
            return cmd_unpin(manager, args)
        elif args.command == "plan":
            return cmd_plan(manager, args)
        elif args.command == "explain":
            return cmd_explain(manager, args)
        elif args.command == "tune":
            return cmd_tune(manager, args)
        elif args.command == "memory":
            return cmd_memory(manager, args)
        elif args.command == "doctor":
            if args.doctor_cmd == "run":
                return cmd_doctor(manager, args)
            print(f"Unknown doctor command: {args.doctor_cmd}")
            return 1
        elif args.command == "board":
            if args.board_cmd == "init":
                return cmd_board_init(manager, args)
            print(f"Unknown board command: {args.board_cmd}")
            return 1
        elif args.command == "audit":
            if args.audit_cmd == "log":
                return cmd_audit(manager, args)
            print(f"Unknown audit command: {args.audit_cmd}")
            return 1
        elif args.command == "undo":
            return cmd_undo(manager, args)
        elif args.command == "slack":
            return cmd_slack(vault, args)
        elif args.command == "auth":
            return cmd_auth(vault, args)
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


def cmd_next(manager: WorkflowManager, args) -> int:
    """Return the next best task."""
    from ..tasks.task_manager import TaskManager

    tm = TaskManager(manager.github_token, manager.owner, manager.repo)
    issue, breakdown = tm.get_next_task(
        assignee=args.assignee, team=args.team, explain=True
    )
    if not issue:
        print("No tasks found")
        return 0

    print(f"Next task: #{issue['number']} - {issue['title']}")
    if breakdown:
        print(
            f"  Priority score: {breakdown.get('priority')} age_penalty={breakdown.get('age_penalty')}"
        )
    return 0


def cmd_update(manager: WorkflowManager, args) -> int:
    """Update an issue's status or completion."""
    from ..tasks.task_manager import TaskManager

    tm = TaskManager(manager.github_token, manager.owner, manager.repo)
    success = tm.update_task(
        args.issue, status=args.status, done=args.done, notes=args.notes
    )
    if success:
        print("✓ Issue updated")
        return 0
    print("✗ Failed to update issue")
    return 1


def cmd_list(manager: WorkflowManager, args) -> int:
    """List open tasks."""
    from ..tasks.pinned_items import PinnedItemsStore
    from ..tasks.task_manager import TaskManager

    store = PinnedItemsStore()
    if args.pinned:
        pinned = store.list_pinned(f"{manager.owner}/{manager.repo}")
        if not pinned:
            print("No pinned items")
            return 0
        for num in pinned:
            issue = manager.issue_manager.get_issue(int(num))
            title = issue.get("title") if issue else ""
            print(f"#{num}: {title}")
        return 0

    tm = TaskManager(manager.github_token, manager.owner, manager.repo)
    assignee = args.assignee
    if args.mine:
        assignee = assignee or os.getenv("GITHUB_USER")
    issues = tm.list_tasks(assignee=assignee, team=args.team)
    if not issues:
        print("No tasks found")
        return 0
    for issue in issues:
        print(f"#{issue['number']}: {issue['title']}")
    return 0


def cmd_pin(manager: WorkflowManager, args) -> int:
    """Pin an issue."""
    from ..tasks.pinned_items import PinnedItemsStore

    store = PinnedItemsStore()
    store.pin_item(f"{manager.owner}/{manager.repo}", str(args.issue))
    print(f"\N{CHECK MARK} Issue #{args.issue} pinned")
    return 0


def cmd_unpin(manager: WorkflowManager, args) -> int:
    """Unpin an issue."""
    from ..tasks.pinned_items import PinnedItemsStore

    store = PinnedItemsStore()
    store.unpin_item(f"{manager.owner}/{manager.repo}", str(args.issue))
    print(f"\N{CHECK MARK} Issue #{args.issue} unpinned")
    return 0


def cmd_plan(manager: WorkflowManager, args) -> int:
    """Run planning workflow."""
    from ..core.platform import AutonomyPlatform
    from ..planning.langgraph_workflow import LangGraphPlanningWorkflow

    issue = manager.issue_manager.get_issue(args.issue) or {}
    issue["issue_id"] = str(args.issue)
    issue.setdefault("repository", "default")
    platform = AutonomyPlatform()
    wf = platform.create_workflow(LangGraphPlanningWorkflow)
    result = wf.run(issue)
    score = result.state.data.get("priority_score")
    print(f"Priority score: {score}")
    return 0


def cmd_explain(manager: WorkflowManager, args) -> int:
    """Explain ranking for an issue."""
    from ..tasks.ranking import RankingEngine

    issue = manager.issue_manager.get_issue(args.issue) or {}
    eng = RankingEngine()
    score, breakdown = eng.score_issue(issue, explain=True)
    print(f"Score: {score}")
    for k, v in breakdown.items():
        print(f"  {k}: {v}")
    return 0


def cmd_tune(manager: WorkflowManager, args) -> int:
    """Write ranking weights to config file."""
    from pathlib import Path

    import yaml

    weights = {}
    for pair in args.weights or []:
        if "=" in pair:
            k, v = pair.split("=", 1)
            try:
                weights[k] = float(v)
            except ValueError:
                pass
    cfg_path = Path(".autonomy.yml")
    data = {"weights": weights}
    cfg_path.write_text(yaml.safe_dump(data))
    print("✓ Configuration updated")
    return 0


def cmd_memory(manager: WorkflowManager, args) -> int:
    """Display learned patterns."""
    from ..core.platform import AutonomyPlatform

    platform = AutonomyPlatform()
    if not platform.memory.store:
        print("No patterns learned yet")
        return 0
    for repo, data in platform.memory.store.items():
        print(f"Repository: {repo}")
        for k, v in data.items():
            print(f"  {k}: {v}")
    return 0


def cmd_doctor(manager: WorkflowManager, args) -> int:
    """Run backlog doctor checks."""
    from ..tasks.backlog_doctor import BacklogDoctor

    doctor = BacklogDoctor(manager.issue_manager)
    only_flags = args.stale or args.duplicates or args.oversized
    results = doctor.run(
        stale_days=args.stale_days,
        checklist_limit=args.checklist_limit,
        check_stale=args.stale or not only_flags,
        check_duplicates=args.duplicates or not only_flags,
        check_oversized=args.oversized or not only_flags,
    )
    if results["stale"]:
        print(f"Stale issues: {', '.join(map(str, results['stale']))}")
    if results["duplicates"]:
        print("Duplicate candidates:")
        for a, b in results["duplicates"]:
            print(f"  #{a} <-> #{b}")
    if results["oversized"]:
        print(f"Oversized issues: {', '.join(map(str, results['oversized']))}")
    return 0


def cmd_board_init(manager: WorkflowManager, args) -> int:
    """Initialize project board fields."""
    from ..github.board_manager import BoardManager

    cache_path = (
        Path(args.cache).expanduser()
        if getattr(args, "cache", None)
        else Path(manager.config.board_cache_path).expanduser()
    )
    bm = BoardManager(
        manager.github_token,
        manager.owner,
        manager.repo,
        cache_path=cache_path,
    )
    try:
        bm.init_board()
        print("✓ Board initialized")
        return 0
    except Exception as e:
        print(f"✗ Board initialization failed: {e}")
        return 1


def cmd_audit(manager: WorkflowManager, args) -> int:
    """Show audit log entries."""
    for entry in manager.audit_logger.iter_logs():
        ts = entry.get("timestamp")
        op = entry.get("operation")
        h = entry.get("hash")
        print(f"{ts} {h} {op}")
    return 0


def cmd_undo(manager: WorkflowManager, args) -> int:
    """Undo a previously logged operation."""
    from ..audit.undo import UndoManager

    um = UndoManager(manager.issue_manager, manager.audit_logger)
    if args.last:
        result = um.undo_last()
        if not result:
            print("No operations to undo")
            return 1
        print(f"✓ Undid {result}")
        return 0
    if args.hash:
        if um.undo(args.hash):
            print(f"✓ Undid {args.hash}")
            return 0
        print("✗ Undo failed")
        return 1
    print("Error: provide hash or --last")
    return 1


def cmd_auth(vault: SecretVault, args) -> int:
    """Authentication commands."""
    if args.action == "login":
        gh_token = args.token or os.getenv("GITHUB_TOKEN")
        slack_token = args.slack_token or os.getenv("SLACK_TOKEN")
        storage = SecureTokenStorage()
        if not gh_token and not slack_token:
            client_id = os.getenv("GITHUB_CLIENT_ID")
            if not client_id:
                print("Error: provide --token or set GITHUB_CLIENT_ID for OAuth login")
                return 1
            try:
                console = Console()
                console.print(
                    "\N{LOCK WITH INK PEN} [bold]Authenticating with GitHub...[/bold]"
                )
                flow = GitHubDeviceFlow(client_id)
                resp = flow.start_flow()
                console.print(
                    f"\n📋 Your device code: [bold cyan]{resp.user_code}[/bold cyan]"
                )
                console.print(
                    f"🌐 Please visit: [bold blue]{resp.verification_uri}[/bold blue]"
                )
                if click.confirm("Open browser automatically?", default=True):
                    webbrowser.open(resp.verification_uri)
                console.print("\n⏳ Waiting for authentication...")
                gh_token = flow.poll_for_token(resp.device_code, resp.interval)
            except Exception as e:
                print(f"Error: {e}")
                return 1
        if gh_token:
            vault.set_secret("github_token", gh_token)
            storage.store_token("github", gh_token)
            print("✓ GitHub token stored in vault")
        if slack_token:
            vault.set_secret("slack_token", slack_token)
            print("✓ Slack token stored in vault")
        return 0

    if args.action == "logout":
        vault.delete_secret("github_token")
        vault.delete_secret("slack_token")
        print("✓ Credentials removed")
        return 0

    if args.action == "status":
        storage = SecureTokenStorage()
        gh_token = (
            args.token
            or os.getenv("GITHUB_TOKEN")
            or storage.get_token("github")
            or vault.get_secret("github_token")
        )
        slack_token = (
            args.slack_token
            or os.getenv("SLACK_TOKEN")
            or vault.get_secret("slack_token")
        )
        gh_status = (
            "logged in" if gh_token and validate_token(gh_token) else "not logged in"
        )
        print(f"GitHub: {gh_status}")
        print(f"Slack: {'logged in' if slack_token else 'not logged in'}")
        return 0

    if args.action == "github":
        storage = SecureTokenStorage()
        token = (
            args.token
            or os.getenv("GITHUB_TOKEN")
            or storage.get_token("github")
            or vault.get_secret("github_token")
        )
        if not token:
            print("Error: GitHub token not found")
            return 1
        client_id = os.getenv("GITHUB_CLIENT_ID", "")
        token = refresh_token_if_needed(token, client_id) if client_id else token
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {token}"},
                timeout=10,
            )
            if response.status_code == 200:
                print(response.json().get("login"))
                return 0
            print(f"Error: {response.status_code} {response.text}")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1

    if args.action == "slack":
        from ..slack import SlackOAuth, get_slack_auth_info

        if args.install:
            client_id = os.getenv("SLACK_CLIENT_ID")
            if not client_id:
                print("Error: SLACK_CLIENT_ID not set")
                return 1
            oauth = SlackOAuth(client_id, os.getenv("SLACK_CLIENT_SECRET", ""))
            print(oauth.get_install_url())
            return 0

        if args.slack_token:
            vault.set_secret("slack_token", args.slack_token)
            print("✓ Slack token stored in vault")
            return 0

        token = (
            args.slack_token
            or os.getenv("SLACK_TOKEN")
            or vault.get_secret("slack_token")
        )
        if not token:
            print("Slack: not logged in")
            return 0
        try:
            info = get_slack_auth_info(token)
            print(info.get("team", info.get("team_id", "unknown")))
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    print("Unknown auth action")
    return 1


def cmd_slack(vault: SecretVault, args) -> int:
    """Slack-specific commands."""
    token = args.token or vault.get_secret("slack_token")
    if not token:
        print("Error: Slack token not found")
        return 1

    if args.slack_cmd == "test":
        from ..slack import get_slack_auth_info

        try:
            get_slack_auth_info(token)
            print("✓ Slack authentication successful")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    if args.slack_cmd == "channels":
        import requests

        response = requests.get(
            "https://slack.com/api/conversations.list",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        data = response.json()
        if response.status_code != 200 or not data.get("ok"):
            print("Error: failed to list channels")
            return 1
        for ch in data.get("channels", []):
            print(f"{ch['id']}: {ch['name']}")
        return 0

    if args.slack_cmd == "notify":
        from ..slack import SlackBot

        bot = SlackBot(token)
        if bot.post_message(args.channel, args.message):
            print("\N{CHECK MARK} Notification sent")
            return 0
        print("Error: failed to send notification")
        return 1

    print(f"Unknown Slack command: {args.slack_cmd}")
    return 1


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
            "test:coverage": "vitest --coverage",
        },
        "devDependencies": {
            "vite": "^4.0.0",
            "vitest": "^0.28.0",
            "@vitejs/plugin-react": "^3.0.0",
        },
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
        "httpx>=0.24.0",
    ]

    with open(workspace_path / "requirements.txt", "w") as f:
        f.write("\n".join(requirements))


def _create_cli_template(workspace_path: Path) -> None:
    """Create CLI template"""
    (workspace_path / "src").mkdir(exist_ok=True)
    (workspace_path / "tests").mkdir(exist_ok=True)

    # Create setup.py template
    setup_content = (
        '''
from setuptools import setup, find_packages

setup(
    name="'''
        + workspace_path.name
        + '''",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "'''
        + workspace_path.name
        + """=src.main:main",
        ],
    },
    install_requires=[
        "click>=8.0.0",
    ],
)
"""
    )

    with open(workspace_path / "setup.py", "w") as f:
        f.write(setup_content.strip())


def _create_library_template(workspace_path: Path) -> None:
    """Create library template"""
    (workspace_path / "src").mkdir(exist_ok=True)
    (workspace_path / "tests").mkdir(exist_ok=True)

    # Create __init__.py
    with open(workspace_path / "src" / "__init__.py", "w") as f:
        f.write(
            f'''"""
{workspace_path.name}

A Python library created with GitHub Workflow Manager.
"""

__version__ = "0.1.0"
'''
        )


if __name__ == "__main__":
    sys.exit(main())
