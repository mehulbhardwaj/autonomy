from __future__ import annotations

import requests


def get_slack_auth_info(token: str) -> dict:
    """Return Slack auth information for the provided token.

    Raises ValueError if the token is invalid.
    """
    response = requests.post(
        "https://slack.com/api/auth.test",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if response.status_code != 200:
        raise ValueError(f"Failed to authenticate: {response.status_code}")
    data = response.json()
    if not data.get("ok"):
        raise ValueError(f"Slack authentication failed: {data.get('error')}")
    return data
