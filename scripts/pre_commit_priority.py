#!/usr/bin/env python
"""Pre-commit helper to show highest priority task."""
import json
import subprocess
import sys


def main() -> int:
    try:
        result = subprocess.run(
            ["autonomy", "next", "--json"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return 0

    if result.returncode == 0 and result.stdout:
        try:
            data = json.loads(result.stdout)
            issue = data.get("number")
            title = data.get("title")
            print(f"Next task #{issue}: {title}")
        except json.JSONDecodeError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
