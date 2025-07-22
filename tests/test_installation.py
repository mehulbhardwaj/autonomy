import subprocess
import sys


def test_cli_help_runs():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "--help",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0
