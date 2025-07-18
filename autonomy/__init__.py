"""Autonomy package alias for src."""

import importlib
import sys

from src import *  # noqa: F401,F403

for _pkg in (
    "cli",
    "core",
    "github",
    "planning",
    "scaffold",
    "slack",
    "tasks",
    "templates",
    "verify",
):
    sys.modules[f"autonomy.{_pkg}"] = importlib.import_module(f"src.{_pkg}")
