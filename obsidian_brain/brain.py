"""
Core Brain class for obsidian-brain.
Main interface for agents to interact with the shared vault.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from .vault import Vault
from .git_sync import GitSync
from .templates import TemplateEngine


class Brain:
    """
    The shared brain that all agents write to.

    Usage:
        brain = Brain(vault_path="./my-vault")
        brain.push(
            agent="researcher",
            title="AI Trends 2025",
            content="# AI Trends...",
            tags=["AI", "research"]
        )
    """

    def __init__(
        self,
        vault_path: Optional[str] = None,
        github_repo: str = "",
        github_token: str = "",
        auto_sync: bool = True,
        config_path: Optional[str] = None,
    ):
        from .config import Config

        # Load config
        if config_path and Path(config_path).exists():
            self.config = Config.load(config_path)
        else:
            self.config = Config.load()

        # Override with runtime params if provided
        if vault_path:
            self.config.vault_path = vault_path
        if github_repo:
            self.config.github_repo = github_repo
        if github_token:
            self.config.github_token = github_token

        if not self.config.vault_path:
            raise ValueError("vault_path must be set via config or parameter")

        self.vault = Vault(self.config.vault_path)
        self.git = GitSync(
            vault_path=self.config.vault_path,
            repo=self.config.github_repo,
            token=self.config.github_token,
            branch=self.config.git_branch,
        )
        self.templates = TemplateEngine(
            template_dir=self.config.template_dir
        )

        self._agent_registry: dict = {}

    def register_agent(self, name: str, description: str = ""):
        """Register an agent with the brain."""
        self._agent_registry[name] = {
            "description": description,
            "registered_at": datetime.now().isoformat(),
        }
        # Create agent folder in vault
        self.vault.ensure_agent_folder(name)

    def push(
        self,
        agent: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        folder: Optional[str] = None,
        link_to: Optional[List[str]] = None,
        auto_commit: bool = True,
    ) -> str:
        """
        Push content to the vault.

        Args:
            agent: Name of the agent pushing content
            title: Note title (used for filename and H1)
            content: Markdown content
            tags: List of tags (will be added as #tag)
            folder: Subfolder within agent's folder (optional)
            link_to: List of other note titles to link to via [[wiki-link]]
            auto_commit: Whether to auto-commit to git

        Returns:
            Path to the created note
        """
        if tags is None:
            tags = self.config.default_tags

        # Ensure agent folder exists
        self.vault.ensure_agent_folder(agent)

        # Build the full note content
        note = self._build_note(
            agent=agent,
            title=title,
            content=content,
            tags=tags,
            folder=folder,
            link_to=link_to,
        )

        # Generate filename
        filename = self._sanitize_filename(title)
        subfolder = folder or agent
        note_path = self.vault.write_note(
            subfolder=subfolder,
            filename=filename,
            content=note,
        )

        # Update agent index
        self.vault.update_agent_index(agent, title, note_path, tags)

        # Git sync
        if auto_commit and self.config.auto_commit:
            self.git.commit_and_push(
                message=f"[{agent}] Add: {title}"
            )

        return note_path

    def search(self, query: str, agent: Optional[str] = None) -> List[dict]:
        """
        Search the vault for notes matching query.

        Args:
            query: Search term
            agent: Limit to specific agent's notes

        Returns:
            List of matching notes with metadata
        """
        return self.vault.search(query, agent=agent)

    def get_recent(self, agent: Optional[str] = None, limit: int = 10) -> List[dict]:
        """Get recently modified notes."""
        return self.vault.get_recent(agent=agent, limit=limit)

    def build_graph(self) -> dict:
        """
        Build a graph of all notes and their links.
        Useful for Obsidian's graph view.
        """
        return self.vault.build_graph()

    def audit(self):
        """
        Audit the vault for Karpathy LLM-wiki compliance.
        Returns an AuditResult with score, findings, and suggestions.
        """
        from .audit import audit_vault
        return audit_vault(self.config.vault_path)

    def init_wiki_structure(self, force: bool = False) -> List[str]:
        """
        Create the Karpathy LLM-wiki structure in the vault.
        Creates folders and copies template files.

        Returns:
            List of paths created
        """
        from pathlib import Path
        import shutil

        vault = Path(self.config.vault_path)
        template_dir = Path(__file__).parent.parent / "templates"
        created = []

        # Create folders
        folders = ["sources", "wiki", "wiki/concepts", "wiki/entities",
                   "wiki/summaries", "queries"]
        for folder in folders:
            path = vault / folder
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                created.append(str(path))

        # Copy template files (only if not exists, unless force)
        templates = {
            "CLAUDE.md": "CLAUDE.md",
            "index.md": "index.md",
            "log.md": "log.md",
        }
        for src_name, dest_name in templates.items():
            src = template_dir / src_name
            dest = vault / dest_name
            if src.exists() and (not dest.exists() or force):
                shutil.copy(src, dest)
                created.append(str(dest))

        return created

    # ── Private helpers ────────────────────────────────────────────────────────

    def _build_note(
        self,
        agent: str,
        title: str,
        content: str,
        tags: List[str],
        folder: Optional[str],
        link_to: Optional[List[str]],
    ) -> str:
        """Build full markdown note with frontmatter and structure."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        tag_str = " ".join(f"#{t.strip()}" for t in tags)

        tags_list = ", ".join('"' + t.strip() + '"' for t in tags)
        frontmatter = f"""---
created: {now}
agent: {agent}
tags: [{tags_list}]
---

"""

        header = f"# {title}\n\n"
        meta = f"> Agent: **{agent}** · {now} · {tag_str}\n\n"
        links = ""
        if link_to:
            links = "## Links\n\n" + "\n".join(f"- [[{t}]]" for t in link_to) + "\n\n"

        return frontmatter + header + meta + content + "\n\n" + links

    def _sanitize_filename(self, title: str) -> str:
        """Convert title to safe Obsidian filename."""
        # Remove invalid chars
        name = re.sub(r'[<>:"/\\|?*]', "", title)
        name = re.sub(r"\s+", "-", name.strip())
        name = name[:200]  # Truncate long titles
        return f"{name}.md"
