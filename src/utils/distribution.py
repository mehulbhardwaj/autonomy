import importlib

import httpx
from packaging import version

from .. import __version__


def verify_installation() -> bool:
    """Verify package installation and basic imports."""
    try:
        importlib.import_module("src.cli.main")
        importlib.import_module("src.core.config")
        return True
    except Exception:
        return False


def check_for_updates() -> None:
    """Check PyPI for newer versions and print upgrade hint."""
    try:
        resp = httpx.get("https://pypi.org/pypi/autonomy/json", timeout=5)
        resp.raise_for_status()
        latest = resp.json()["info"]["version"]
        if version.parse(latest) > version.parse(__version__):
            print(f"\U0001f4e6 Update available: {__version__} → {latest}")
            print("Run: pipx upgrade autonomy")
    except Exception:
        # Fail silently on network or parsing errors
        pass
