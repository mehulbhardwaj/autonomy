import subprocess
import sys

from src.verify import verify_installation


def test_verify_installation():
    assert verify_installation() is True


def test_cli_help_runs():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "autonomy.cli.main",
            "--help",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0
