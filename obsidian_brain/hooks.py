"""
Hook system for obsidian-brain.
Provides a simple interface for any LLM/agent to record progress
to the vault automatically.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List


HOOK_TYPES = [
    "ingest",   # Adding a new source
    "query",    # Asking a question
    "lint",     # Health check
    "note",     # General note
    "summary",  # Source summary
    "concept",  # New concept page
    "entity",   # New entity page
]


def log_event(
    vault_path: str,
    event_type: str,
    title: str,
    content: str = "",
    tags: Optional[List[str]] = None,
    source: Optional[str] = None,
    links: Optional[List[str]] = None,
):
    """
    Log an event to the vault's log.md and create a wiki page.

    This is the single function any LLM agent should call to record work.

    Args:
        vault_path: Path to the Obsidian vault
        event_type: One of HOOK_TYPES (ingest, query, lint, note, etc.)
        title: Short title of the event
        content: Full markdown content (optional)
        tags: List of tags
        source: Source URL or path (for ingest events)
        links: List of [[wiki-links]] to other pages
    """
    vault = Path(vault_path)
    if not vault.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_entry_id = datetime.now().strftime("%H%M%S")

    if tags is None:
        tags = []
    if links is None:
        links = []

    # 1. Append to log.md
    _append_to_log(vault, log_date, event_type, title, source)

    # 2. Create wiki page if event is content-bearing
    if event_type in ("note", "summary", "concept", "entity") and content:
        _create_wiki_page(vault, event_type, title, content, tags, links, source, timestamp)

    return f"[{timestamp}] {event_type}: {title}"


def _append_to_log(vault: Path, date: str, event_type: str, title: str, source: Optional[str]):
    """Append an entry to log.md in the Karpathy-parseable format."""
    log_path = vault / "log.md"
    if not log_path.exists():
        log_path.write_text("# log.md — Operation Log\n\n", encoding="utf-8")

    entry = f"## [{date}] {event_type} | {title}\n"
    if source:
        entry += f"- source: {source}\n"
    entry += "\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


def _create_wiki_page(
    vault: Path,
    event_type: str,
    title: str,
    content: str,
    tags: List[str],
    links: List[str],
    source: Optional[str],
    timestamp: str,
):
    """Create a wiki page in the appropriate subfolder."""
    # Map event types to folders
    folder_map = {
        "summary": "wiki/summaries",
        "concept": "wiki/concepts",
        "entity": "wiki/entities",
        "note": "wiki",
        "ingest": "wiki/summaries",
    }
    folder = vault / folder_map.get(event_type, "wiki")
    folder.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in title.lower())
    safe_name = safe_name.strip("-")[:100]
    page_path = folder / f"{safe_name}.md"

    # Build frontmatter
    tags_str = ", ".join('"' + t + '"' for t in tags)
    frontmatter_lines = [
        "---",
        f"created: {timestamp}",
        f"type: {event_type}",
        f"tags: [{tags_str}]",
    ]
    if source:
        frontmatter_lines.append(f"source: {source}")
    frontmatter_lines.append("---\n")

    # Build full page
    page = "\n".join(frontmatter_lines)
    page += f"# {title}\n\n"
    if links:
        page += "## Related\n"
        for link in links:
            page += f"- [[{link}]]\n"
        page += "\n"
    page += content
    page += "\n"

    # Don't overwrite existing
    if not page_path.exists():
        page_path.write_text(page, encoding="utf-8")

    # Update index.md
    _update_index(vault, title, page_path, event_type, tags)


def _update_index(vault: Path, title: str, page_path: Path, event_type: str, tags: List[str]):
    """Add the new page to index.md."""
    index_path = vault / "index.md"
    if not index_path.exists():
        return

    rel_path = page_path.relative_to(vault)
    tag_str = " ".join("#" + t for t in tags)

    entry = f"- [[{title}]] ({event_type}) {tag_str}\n"

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Insert before the "Recent Activity" section
    if "Recent Activity" in content:
        parts = content.split("## Recent Activity")
        if title not in parts[0]:
            parts[0] += f"\n{entry}"
            content = "## Recent Activity".join(parts)
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(content)


# ── Convenience wrappers ──────────────────────────────────────────────────────

def ingest(vault_path: str, source: str, summary: str, title: Optional[str] = None):
    """Record a new source ingestion."""
    if title is None:
        title = Path(source).stem if "/" in source else source[:50]
    return log_event(
        vault_path=vault_path,
        event_type="ingest",
        title=title,
        content=summary,
        source=source,
    )


def note(vault_path: str, title: str, content: str, tags: Optional[List[str]] = None):
    """Add a general note to the wiki."""
    return log_event(
        vault_path=vault_path,
        event_type="note",
        title=title,
        content=content,
        tags=tags or [],
    )


def query(vault_path: str, question: str, answer: str):
    """Record a Q&A pair."""
    title = question[:80]
    content = f"## Question\n\n{question}\n\n## Answer\n\n{answer}"
    return log_event(
        vault_path=vault_path,
        event_type="query",
        title=title,
        content=content,
        tags=["query"],
    )
