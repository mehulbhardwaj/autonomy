import subprocess
from pathlib import Path


def test_black_formatting():
    """Ensure code is formatted with black."""
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["black", "--check", str(root / "src"), str(root / "tests")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
