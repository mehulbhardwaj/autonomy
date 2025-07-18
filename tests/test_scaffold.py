from pathlib import Path

from src.scaffold import create_basic_scaffold


def test_create_basic_scaffold(tmp_path: Path) -> None:
    create_basic_scaffold(tmp_path)
    assert (tmp_path / "src").is_dir()
    assert (tmp_path / "tests").is_dir()
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "src" / "__init__.py").exists()
