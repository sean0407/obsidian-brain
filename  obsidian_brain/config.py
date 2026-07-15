"""
Config loader for obsidian-brain.
Loads settings from config.yaml in the project root.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Configuration for obsidian-brain."""

    # Vault settings
    vault_path: str = ""

    # Git settings
    github_repo: str = ""
    github_token: str = ""
    git_branch: str = "main"
    auto_commit: bool = True
    auto_push: bool = True

    # Agent settings
    default_agent: str = "agent"
    default_tags: list = field(default_factory=list)

    # Template settings
    use_templates: bool = True
    template_dir: str = "templates"

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load config from YAML file."""
        if config_path is None:
            config_path = os.environ.get(
                "OBSIDIAN_BRAIN_CONFIG",
                str(Path(__file__).parent.parent / "config.yaml")
            )

        if not Path(config_path).exists():
            return cls()

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def save(self, config_path: Optional[str] = None):
        """Save config to YAML file."""
        if config_path is None:
            config_path = os.environ.get(
                "OBSIDIAN_BRAIN_CONFIG",
                str(Path(__file__).parent.parent / "config.yaml")
            )

        data = {
            "vault_path": self.vault_path,
            "github_repo": self.github_repo,
            "github_token": self.github_token,
            "git_branch": self.git_branch,
            "auto_commit": self.auto_commit,
            "auto_push": self.auto_push,
            "default_agent": self.default_agent,
            "default_tags": self.default_tags,
            "use_templates": self.use_templates,
            "template_dir": self.template_dir,
        }

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
