"""
Base class for obsidian-brain agent plugins.
Extend this to create reusable agent templates.
"""

from abc import ABC, abstractmethod
from typing import Optional, List


class AgentPlugin(ABC):
    """
    Base class for all agent plugins.

    Each plugin has:
    - name: unique identifier
    - description: what this agent does
    - push(): called when the agent wants to write to the vault

    Usage:
        class MyAgent(AgentPlugin):
            name = "my-agent"
            description = "Does something useful"

            def push(self, brain, **kwargs):
                brain.push(agent=self.name, **kwargs)

        agent = MyAgent()
        agent.push(brain, title="...", content="...")
    """

    name: str = "agent"
    description: str = ""

    @abstractmethod
    def push(self, brain, **kwargs):
        """Push content to the vault via the shared brain."""
        pass

    def on_register(self, brain):
        """Called when the agent registers with the brain."""
        brain.register_agent(self.name, self.description)

    def search(self, brain, query: str) -> List[dict]:
        """Search the vault for relevant notes."""
        return brain.search(query, agent=self.name)

    def get_context(self, brain, limit: int = 5) -> str:
        """Get recent notes from this agent as markdown context."""
        recent = brain.get_recent(agent=self.name, limit=limit)
        lines = [f"## Recent notes from {self.name}\n"]
        for note in recent:
            lines.append(f"- [[{note['file'].replace('.md', '')}]]")
        return "\n".join(lines)


# ── Example: Scout Agent Plugin ────────────────────────────────────────────────

class ScoutPlugin(AgentPlugin):
    """Finds and reports trending topics."""

    name = "scout"
    description = "Scouts trending topics and saves research findings"

    def push(self, brain, title: str, content: str, tags: Optional[List[str]] = None, **kwargs):
        if tags is None:
            tags = ["trends", "scout"]
        brain.push(
            agent=self.name,
            title=title,
            content=content,
            tags=tags,
            **kwargs,
        )


# ── Example: Writer Agent Plugin ──────────────────────────────────────────────

class WriterPlugin(AgentPlugin):
    """Writes content based on research."""

    name = "writer"
    description = "Writes content based on research from the vault"

    def push(self, brain, title: str, content: str, tags: Optional[List[str]] = None, **kwargs):
        if tags is None:
            tags = ["content", "writer"]

        # Auto-link to related scout notes
        related = brain.search(title.split()[0], agent="scout")
        link_to = [r["file"].replace(".md", "") for r in related[:3]]

        brain.push(
            agent=self.name,
            title=title,
            content=content,
            tags=tags,
            link_to=link_to,
            **kwargs,
        )
