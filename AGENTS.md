# AGENTS.md — obsidian-brain

> **For your LLM Agent** (Claude Code, Codex, OpenCode, etc.)
> **Read this first** when working in this project.

## What is obsidian-brain?

A tool to connect any LLM to a local Obsidian vault. It:
1. Audits the vault for [Karpathy LLM-wiki structure](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
2. Initializes the structure if missing
3. Provides hooks for LLM agents to log work to the vault
4. Auto-syncs to GitHub via background watcher

## Project Layout

```
obsidian-brain/
├── obsidian_brain/        # Core library
│   ├── brain.py          # Main Brain class (push, search, audit)
│   ├── vault.py          # Vault I/O operations
│   ├── audit.py          # Karpathy structure compliance check
│   ├── hooks.py          # log_event() for LLM agents
│   ├── watch.py          # Background auto-sync daemon
│   ├── config.py         # YAML config loader
│   ├── git_sync.py       # Git operations
│   └── templates.py      # Note templates
├── templates/            # Vault templates (CLAUDE.md, index.md, log.md)
├── plugins/              # Agent plugin specs
├── examples/             # Usage examples
├── cli.py                # CLI entry point
├── config.yaml           # User config (vault path, GitHub)
├── install.ps1           # Windows installer
├── install.sh            # macOS/Linux installer
├── README.md             # User docs
└── AGENTS.md             # This file (LLM guide)
```

## Setup

1. User must configure `config.yaml` with their vault path:
   ```yaml
   vault_path: "C:/Users/Sean/OneDrive/_Obsidian"
   github_repo: "sean0407/obsidian-brain"
   ```

2. Install Python deps: `pip install python-frontmatter pyyaml`

## Common Tasks for LLM Agents

### Audit a vault
```bash
python cli.py audit
```

### Initialize vault structure (creates CLAUDE.md, index.md, log.md, folders)
```bash
python cli.py init
```

### Log a piece of work to the vault
```bash
python cli.py hook --type note --title "Title" --content "Body" --tags "tag1,tag2"
```

### Types of hooks
- `ingest` — new source added
- `note` — general note
- `summary` — source summary (goes to wiki/summaries/)
- `concept` — concept page (goes to wiki/concepts/)
- `entity` — entity page (goes to wiki/entities/)
- `query` — Q&A pair
- `lint` — health check report

### Start auto-sync daemon
```bash
python cli.py watch
```
Runs in foreground. User should run this in a separate terminal or as a background service.

## Coding Conventions

- Python 3.11+
- Use `pathlib.Path` for file operations
- Functions returning user-facing data return dicts
- New CLI commands go in `cli.py` with `cmd_<name>` functions
- New modules go in `obsidian_brain/`
- Templates go in `templates/`
- Always test with `python cli.py audit` after structural changes

## Don't

- Don't modify `config.yaml` to point at a different vault without user consent
- Don't push to a different GitHub repo without user consent
- Don't delete vault files
- Don't run `git push --force`

## Testing

```bash
# Audit (read-only)
python cli.py audit

# Hook test (writes to vault)
python cli.py hook --type note --title "Agent Test" --content "Testing"
```

## Releasing

1. Update `__version__` in `obsidian_brain/__init__.py`
2. Commit with message `vX.Y.Z: <description>`
3. Push to `master` branch on GitHub
