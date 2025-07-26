"""Command Line Interface for GitHub Workflow Manager"""

from __future__ import annotations

import argparse
import os
import shlex
import sys
import webbrowser
from pathlib import Path
from types import SimpleNamespace

from ..core.errors import handle_errors

os.environ.setdefault("POSTHOG_DISABLED", "1")
# Disable Mem0 telemetry by default to avoid network delays on startup
os.environ.setdefault("MEM0_TELEMETRY", "False")

# Placeholders for optional heavy imports
click = SimpleNamespace(confirm=lambda *a, **kw: True)
requests = None
Console = None
WorkflowConfig = None
SecretVault = None
WorkflowManager = None
REQUIRED_GITHUB_SCOPES = None
validate_github_token_scopes = None
GitHubDeviceFlow = None
SecureTokenStorage = None
refresh_token_if_needed = None
validate_token = None
Table = None


def _ensure_imports() -> None:
    """Load heavy dependencies if not already loaded."""
    global click, requests, Console, Table
    global WorkflowConfig, SecretVault, WorkflowManager
    global REQUIRED_GITHUB_SCOPES, validate_github_token_scopes
    global GitHubDeviceFlow, SecureTokenStorage, refresh_token_if_needed, validate_token

    if click is None:
        import click  # type: ignore

        click = click
    if requests is None:
        import requests  # type: ignore

        requests = requests
    if Console is None:
        from rich.console import Console as _Console  # type: ignore
        from rich.table import Table as _Table  # type: ignore

        Console = _Console
        Table = _Table  # noqa: F841
    if WorkflowConfig is None:
        from ..core.config import WorkflowConfig as _WorkflowConfig

        WorkflowConfig = _WorkflowConfig

    if SecretVault is None:
        from ..core.secret_vault import SecretVault as _SecretVault

        SecretVault = _SecretVault

    if WorkflowManager is None:
        from ..core.workflow_manager import WorkflowManager as _WorkflowManager

        WorkflowManager = _WorkflowManager

    if REQUIRED_GITHUB_SCOPES is None:
        from ..github import REQUIRED_GITHUB_SCOPES as _SCOPES

        REQUIRED_GITHUB_SCOPES = _SCOPES

    if validate_github_token_scopes is None:
        from ..github import validate_github_token_scopes as _validate

        validate_github_token_scopes = _validate

    if GitHubDeviceFlow is None:
        from ..github.device_flow import GitHubDeviceFlow as _GitHubDeviceFlow

        GitHubDeviceFlow = _GitHubDeviceFlow

    if SecureTokenStorage is None:
        from ..github.token_storage import SecureTokenStorage as _SecureTokenStorage
        from ..github.token_storage import (
            refresh_token_if_needed as _refresh_token_if_needed,
        )
        from ..github.token_storage import validate_token as _validate_token

        SecureTokenStorage = _SecureTokenStorage
        refresh_token_if_needed = _refresh_token_if_needed
        validate_token = _validate_token


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser."""
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
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument(
        "--log-json",
        action="store_true",
        help="Write logs to autonomy.log in JSON format",
    )

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
    next_parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )
    next_parser.add_argument("--quiet", action="store_true", help="Minimal output")

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

    nightly_parser = doctor_sub.add_parser(
        "nightly", help="Schedule nightly backlog digest"
    )
    nightly_parser.add_argument("--repos", nargs="+", help="owner/repo list")
    nightly_parser.add_argument("--channel", default="#autonomy-daily")
    nightly_parser.add_argument("--time", default="02:00")
    nightly_parser.add_argument("--slack-token")
    nightly_parser.add_argument("--forever", action="store_true")

    metrics_parser = subparsers.add_parser("metrics", help="Metrics related commands")
    metrics_sub = metrics_parser.add_subparsers(dest="metrics_cmd")

    daily_parser = metrics_sub.add_parser("daily", help="Schedule daily metrics digest")
    daily_parser.add_argument("--repos", nargs="+", help="owner/repo list")
    daily_parser.add_argument("--channel", default="#autonomy-metrics")
    daily_parser.add_argument("--time", default="09:00")
    daily_parser.add_argument("--slack-token")
    daily_parser.add_argument("--forever", action="store_true")

    metrics_sub.add_parser("export", help="Export metrics in Prometheus format")

    # Board command
    board_parser = subparsers.add_parser("board", help="Manage project board")
    board_sub = board_parser.add_subparsers(dest="board_cmd")
    board_init_parser = board_sub.add_parser("init", help="Initialize board fields")
    board_init_parser.add_argument("--cache", help="Path to field cache file")
    board_sub.add_parser("reorder", help="Reorder board items by priority")
    board_rank_parser = board_sub.add_parser("rank", help="Show ranked board items")
    board_rank_parser.add_argument("--json", action="store_true", help="Output JSON")

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

    subparsers.add_parser("rerank", help="Re-evaluate priority ranking for open issues")

    assign_parser = subparsers.add_parser("assign", help="Assign an issue to a user")
    assign_parser.add_argument("issue", type=int, help="Issue number")
    assign_parser.add_argument("--to", required=True, help="Username")

    breakdown_parser = subparsers.add_parser(
        "breakdown", help="Decompose an issue into tasks"
    )
    breakdown_parser.add_argument("issue", type=int, help="Issue number")

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

    # New commands
    subparsers.add_parser("interactive", help="Start interactive shell")
    comp_parser = subparsers.add_parser(
        "completion", help="Output shell completion script"
    )
    comp_parser.add_argument(
        "--shell", default="bash", choices=["bash", "zsh"], help="Shell type"
    )

    subparsers.add_parser("configure", help="Create default configuration")

    return parser


def _dispatch_command(
    manager: WorkflowManager, vault: SecretVault, parser: argparse.ArgumentParser, args
) -> int:
    """Dispatch CLI command to its handler."""
    if args.command == "setup":
        return cmd_setup(manager, args)
    if args.command == "process":
        return cmd_process(manager, args)
    if args.command == "init":
        return cmd_init(manager, args)
    if args.command == "status":
        return cmd_status(manager, args)
    if args.command == "next":
        return cmd_next(manager, args)
    if args.command == "update":
        return cmd_update(manager, args)
    if args.command == "list":
        return cmd_list(manager, args)
    if args.command == "pin":
        return cmd_pin(manager, args)
    if args.command == "unpin":
        return cmd_unpin(manager, args)
    if args.command == "plan":
        return cmd_plan(manager, args)
    if args.command == "explain":
        return cmd_explain(manager, args)
    if args.command == "tune":
        return cmd_tune(manager, args)
    if args.command == "rerank":
        return cmd_rerank(manager, args)
    if args.command == "assign":
        return cmd_assign(manager, args)
    if args.command == "breakdown":
        return cmd_breakdown(manager, args)
    if args.command == "memory":
        return cmd_memory(manager, args)
    if args.command == "doctor":
        if args.doctor_cmd == "run":
            return cmd_doctor(manager, args)
        if args.doctor_cmd == "nightly":
            return cmd_doctor_nightly(manager, vault, args)
        print(f"Unknown doctor command: {args.doctor_cmd}")
        return 1
    if args.command == "metrics":
        if args.metrics_cmd in {None, "daily"}:
            return cmd_metrics_daily(manager, vault, args)
        if args.metrics_cmd == "export":
            return cmd_metrics_export(manager, args)
        print(f"Unknown metrics command: {args.metrics_cmd}")
        return 1
    if args.command == "board":
        if args.board_cmd == "init":
            return cmd_board_init(manager, args)
        if args.board_cmd == "reorder":
            return cmd_board_reorder(manager, args)
        if args.board_cmd == "rank":
            return cmd_board_rank(manager, args)
        print(f"Unknown board command: {args.board_cmd}")
        return 1
    if args.command == "audit":
        if args.audit_cmd == "log":
            return cmd_audit(manager, args)
        print(f"Unknown audit command: {args.audit_cmd}")
        return 1
    if args.command == "undo":
        return cmd_undo(manager, args)
    if args.command == "slack":
        return cmd_slack(vault, args)
    if args.command == "auth":
        return cmd_auth(vault, args)
    if args.command == "interactive":
        return cmd_interactive(manager, parser)
    if args.command == "completion":
        return cmd_completion(parser, args)
    if args.command == "configure":
        return cmd_configure(args)
    print(f"Unknown command: {args.command}")
    return 1


def main():
    """Main CLI entry point"""
    if {"-h", "--help"} & set(sys.argv[1:]):
        print("GitHub Workflow Manager")
        os._exit(0)
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    _ensure_imports()

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
            if config_path.suffix in {".yml", ".yaml"}:
                config = WorkflowConfig.from_yaml(config_path)
            else:
                import json

                with open(config_path) as f:
                    config_data = json.load(f)
                config = WorkflowConfig.from_dict(config_data)

    if not config:
        config = WorkflowConfig.load_default()
    try:
        config.validate()
    except Exception as e:
        print(f"Configuration error: {e}")
        return 1

    manager = None
    if args.command != "auth":
        try:
            manager = WorkflowManager(
                github_token=token,
                owner=args.owner,
                repo=args.repo,
                workspace_path=str(workspace_path),
                config=config,
                log_json=args.log_json,
            )
        except Exception as e:
            print(f"Error initializing workflow manager: {e}")
            return 1

    # Execute command
    try:
        return _dispatch_command(manager, vault, parser, args)
    except Exception as e:
        print(f"Error executing command: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


@handle_errors
def cmd_setup(manager: WorkflowManager, args) -> int:
    """Setup repository command"""
    print(f"Setting up repository {manager.owner}/{manager.repo}...")

    manager.setup_repository()
    print("✓ Repository setup complete")
    return 0


@handle_errors
def cmd_process(manager: WorkflowManager, args) -> int:
    """Process issue command"""
    console = Console()
    console.print(f"Processing issue #{args.issue} through Generate-Verify loop...")
    from rich.progress import Progress

    with Progress(transient=True) as progress:
        task = progress.add_task("Running", total=None)
        result = manager.process_issue(args.issue)
        progress.update(task, completed=1)

    if result.get("error"):
        console.print(f"[red]✗ Error: {result['error']}[/red]")
        return 1

    console.print(f"[green]✓ Issue #{args.issue} processed[/green]")
    console.print(f"  Status: {result.get('status', 'unknown')}")
    console.print(
        f"  Phases completed: {', '.join(result.get('phases_completed', []))}"
    )

    if result.get("artifacts_created"):
        console.print(f"  Artifacts created: {len(result['artifacts_created'])}")
        for artifact in result["artifacts_created"]:
            console.print(f"    - {artifact}")

    if result.get("next_action"):
        console.print(f"  Next action: {result['next_action']}")

    return 0


@handle_errors
def cmd_init(manager: WorkflowManager, args) -> int:
    """Initialize project command"""
    print(f"Initializing new project with {args.template} template...")

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
    _ensure_imports()
    from ..tasks.task_manager import TaskManager

    tm = TaskManager(manager.github_token, manager.owner, manager.repo)
    result = tm.get_next_task(
        assignee=args.assignee,
        team=args.team,
        explain=True,
    )
    issue, breakdown = result if isinstance(result, tuple) else (result, {})
    if not issue:
        Console().print("No tasks found")
        return 0

    score = tm._score_issue(issue)
    if getattr(args, "json", False):
        import json

        Console().print(
            json.dumps(
                {
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "score": score,
                    "breakdown": breakdown,
                },
                indent=2,
            )
        )
    else:
        if getattr(args, "quiet", False):
            print(issue.get("number"))
        else:
            console = Console()
            console.print(f"Next task: #{issue.get('number')} - {issue.get('title')}")
            console.print(f"Priority score: {score:.2f}")
            for k, v in breakdown.items():
                console.print(f"  {k}: {v}")
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
    from ..core.platform import AutonomyPlatform
    from ..planning.workflow import PlanningWorkflow

    platform = AutonomyPlatform(
        github_token=manager.github_token,
        owner=manager.owner,
        repo=manager.repo,
    )
    wf = platform.create_workflow(PlanningWorkflow)
    wf.learn_from_override(
        str(args.issue),
        {"pinned": False},
        {"pinned": True},
        repository="default",
    )
    print(f"\N{CHECK MARK} Issue #{args.issue} pinned")
    return 0


def cmd_unpin(manager: WorkflowManager, args) -> int:
    """Unpin an issue."""
    from ..tasks.pinned_items import PinnedItemsStore

    store = PinnedItemsStore()
    store.unpin_item(f"{manager.owner}/{manager.repo}", str(args.issue))
    from ..core.platform import AutonomyPlatform
    from ..planning.workflow import PlanningWorkflow

    platform = AutonomyPlatform(
        github_token=manager.github_token,
        owner=manager.owner,
        repo=manager.repo,
    )
    wf = platform.create_workflow(PlanningWorkflow)
    wf.learn_from_override(
        str(args.issue),
        {"pinned": True},
        {"pinned": False},
        repository="default",
    )
    print(f"\N{CHECK MARK} Issue #{args.issue} unpinned")
    return 0


def cmd_plan(manager: WorkflowManager, args) -> int:
    """Run planning workflow."""
    from ..core.platform import AutonomyPlatform
    from ..planning.langgraph_workflow import LangGraphPlanningWorkflow

    issue = manager.issue_manager.get_issue(args.issue) or {}
    issue["issue_id"] = str(args.issue)
    issue.setdefault("repository", "default")
    platform = AutonomyPlatform(
        github_token=manager.github_token,
        owner=manager.owner,
        repo=manager.repo,
    )
    wf = platform.create_workflow(LangGraphPlanningWorkflow)
    result = wf.run(issue)
    state = result.state.data

    print(f"Priority score: {state.get('priority_score')}")
    if state.get("analysis"):
        print(f"Analysis: {state['analysis']}")

    tasks = state.get("tasks", [])
    if tasks:
        print("Tasks:")
        for t in tasks:
            print(f"- {t}")

    if state.get("assignee"):
        print(f"Assignee: {state['assignee']}")

    if state.get("plan"):
        print("Plan:")
        print(state["plan"])

    return 0


def cmd_explain(manager: WorkflowManager, args) -> int:
    """Explain ranking for an issue."""
    from ..tasks.ranking import RankingEngine

    issue = manager.issue_manager.get_issue(args.issue) or {}
    eng = RankingEngine()
    score, breakdown = eng.score_issue(issue, explain=True)
    print(f"Score: {score:.2f}")
    if breakdown:
        print("Reasoning:")
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


def cmd_rerank(manager: WorkflowManager, args) -> int:
    """Re-evaluate ranking for open issues."""
    from ..tasks.task_manager import TaskManager

    tm = TaskManager(manager.github_token, manager.owner, manager.repo)
    tasks = tm.list_tasks()
    if not tasks:
        print("No tasks found")
        return 0
    for issue in tasks:
        score = tm.ranking.score_issue(issue)
        print(f"#{issue['number']}: {issue['title']} score={score}")
    return 0


def cmd_assign(manager: WorkflowManager, args) -> int:
    """Assign an issue to a user."""
    if manager.issue_manager.assign_issue(args.issue, [args.to]):
        print(f"\N{CHECK MARK} Assigned #{args.issue} to {args.to}")
        return 0
    print("Error: failed to assign issue")
    return 1


def cmd_breakdown(manager: WorkflowManager, args) -> int:
    """Break down an issue using the Planning workflow."""
    from ..core.platform import AutonomyPlatform
    from ..planning.workflow import PlanningWorkflow

    issue = manager.issue_manager.get_issue(args.issue) or {}
    issue.setdefault("repository", "default")
    platform = AutonomyPlatform(
        github_token=manager.github_token,
        owner=manager.owner,
        repo=manager.repo,
    )
    wf = platform.create_workflow(PlanningWorkflow)
    state = wf.decompose(issue)
    for t in state.get("tasks", []):
        print(f"- {t}")
    return 0


def cmd_memory(manager: WorkflowManager, args) -> int:
    """Display learned patterns."""
    from ..core.platform import AutonomyPlatform

    platform = AutonomyPlatform(
        github_token=manager.github_token,
        owner=manager.owner,
        repo=manager.repo,
    )
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


def cmd_doctor_nightly(manager: WorkflowManager, vault: SecretVault, args) -> int:
    """Schedule nightly backlog doctor runs."""
    from ..github.issue_manager import IssueManager
    from ..slack import SlackBot
    from ..slack.notifications import NotificationScheduler
    from ..tasks.backlog_doctor import BacklogDoctor

    slack_token = args.slack_token or vault.get_secret("slack_token")
    if not slack_token:
        print("Error: Slack token not found")
        return 1

    scheduler = NotificationScheduler(SlackBot(slack_token))
    repos = args.repos or [f"{manager.owner}/{manager.repo}"]

    for repo in repos:
        owner, name = repo.split("/")
        mgr = IssueManager(manager.github_token, owner, name)
        doctor = BacklogDoctor(mgr, scheduler.slack_client)

        scheduler.schedule_daily(
            name=repo,
            time=args.time,
            func=lambda ch=args.channel, d=doctor: d.run_nightly_diagnosis(channel=ch),
            channel=args.channel,
        )

    scheduler.run_scheduler(block=args.forever)
    return 0


def cmd_metrics_daily(manager: WorkflowManager, vault: SecretVault, args) -> int:
    """Schedule daily metrics reporting."""
    from ..tasks.metrics_service import DailyMetricsService

    slack_token = args.slack_token or vault.get_secret("slack_token")
    if not slack_token:
        print("Error: Slack token not found")
        return 1

    repos = args.repos or [f"{manager.owner}/{manager.repo}"]
    service = DailyMetricsService(
        {repo: args.channel for repo in repos},
        manager.github_token,
        slack_token,
        run_time=args.time,
        storage_path=Path(manager.workspace_path) / "metrics",
        log_path=Path(manager.workspace_path) / "audit.log",
    )
    service.run(forever=args.forever)
    return 0


@handle_errors
def cmd_metrics_export(manager: WorkflowManager, args) -> int:
    """Export stored metrics in Prometheus text format."""
    from ..metrics.storage import MetricsStorage

    storage = MetricsStorage(Path(manager.workspace_path))
    output = storage.export_prometheus()
    print(output)
    return 0


@handle_errors
def cmd_board_init(manager: WorkflowManager, args) -> int:
    """Initialize project board fields."""
    from ..github.board_manager import BoardManager

    _ensure_imports()

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
    bm.init_board()
    print("✓ Board initialized")
    return 0


@handle_errors
def cmd_board_rank(manager: WorkflowManager, args) -> int:
    """Show ranked project board items."""
    _ensure_imports()
    from ..github.board_manager import BoardManager

    bm = BoardManager(
        manager.github_token,
        manager.owner,
        manager.repo,
        cache_path=Path(manager.config.board_cache_path).expanduser(),
    )
    items = bm.rank_items()
    if getattr(args, "json", False):
        import json

        Console().print(json.dumps(items, indent=2, default=str))
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Issue")
        table.add_column("Title")
        table.add_column("Priority")
        for itm in items:
            table.add_row(
                f"#{itm.get('number')}", itm.get("title", ""), str(itm.get("priority"))
            )
        Console().print(table)
    return 0


@handle_errors
def cmd_board_reorder(manager: WorkflowManager, args) -> int:
    """Reorder board items by ranking."""
    _ensure_imports()
    from ..github.board_manager import BoardManager

    bm = BoardManager(
        manager.github_token,
        manager.owner,
        manager.repo,
        cache_path=Path(manager.config.board_cache_path).expanduser(),
    )
    bm.reorder_items()
    print("✓ Board reordered")
    return 0


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
    _ensure_imports()
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


def cmd_completion(parser: argparse.ArgumentParser, args) -> int:
    """Output shell completion script."""
    shell = args.shell
    print(f'eval "$(register-python-argcomplete --shell {shell} autonomy)"')
    return 0


def cmd_interactive(manager: WorkflowManager, parser: argparse.ArgumentParser) -> int:
    """Simple interactive shell for CLI commands."""
    _ensure_imports()
    console = Console()
    vault = SecretVault()
    console.print(
        "[bold green]Autonomy Interactive Shell[/bold green] (type 'quit' to exit)"
    )
    while True:
        try:
            line = input("autonomy> ")
        except EOFError:
            break
        if not line:
            continue
        if line.strip() in {"quit", "exit"}:
            break
        try:
            sub_args = parser.parse_args(shlex.split(line))
            _dispatch_command(manager, vault, parser, sub_args)
        except SystemExit:
            console.print("[red]Invalid command[/red]")
    return 0


def cmd_configure(args) -> int:
    """Write a default configuration file."""
    _ensure_imports()
    path = Path.home() / ".autonomy" / "config.yml"
    cfg = WorkflowConfig.load_default()
    try:
        cfg.save_yaml(path)
        print(f"\N{CHECK MARK} Config written to {path}")
        return 0
    except Exception as e:
        print(f"Error writing config: {e}")
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
