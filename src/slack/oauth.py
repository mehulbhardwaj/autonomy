from __future__ import annotations

import hashlib
import hmac
from typing import Dict

import requests


class SlackOAuth:
    """Simple Slack OAuth helper."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://slack.com/api"

    def get_install_url(self) -> str:
        """Return the workspace installation URL."""
        scopes = "channels:read,chat:write,commands,im:write,users:read,team:read"
        return (
            "https://slack.com/oauth/v2/authorize?"
            f"client_id={self.client_id}&scope={scopes}"
        )

    def exchange_code(self, code: str) -> Dict:
        """Exchange an OAuth code for an access token."""
        response = requests.post(
            f"{self.base_url}/oauth.v2.access",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
            },
            timeout=10,
        )
        data = response.json()
        if response.status_code != 200:
            raise ValueError(f"Failed to exchange code: {response.status_code}")
        if not data.get("ok"):
            raise ValueError(data.get("error", "unknown_error"))
        return data


def verify_slack_signature(
    timestamp: str, signature: str, body: bytes, signing_secret: str
) -> bool:
    """Verify a Slack request signature."""
    basestring = f"v0:{timestamp}:{body.decode()}"
    computed = hmac.new(
        signing_secret.encode(), basestring.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"v0={computed}", signature)
