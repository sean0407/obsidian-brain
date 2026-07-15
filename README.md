# obsidian-brain

**A shared second brain for AI agents.**

Every agent writes to the same Obsidian vault. Future agents plug in with a single line of code.

```python
from obsidian_brain import Brain

brain = Brain(vault_path="./my-vault")
brain.push(
    agent="researcher",
    title="Claude 4 vs GPT-5",
    content="After testing both...",
    tags=["AI", "comparison"]
)
```

## Features

- **Shared vault** — all agents write to the same Obsidian wiki
- **Agent namespaces** — each agent gets its own folder: `researcher/`, `writer/`, `scout/`
- **Auto git sync** — changes auto-commit and push to GitHub
- **Wiki-links** — notes auto-link to each other via `[[bidirectional links]]`
- **Plug-and-play** — new agents need only one import to join

## Install

```bash
pip install obsidian-brain
```

Or clone and use locally:

```bash
git clone https://github.com/YOUR_USER/obsidian-brain.git
cd obsidian-brain
```

## Quick Start

### 1. Configure

Create `config.yaml` in the project root:

```yaml
vault_path: "/path/to/your/Obsidian/Vault"
github_repo: "your-user/obsidian-brain-wiki"
github_token: "ghp_xxxx"          # GitHub Personal Access Token
auto_commit: true
auto_push: true
default_tags: ["agent", "notes"]
```

### 2. Initialize Git (optional)

```bash
python -m obsidian_brain init --repo https://github.com/you/repo.git
```

### 3. Agent Integration

Any agent can now push notes:

```python
from obsidian_brain import Brain

brain = Brain()

# Register this agent
brain.register_agent("researcher", description="Finds trending topics")

# Push a note
brain.push(
    agent="researcher",
    title="Topic: AI Coding Assistants 2025",
    content="# Findings\n\nClaude Code leads in...",
    tags=["trends", "AI"],
    link_to=["Previous Research"]
)
```

## Vault Structure

```
vault/
├── researcher/          # Agent folder
│   ├── index.md        # Auto-generated index
│   └── ai-coding-2025.md
├── writer/             # Another agent
│   └── draft-claude-carousel.md
└── graph.json          # Auto-generated link graph
```

## CLI

```bash
# Push a note from CLI
obrain push --agent scout --title "Hot Topic" --content "..."

# Search vault
obrain search "AI trends"

# Show recent notes
obrain recent --limit 20
```

## Extending

See `plugins/base.py` for the agent plugin spec. Implement `AgentPlugin` to create reusable agent templates.

## License

MIT
