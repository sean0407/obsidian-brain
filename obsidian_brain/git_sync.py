"""
Git sync for obsidian-brain.
Handles auto-commit and push to GitHub.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


class GitSync:
    """
    Handles Git operations for the vault.
    Auto-commits and pushes changes to GitHub.
    """

    def __init__(
        self,
        vault_path: str,
        repo: str = "",
        token: str = "",
        branch: str = "main",
    ):
        self.vault_path = Path(vault_path)
        self.repo = repo
        self.token = token
        self.branch = branch

    def init(self, repo_url: str, force: bool = False) -> bool:
        """
        Initialize git repo in vault folder.
        repo_url: e.g. https://github.com/user/repo.git
        """
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault not found: {self.vault_path}")

        git_dir = self.vault_path / ".git"
        if git_dir.exists() and not force:
            return True  # Already a git repo

        self._run(["git", "init"], cwd=self.vault_path)
        self._run(["git", "checkout", "-b", self.branch], cwd=self.vault_path)

        # Add remote if URL provided
        if repo_url:
            self._run(["git", "remote", "add", "origin", repo_url], cwd=self.vault_path)

        return True

    def commit_and_push(self, message: str, add_all: bool = True) -> bool:
        """
        Commit all changes and push to remote.

        Returns True if successful, False if nothing to commit or error.
        """
        try:
            # Check git is available
            self._run(["git", "status", "--porcelain"], cwd=self.vault_path)
        except FileNotFoundError:
            print("git not found — skipping auto-sync")
            return False

        if add_all:
            self._run(["git", "add", "."], cwd=self.vault_path)

        # Check if there are changes to commit
        status = self._run(["git", "status", "--porcelain"], cwd=self.vault_path)
        if not status.strip():
            return False  # Nothing to commit

        self._run(["git", "config", "user.email", "agent@obsidian-brain"], cwd=self.vault_path)
        self._run(["git", "config", "user.name", "Obsidian Brain Agent"], cwd=self.vault_path)
        self._run(["git", "commit", "-m", message], cwd=self.vault_path)

        # Push
        if self.repo and self.token:
            remote = self._build_remote_url()
            self._run(["git", "remote", "set-url", "origin", remote], cwd=self.vault_path)
            self._run(["git", "push", "-u", "origin", self.branch], cwd=self.vault_path)

        return True

    def _build_remote_url(self) -> str:
        """Build HTTPS remote URL with token."""
        if self.repo.startswith("https://"):
            base = self.repo.rstrip("/")
        else:
            base = f"https://github.com/{self.repo}"

        if self.token:
            return f"https://{self.token}@github.com/{self.repo.lstrip('https://github.com/')}"
        return base

    def _run(self, cmd: list, cwd: Path) -> str:
        """Run a shell command and return output."""
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            shell=False,
        )
        if result.returncode != 0 and "git" in cmd[0]:
            # Non-fatal for most operations
            pass
        return result.stdout + result.stderr
