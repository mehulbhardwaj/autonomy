from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests


class SlackBot:
    """Minimal Slack Web API wrapper for posting messages."""

    def __init__(self, token: str) -> None:
        self.token = token
        self.base_url = "https://slack.com/api"

    def post_message(
        self, channel: str, text: str, blocks: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Post a message to Slack and return success status."""
        payload: Dict[str, Any] = {"channel": channel, "text": text}
        if blocks is not None:
            payload["blocks"] = blocks
        response = requests.post(
            f"{self.base_url}/chat.postMessage",
            json=payload,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=10,
        )
        data = response.json()
        return response.status_code == 200 and data.get("ok", False)
