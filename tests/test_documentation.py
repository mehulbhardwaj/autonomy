import subprocess
import sys
from pathlib import Path

DOCS = [
    "docs/USER_GUIDE.md",
    "docs/INSTALLATION.md",
    "docs/CONFIGURATION.md",
    "docs/SELF_HOSTING.md",
    "docs/ENTERPRISE.md",
    "docs/API.md",
    "docs/ARCHITECTURE.md",
    "docs/OPERATIONS.md",
]


def test_docs_exist():
    for doc in DOCS:
        assert Path(doc).exists(), f"missing {doc}"


def test_generate_docs_script(tmp_path: Path):
    output = tmp_path / "api.md"
    result = subprocess.run(
        [sys.executable, "scripts/generate_docs.py", str(output)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert output.exists()
