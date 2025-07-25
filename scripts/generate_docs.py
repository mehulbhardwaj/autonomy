#!/usr/bin/env python
"""Generate documentation files from the current code base."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def generate_cli_reference() -> str:
    """Return the CLI help text."""
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def generate_api_reference() -> str:
    """Return API documentation extracted from docstrings."""
    # Importing the full CLI can pull in heavy optional dependencies. To keep
    # documentation generation lightweight we simply read the module docstring
    # from ``src/cli/main.py`` without executing it.
    path = Path("src/cli/main.py")
    with path.open() as f:
        first_line = f.readline()
    doc = first_line.strip('\n" ') if first_line.startswith('""') else ""
    return doc


def main(output: str | None = None) -> None:
    output_path = Path(output or "docs/API.md")
    cli_help = generate_cli_reference()
    api_docs = generate_api_reference()
    content = "# Autonomy CLI Reference\n\n" + "```\n" + cli_help + "```\n\n"
    content += "# Python API\n\n" + "```\n" + api_docs + "```\n"
    output_path.write_text(content)
    print(f"Wrote documentation to {output_path}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    main(path)
