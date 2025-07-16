import subprocess
from pathlib import Path


def test_isort_formatting():
    """Ensure imports are properly sorted with isort."""
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["isort", "--check-only", str(root / "src"), str(root / "tests")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
