import subprocess
from pathlib import Path


def test_flake8_compliance():
    """Ensure code passes flake8."""
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            "flake8",
            "--max-line-length=120",
            str(root / "src"),
            str(root / "tests"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
