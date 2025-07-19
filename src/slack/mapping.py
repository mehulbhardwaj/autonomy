from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from ..core.secret_vault import SecretVault


class SlackGitHubMapper:
    """Map Slack users to GitHub usernames using a local JSON file."""

    def __init__(self, vault: SecretVault | None = None) -> None:
        self.vault = vault or SecretVault()
        self.mapping_file = Path.home() / ".autonomy" / "slack_github_mapping.json"

    def load_mappings(self) -> Dict[str, str]:
        if self.mapping_file.exists():
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_mappings(self, data: Dict[str, str]) -> None:
        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.mapping_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def get_github_user(self, slack_user: str) -> str:
        mappings = self.load_mappings()
        return mappings.get(slack_user, slack_user)

    def set_mapping(self, slack_user: str, github_user: str) -> None:
        mappings = self.load_mappings()
        mappings[slack_user] = github_user
        self.save_mappings(mappings)
