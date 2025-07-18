from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import keyring
except Exception:  # pragma: no cover - keyring may not be installed
    keyring = None  # type: ignore

from ..core.secret_vault import SecretVault


class SecureTokenStorage:
    """OS keychain backed token storage with file fallback."""

    def __init__(
        self, service_name: str = "autonomy-github", vault: SecretVault | None = None
    ) -> None:
        self.service_name = service_name
        self.vault = vault or SecretVault()

    def store_token(self, username: str, token: str) -> None:
        if keyring is not None:
            try:
                keyring.set_password(self.service_name, username, token)
                return
            except Exception:
                pass
        self.vault.set_secret(f"{self.service_name}-{username}", token)

    def get_token(self, username: str) -> Optional[str]:
        if keyring is not None:
            try:
                token = keyring.get_password(self.service_name, username)
                if token:
                    return token
            except Exception:
                pass
        return self.vault.get_secret(f"{self.service_name}-{username}")


import httpx

REQUIRED_SCOPES = {"repo", "read:user", "read:org"}


def validate_token(token: str) -> bool:
    """Return True if token is valid and has required scopes."""
    try:
        resp = httpx.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}"},
            timeout=10,
        )
        if resp.status_code != 200:
            return False
        scopes = set(
            s.strip()
            for s in resp.headers.get("X-OAuth-Scopes", "").split(",")
            if s.strip()
        )
        return REQUIRED_SCOPES.issubset(scopes)
    except Exception:
        return False


from .device_flow import GitHubDeviceFlow


def refresh_token_if_needed(token: str, client_id: str) -> str:
    """Validate token and re-authenticate via device flow if invalid."""
    if validate_token(token):
        return token
    flow = GitHubDeviceFlow(client_id)
    resp = flow.start_flow()
    print(f"Open {resp.verification_uri} and enter code {resp.user_code}")
    return flow.poll_for_token(resp.device_code, resp.interval)
