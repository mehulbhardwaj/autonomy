from __future__ import annotations

import time
from dataclasses import dataclass

import httpx


@dataclass
class DeviceFlowResponse:
    """Response data from device code initiation."""

    device_code: str
    user_code: str
    verification_uri: str
    interval: int = 5


class OAuthError(Exception):
    """Raised when OAuth authentication fails."""


class GitHubDeviceFlow:
    """Simple GitHub Device-Flow OAuth client."""

    def __init__(self, client_id: str) -> None:
        self.client_id = client_id
        self.base_url = "https://github.com/login/device"
        self.api_url = "https://github.com/login/oauth/access_token"

    def start_flow(self) -> DeviceFlowResponse:
        """Start the device authorization flow."""
        response = httpx.post(
            f"{self.base_url}/code",
            data={
                "client_id": self.client_id,
                "scope": "repo read:user read:org write:repo_hook",
            },
            headers={"Accept": "application/json"},
            timeout=10,
        )
        data = response.json()
        if response.status_code != 200:
            raise OAuthError(
                data.get("error_description", "Failed to start device flow")
            )
        return DeviceFlowResponse(
            device_code=data["device_code"],
            user_code=data["user_code"],
            verification_uri=data.get("verification_uri")
            or data.get("verification_uri_complete"),
            interval=data.get("interval", 5),
        )

    def poll_for_token(self, device_code: str, interval: int = 5) -> str:
        """Poll GitHub until an access token is issued."""
        while True:
            response = httpx.post(
                self.api_url,
                data={
                    "client_id": self.client_id,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                headers={"Accept": "application/json"},
                timeout=10,
            )
            data = response.json()
            if "access_token" in data:
                return data["access_token"]
            if data.get("error") in {"authorization_pending", "slow_down"}:
                time.sleep(data.get("interval", interval))
                continue
            raise OAuthError(data.get("error_description", "Authentication failed"))
