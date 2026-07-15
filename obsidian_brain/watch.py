"""
Watch module for obsidian-brain.
Monitors the vault for changes and auto-commits to git.
Can run as a background daemon.
"""

import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional


class VaultWatcher:
    """
    Watches the vault directory and auto-commits changes.
    Designed to run as a background process.
    """

    def __init__(self, vault_path: str, debounce_seconds: int = 5):
        self.vault = Path(vault_path)
        self.debounce = debounce_seconds
        self.last_change: Optional[float] = None
        self.running = False

    def start(self, push: bool = True):
        """Start watching the vault."""
        self.running = True
        print(f"[{datetime.now():%H:%M:%S}] Watching vault: {self.vault}")
        print(f"[{datetime.now():%H:%M:%S}] Debounce: {self.debounce}s, Push: {push}")
        print(f"[{datetime.now():%H:%M:%S}] Press Ctrl+C to stop")

        try:
            while self.running:
                changed = self._has_changes()

                if changed and self.last_change is None:
                    self.last_change = time.time()
                    print(f"[{datetime.now():%H:%M:%S}] Change detected, waiting for debounce...")

                if self.last_change and (time.time() - self.last_change) >= self.debounce:
                    self._commit_and_push(push)
                    self.last_change = None

                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now():%H:%M:%S}] Stopped")
            self.running = False

    def _has_changes(self) -> bool:
        """Check if there are uncommitted git changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.vault),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return bool(result.stdout.strip())
        except Exception:
            return False

    def _commit_and_push(self, push: bool):
        """Commit all changes and optionally push."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # Add all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=str(self.vault),
                capture_output=True,
                timeout=10,
            )

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", f"auto-sync: {timestamp}"],
                cwd=str(self.vault),
                capture_output=True,
                text=True,
                timeout=10,
            )

            if "nothing to commit" in (result.stdout + result.stderr).lower():
                return

            print(f"[{datetime.now():%H:%M:%S}] Committed")

            # Push
            if push:
                push_result = subprocess.run(
                    ["git", "push"],
                    cwd=str(self.vault),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if push_result.returncode == 0:
                    print(f"[{datetime.now():%H:%M:%S}] Pushed to remote")
                else:
                    print(f"[{datetime.now():%H:%M:%S}] Push failed: {push_result.stderr[:100]}")
        except Exception as e:
            print(f"[{datetime.now():%H:%M:%S}] Error: {e}")


def run_watcher(vault_path: str, debounce: int = 5, push: bool = True):
    """Entry point for running the watcher."""
    watcher = VaultWatcher(vault_path, debounce)
    watcher.start(push=push)
