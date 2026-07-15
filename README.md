# obsidian-brain

**Connect any LLM to your Obsidian vault — with Karpathy LLM-wiki structure check.**

> A pattern for personal knowledge bases: sources stay raw, the wiki grows, the LLM does the maintenance.

Inspired by [Andrej Karpathy's LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

---

## What it does

After installing, obsidian-brain will:

1. **Connect** to your local Obsidian vault
2. **Audit** whether it follows the Karpathy LLM-wiki structure
3. **Suggest** what to add or change (without modifying your data)
4. Provide a **CLI** for agents to read/write/audit

```
$ obrain init
$ obrain audit

============================================================
  obsidian-brain  /  Karpathy LLM-wiki Audit
============================================================

Status: NEEDS WORK
Score:  45 / 100
...
```

---

## Install

### One-line install (Windows)
```powershell
irm https://raw.githubusercontent.com/sean0407/obsidian-brain/main/install.ps1 | iex
```

### One-line install (macOS/Linux)
```bash
curl -fsSL https://raw.githubusercontent.com/sean0407/obsidian-brain/main/install.sh | bash
```

### Manual
```bash
git clone https://github.com/sean0407/obsidian-brain.git
cd obsidian-brain
pip install python-frontmatter pyyaml
```

---

## Quick Start

### 1. Configure your vault path

Edit `config.yaml`:
```yaml
vault_path: "C:/Users/Sean/OneDrive/_Obsidian"
```

### 2. Initialize the wiki structure

```bash
python cli.py init
```

This creates:
```
your-vault/
├── sources/           # Raw materials (immutable)
├── wiki/
│   ├── concepts/      # Abstract ideas
│   ├── entities/      # People, orgs, things
│   └── summaries/     # Source summaries
├── queries/           # Saved Q&A
├── CLAUDE.md          # Schema (read by your LLM)
├── index.md           # Content catalog
└── log.md             # Operation log
```

### 3. Audit compliance

```bash
python cli.py audit
```

### 4. Use from any agent

```python
from obsidian_brain import Brain

brain = Brain()
brain.push(
    agent="researcher",
    title="AI Trends 2025",
    content="## Findings\n\n...",
    tags=["AI", "trends"]
)
```

---

## CLI

| Command | Description |
|---------|-------------|
| `obrain init` | Create Karpathy wiki structure |
| `obrain audit` | Check structure compliance |
| `obrain push` | Push a note to the vault |
| `obrain search "query"` | Full-text search |
| `obrain recent` | Show recent notes |

---

## The Karpathy Pattern

This project follows the [LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):

- **Three layers:** `sources/` (raw) → `wiki/` (LLM-maintained) → `schema`
- **Sources are immutable** — LLM reads but never writes
- **Wiki is a persistent, compounding artifact** — knowledge accumulates
- **`CLAUDE.md` is the schema** — tells the LLM how to operate on the wiki
- **`index.md` is the catalog** — what every page is and where it lives
- **`log.md` is the timeline** — what happened and when

---

## Integration with AI Agents

Any LLM agent (Claude Code, Codex, OpenCode, Cursor) can:

1. Clone this repo and run `obrain init`
2. Read the `CLAUDE.md` it generates
3. Follow the Ingest / Query / Lint workflow
4. Run `obrain audit` periodically to check structure

The LLM is the programmer. The wiki is the codebase. obsidian-brain is the linter.

---

## License

MIT
