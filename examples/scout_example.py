"""Example: how to integrate with an existing Mavis agent."""

import sys
from pathlib import Path

# Add obsidian-brain to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_brain import Brain
from obsidian_brain.plugins.base import ScoutPlugin


def main():
    # Connect to the shared brain
    brain = Brain()

    # Register our agent
    scout = ScoutPlugin()
    scout.on_register(brain)

    # Push a research note
    scout.push(
        brain,
        title="Topic: AI Agents in 2025",
        content="""# Research Notes

## Key Trends
- Agentic AI is the dominant theme this year
- Memory and context windows are expanding rapidly
- Multi-agent systems are becoming production-ready

## Sources
- Anthropic blog, OpenAI announcements, GitHub trending
""",
        tags=["AI", "agents", "2025"],
        link_to=["Claude Context Windows"],
    )

    print("Scout pushed research to vault ✅")


if __name__ == "__main__":
    main()
