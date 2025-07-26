from __future__ import annotations

from typing import Any, Dict, List, Optional

from .mapping import SlackGitHubMapper


class SlashCommandHandler:
    """Handle Slack slash commands."""

    def __init__(
        self, task_manager, mapper: Optional[SlackGitHubMapper] = None
    ) -> None:
        self.task_manager = task_manager
        self.mapper = mapper or SlackGitHubMapper()

    def handle_command(self, command: str, args: Dict) -> Dict:
        if command == "/autonomy next":
            return self.handle_next_command(args)
        if command == "/autonomy update":
            return self.handle_update_command(args)
        if command == "/autonomy status":
            return self.handle_status_command(args)
        if command == "/autonomy undo":
            return self.handle_undo_command(args)
        return self.handle_help_command()

    def handle_next_command(self, args: Dict) -> Dict:
        slack_user = args.get("user_id") or args.get("user")
        github_user = self.mapper.get_github_user(slack_user) if slack_user else None
        issue = self.task_manager.get_next_task(assignee=github_user)
        if not issue:
            return {"text": "No tasks found", "response_type": "ephemeral"}
        blocks = self.format_task_blocks(issue)
        return {
            "text": f"Next task: #{issue['number']}",
            "blocks": blocks,
            "response_type": "ephemeral",
        }

    def handle_update_command(self, args: Dict) -> Dict:
        slack_user = args.get("user_id") or args.get("user")
        issue_str = args.get("text", "").strip() or args.get("issue")
        if not issue_str or not issue_str.isdigit():
            return {
                "text": "Usage: `/autonomy update <issue-number>`",
                "response_type": "ephemeral",
            }
        issue_number = int(issue_str)
        success = self.task_manager.update_task(
            issue_number,
            status="completed",
            notes=f"Updated via Slack by {slack_user}",
        )
        if success:
            return {
                "text": f"\u2705 Issue #{issue_number} updated successfully!",
                "response_type": "in_channel",
            }
        return {
            "text": f"\u274c Failed to update issue #{issue_number}",
            "response_type": "ephemeral",
        }

    def handle_status_command(self, args: Dict) -> Dict:
        slack_user = args.get("user_id") or args.get("user")
        github_user = self.mapper.get_github_user(slack_user) if slack_user else None
        tasks = self.task_manager.list_tasks(assignee=github_user)
        in_progress = len(
            [
                task
                for task in tasks
                if "in-progress"
                in [
                    label if isinstance(label, str) else label.get("name")
                    for label in task.get("labels", [])
                ]
            ]
        )
        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Status for {github_user}*"},
            },
            {
                "type": "fields",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Open Tasks:* {len(tasks)}"},
                    {"type": "mrkdwn", "text": f"*In Progress:* {in_progress}"},
                ],
            },
        ]
        return {
            "text": f"Status for {github_user}",
            "blocks": blocks,
            "response_type": "ephemeral",
        }

    def handle_undo_command(self, args: Dict) -> Dict:
        hash_value = args.get("text", "").strip()
        if not hash_value:
            return {
                "text": "Usage: `/autonomy undo <hash>`",
                "response_type": "ephemeral",
            }

        issue_mgr = getattr(self.task_manager, "issue_manager", None)
        logger = getattr(self.task_manager, "audit_logger", None)
        if not issue_mgr or not logger:
            return {"text": "Undo not supported", "response_type": "ephemeral"}

        from src.audit.undo import UndoManager

        undo = UndoManager(issue_mgr, logger)
        if undo.undo(hash_value):
            return {
                "text": f"\u2705 Undo {hash_value} completed",
                "response_type": "in_channel",
            }
        return {
            "text": f"\u274c Undo {hash_value} failed",
            "response_type": "ephemeral",
        }

    def handle_help_command(self) -> Dict:
        return {
            "text": (
                "Available commands: /autonomy next, /autonomy update, "
                "/autonomy status, /autonomy undo"
            )
        }

    # --------------------- helpers ---------------------
    def format_task_blocks(self, issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        labels = [
            label if isinstance(label, str) else label.get("name")
            for label in issue.get("labels", [])
        ]
        issue_mgr = getattr(self.task_manager, "issue_manager", None)
        owner = issue_mgr.owner if issue_mgr else "owner"
        repo = issue_mgr.repo if issue_mgr else "repo"
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*#{issue['number']}: {issue['title']}*",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Labels: {', '.join(labels)}",
                    }
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View on GitHub"},
                        "url": f"https://github.com/{owner}/{repo}/issues/{issue['number']}",
                    }
                ],
            },
        ]

    def handle_error(self, exc: Exception) -> Dict[str, str]:
        return {"text": f"Error: {exc}", "response_type": "ephemeral"}
