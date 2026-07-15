# CLAUDE.md — Wiki Schema and Operations

> **For your LLM Agent** (Claude Code, Codex, OpenCode, etc.)
> **Read this file before doing any work on the wiki.**

This file tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow. It is the most important file in the vault — without it, the LLM is just a generic chatbot instead of a disciplined wiki maintainer.

## Wiki Architecture (Karpathy LLM-wiki pattern)

This vault follows the [LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). There are three layers:

### 1. Raw sources (`sources/`)
**Immutable.** Your curated collection of source documents — articles, papers, images, data files. The LLM reads from them but **never modifies them**. This is your source of truth.

### 2. The wiki (`wiki/`)
**LLM-owned.** A directory of generated markdown files — summaries, entity pages, concept pages, comparisons. The LLM creates pages, updates them when new sources arrive, maintains cross-references, and keeps everything consistent. You read it; the LLM writes it.

```
wiki/
├── concepts/   # Pages for abstract ideas, themes, frameworks
├── entities/   # Pages for people, organizations, specific things
└── summaries/  # One-page summaries of individual sources
```

### 3. The schema (this file)
You and the LLM co-evolve this file over time as you figure out what works for your domain.

## Core Files

| File | Purpose |
|------|---------|
| `index.md` | Content catalog — every page listed with one-line summary |
| `log.md` | Chronological log — record of every operation |
| `CLAUDE.md` | This file — schema and operations |
| `queries/` | Q&A records and analyses worth saving |

## Operations

### Ingest
When a new source arrives in `sources/`:
1. Read the source, discuss key takeaways with the user
2. Write a summary page in `wiki/summaries/`
3. Update `index.md` with the new page
4. Update relevant `wiki/concepts/` and `wiki/entities/` pages
5. Append an entry to `log.md` with format `## [YYYY-MM-DD] ingest | <title>`
6. A single source may touch 10-15 wiki pages — that's normal

### Query
When the user asks a question:
1. Read `index.md` to find relevant pages
2. Read those pages, synthesize an answer with citations
3. If the answer is valuable, file it as a new page in `wiki/` or `queries/`

### Lint
Periodically health-check the wiki:
- Look for contradictions between pages
- Find stale claims newer sources have superseded
- Identify orphan pages with no inbound links
- Spot important concepts mentioned but lacking their own page
- Flag missing cross-references and data gaps

## Conventions

- **Naming:** `wiki/concepts/<topic>.md`, `wiki/entities/<name>.md`
- **Frontmatter:** Every wiki page should have YAML frontmatter (tags, source, date)
- **Links:** Use `[[wiki-links]]` for Obsidian bidirectional linking
- **Citations:** Always cite `sources/<filename>.md#section` for facts
- **Never edit `sources/`** — it is immutable

## Tools

- `obrain` CLI — search, push, audit the vault
- `obrain audit` — check Karpathy LLM-wiki compliance
- `obrain search "<query>"` — full-text search across the wiki
- `obrain push --agent <name> --title ... --content ...` — write a new page

---

*This file is your wiki's operating manual. Update it as your workflow evolves.*
