from pathlib import Path

import yaml


def test_release_scripts_exist():
    for name in ["bump-version.sh", "release-notes.sh", "test-installation.sh"]:
        path = Path("scripts") / name
        assert path.exists(), f"missing {name}"
        assert path.stat().st_mode & 0o111, f"{name} not executable"


def test_release_workflow_matrix():
    with open(".github/workflows/release.yml") as f:
        data = yaml.safe_load(f)
    on_field = data.get("on") or data.get(True)
    assert "workflow_dispatch" in on_field
    matrix = data["jobs"]["test-installation"]["strategy"]["matrix"]
    assert set(matrix["os"]) == {"ubuntu-latest", "macos-latest", "windows-latest"}
    assert matrix["python-version"] == ["3.8", "3.9", "3.10", "3.11", "3.12"]
