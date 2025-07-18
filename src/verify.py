"""Installation verification utilities."""

from importlib import import_module


def verify_installation() -> bool:
    """Verify package installation and basic functionality."""
    try:
        import autonomy

        # Basic imports that should succeed for a functional install
        import_module("autonomy.cli.main")
        import_module("autonomy.core.config")
        print(f"\u2705 Autonomy {autonomy.__version__} installed successfully")
        print("\u2705 Core modules imported successfully")
        return True
    except Exception as exc:
        print(f"\u274c Installation verification failed: {exc}")
        return False
