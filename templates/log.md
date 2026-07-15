# log.md — Operation Log

> Append-only record of what happened and when.

Format: `## [YYYY-MM-DD] <operation> | <title>`

This format is parseable with simple unix tools:
```bash
grep "^## \[" log.md | tail -5   # last 5 entries
```

---

## [INIT] System Initialized

- Vault structure created following Karpathy LLM-wiki pattern
- Folders: `sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/summaries/`, `queries/`
- Files: `CLAUDE.md`, `index.md`, `log.md`
- Tool: obsidian-brain
