from __future__ import annotations

from typing import Iterable, List

import requests

REQUIRED_GITHUB_SCOPES = [
    "repo",
    "read:org",
    "write:repo_hook",
    "read:user",
]


def get_github_token_scopes(token: str) -> List[str]:
    """Return the list of OAuth scopes associated with a GitHub token."""
    response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"},
        timeout=10,
    )
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch token scopes: {response.status_code}")
    scopes = response.headers.get("X-OAuth-Scopes", "")
    return [s.strip() for s in scopes.split(",") if s.strip()]


def validate_github_token_scopes(
    token: str, required: Iterable[str] | None = None
) -> None:
    """Validate that the GitHub token includes the required scopes."""
    required_scopes = list(required) if required is not None else REQUIRED_GITHUB_SCOPES
    scopes = get_github_token_scopes(token)
    missing = [s for s in required_scopes if s not in scopes]
    if missing:
        raise ValueError(f"Token missing scopes: {', '.join(missing)}")
