"""
Obsidian Vault operations.
Handles reading, writing, and searching notes in the vault.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import frontmatter


class Vault:
    """
    Interacts with an Obsidian vault.
    Provides methods for reading, writing, and searching notes.
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault not found: {vault_path}")

    def ensure_agent_folder(self, agent: str):
        """Ensure the agent's folder exists."""
        folder = self.vault_path / agent
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def write_note(
        self,
        subfolder: str,
        filename: str,
        content: str,
    ) -> Path:
        """Write a note to the vault."""
        folder = self.vault_path / subfolder
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / filename

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return path

    def read_note(self, relative_path: str) -> tuple:
        """Read a note, returns (metadata, content)."""
        path = self.vault_path / relative_path
        if not path.exists():
            raise FileNotFoundError(f"Note not found: {relative_path}")

        with open(path, "r", encoding="utf-8") as f:
            post = frontmatter.parse(f)

        return post.metadata, post.content

    def search(self, query: str, agent: Optional[str] = None) -> List[dict]:
        """Search notes by content or title."""
        results = []
        search_dir = self.vault_path
        if agent:
            search_dir = self.vault_path / agent

        query_lower = query.lower()
        for md_file in search_dir.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                if query_lower in content:
                    rel = md_file.relative_to(self.vault_path)
                    results.append({
                        "path": str(rel),
                        "file": md_file.name,
                        "folder": str(rel.parent),
                    })
            except Exception:
                continue

        return results

    def get_recent(self, agent: Optional[str] = None, limit: int = 10) -> List[dict]:
        """Get recently modified notes."""
        search_dir = self.vault_path
        if agent:
            search_dir = self.vault_path / agent

        notes = []
        for md_file in sorted(
            search_dir.rglob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]:
            try:
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                notes.append({
                    "path": str(md_file.relative_to(self.vault_path)),
                    "file": md_file.name,
                    "modified": mtime.isoformat(),
                    "folder": str(md_file.parent.name),
                })
            except Exception:
                continue

        return notes

    def update_agent_index(self, agent: str, title: str, note_path: Path, tags: List[str]):
        """Append this note to the agent's index file."""
        index_path = self.vault_path / agent / "index.md"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        entry = f"- [[{title}]] — {now} — {', '.join('#'+t for t in tags)}\n"

        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = f"# {agent} Notes\n\n## All Notes\n\n"

        # Avoid duplicates
        if f"[[{title}]]" not in content:
            content += entry
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(content)

    def build_graph(self) -> dict:
        """Build a graph of notes and wiki-links."""
        graph = {"nodes": [], "links": []}
        nodes_set = set()

        for md_file in self.vault_path.rglob("*.md"):
            rel = str(md_file.relative_to(self.vault_path))
            nodes_set.add(rel)
            graph["nodes"].append({
                "id": rel,
                "name": md_file.stem,
                "folder": md_file.parent.name,
            })

            # Find wiki-links in this note
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                for match in re.finditer(r'\[\[([^\]]+)\]\]', content):
                    target = match.group(1) + ".md"
                    target_path = str(md_file.parent / target)
                    if target_path in nodes_set:
                        graph["links"].append({
                            "source": rel,
                            "target": target_path,
                        })
            except Exception:
                continue

        return graph
