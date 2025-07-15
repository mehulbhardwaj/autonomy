from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet


class SecretVault:
    """Simple file-based secret vault with Fernet encryption."""

    def __init__(
        self, vault_path: Optional[Path] = None, key_path: Optional[Path] = None
    ) -> None:
        self.vault_path = vault_path or Path(
            os.getenv("AUTONOMY_VAULT_PATH", Path.home() / ".autonomy" / "vault.json")
        )
        self.key_path = key_path or Path(
            os.getenv("AUTONOMY_KEY_PATH", Path.home() / ".autonomy" / "vault.key")
        )
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        self._fernet = Fernet(self._load_or_create_key())

    def _load_or_create_key(self) -> bytes:
        if self.key_path.exists():
            return self.key_path.read_bytes()
        key = Fernet.generate_key()
        self.key_path.write_bytes(key)
        return key

    def _load_vault(self) -> dict:
        if self.vault_path.exists():
            with open(self.vault_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_vault(self, data: dict) -> None:
        with open(self.vault_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def set_secret(self, name: str, value: str) -> None:
        data = self._load_vault()
        token = self._fernet.encrypt(value.encode()).decode()
        data[name] = token
        self._save_vault(data)

    def get_secret(self, name: str) -> Optional[str]:
        env_value = os.getenv(name.upper())
        if env_value is not None:
            return env_value
        data = self._load_vault()
        token = data.get(name)
        if token is None:
            return None
        return self._fernet.decrypt(token.encode()).decode()

    def delete_secret(self, name: str) -> None:
        data = self._load_vault()
        if name in data:
            del data[name]
            self._save_vault(data)
