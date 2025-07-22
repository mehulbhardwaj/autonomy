from __future__ import annotations

from typing import Any, Dict, List

from src.slack.bot import SlackBot


class SlackTools:
    """Simple Slack tool wrapper."""

    def __init__(self, bot: SlackBot) -> None:
        self.bot = bot

    def post_message(
        self, channel: str, text: str, blocks: List[Dict[str, Any]] | None = None
    ) -> bool:
        return self.bot.post_message(channel=channel, text=text, blocks=blocks)
