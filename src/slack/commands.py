from __future__ import annotations

from typing import Dict


class SlashCommandHandler:
    """Basic slash command handler."""

    def __init__(self, task_manager) -> None:
        self.task_manager = task_manager

    def handle_command(self, command: str, args: Dict) -> Dict:
        if command == "/autonomy next":
            return self.handle_next_command(args)
        if command == "/autonomy update":
            return self.handle_update_command(args)
        if command == "/autonomy status":
            return self.handle_status_command(args)
        return self.handle_help_command()

    def handle_next_command(self, args: Dict) -> Dict:
        issue = self.task_manager.get_next_task()
        if not issue:
            return {"text": "No tasks found"}
        return {"text": f"Next task: #{issue['number']} - {issue['title']}"}

    def handle_update_command(self, args: Dict) -> Dict:
        issue = args.get("issue")
        status = args.get("status")
        notes = args.get("notes")
        if self.task_manager.update_task(issue, status=status, notes=notes):
            return {"text": "Issue updated"}
        return {"text": "Failed to update issue"}

    def handle_status_command(self, args: Dict) -> Dict:
        return {"text": "Status command not implemented"}

    def handle_help_command(self) -> Dict:
        return {
            "text": (
                "Available commands: /autonomy next, /autonomy update, /autonomy status"
            )
        }
