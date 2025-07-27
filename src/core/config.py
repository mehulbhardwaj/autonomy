"""
Workflow Configuration

Configuration settings for the Generate-Verify loop workflow.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None


@dataclass
class WorkflowConfig:
    """Configuration for the GitHub workflow manager"""

    # Code quality constraints
    max_file_lines: int = 300
    max_function_lines: int = 40
    max_pr_lines: int = 500

    # Testing requirements
    test_coverage_target: float = 0.75  # 75%
    require_integration_tests: bool = True
    require_unit_tests: bool = True

    # Agent models (can be configured per agent)
    pm_agent_model: str = "gpt-4"
    sde_agent_model: str = "claude-3-sonnet"
    qa_agent_model: str = "gpt-4"

    # Autonomy settings
    autonomy_level: str = "supervised"  # "supervised", "semi-autonomous", "autonomous"
    require_human_approval: bool = True
    auto_merge_on_approval: bool = True

    # Repository settings
    default_branch: str = "main"
    require_branch_protection: bool = True
    require_status_checks: bool = True

    # Documentation requirements
    require_prd: bool = True
    require_tech_doc: bool = True
    require_test_doc: bool = True

    # Workflow timeouts (in minutes)
    pm_agent_timeout: int = 30
    sde_agent_timeout: int = 120
    qa_agent_timeout: int = 60

    # Board configuration
    board_cache_path: str = "~/.autonomy/field_cache.json"

    # Undo configuration
    commit_window: int = 5

    # Hierarchy management
    hierarchy_orphan_threshold: int = 3
    hierarchy_sync_cooldown: int = 60

    # ------------------------------------------------------------------
    @classmethod
    def from_yaml(cls, path: Path) -> "WorkflowConfig":
        """Load configuration from a YAML file."""
        if yaml is None:
            raise RuntimeError("pyyaml not installed")
        data = yaml.safe_load(path.read_text()) or {}
        return cls.from_dict(data)

    def save_yaml(self, path: Path) -> None:
        """Write configuration to YAML file."""
        if yaml is None:
            raise RuntimeError("pyyaml not installed")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(self.to_dict()))

    @classmethod
    def load_default(cls) -> "WorkflowConfig":
        """Load default configuration from ~/.autonomy/config.yml if present."""
        default = Path.home() / ".autonomy" / "config.yml"
        data: Dict[str, Any] = {}
        if default.exists():
            try:
                data = yaml.safe_load(default.read_text()) or {}
            except Exception:
                data = {}
        config = cls.from_dict(data)
        env_window = os.getenv("AUTONOMY_COMMIT_WINDOW")
        if env_window:
            try:
                config.commit_window = int(env_window)
            except ValueError:
                raise ValueError("AUTONOMY_COMMIT_WINDOW must be an integer")
        return config

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "WorkflowConfig":
        """Create config from dictionary"""
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }

    def validate(self) -> bool:
        """Validate configuration settings"""
        if self.max_file_lines <= 0:
            raise ValueError("max_file_lines must be positive")

        if self.max_function_lines <= 0:
            raise ValueError("max_function_lines must be positive")

        if self.max_pr_lines <= 0:
            raise ValueError("max_pr_lines must be positive")

        if not 0 <= self.test_coverage_target <= 1:
            raise ValueError("test_coverage_target must be between 0 and 1")

        if self.autonomy_level not in ["supervised", "semi-autonomous", "autonomous"]:
            raise ValueError(
                "autonomy_level must be one of: supervised, semi-autonomous, autonomous"
            )

        if self.hierarchy_orphan_threshold <= 0:
            raise ValueError("hierarchy_orphan_threshold must be positive")

        if self.hierarchy_sync_cooldown <= 0:
            raise ValueError("hierarchy_sync_cooldown must be positive")

        if self.commit_window <= 0:
            raise ValueError("commit_window must be positive")

        return True
