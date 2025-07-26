"""Project scaffolding utilities."""

from pathlib import Path


def create_basic_scaffold(workspace_path: Path) -> None:
    """Create a minimal project scaffold with src and tests folders.

    Args:
        workspace_path: Path to the new project directory
    """
    (workspace_path / "src").mkdir(parents=True, exist_ok=True)
    (workspace_path / "tests").mkdir(parents=True, exist_ok=True)

    readme = workspace_path / "README.md"
    if not readme.exists():
        readme.write_text(f"# {workspace_path.name}\n")

    init_file = workspace_path / "src" / "__init__.py"
    if not init_file.exists():
        init_file.write_text("__version__ = '0.1.0'\n")
