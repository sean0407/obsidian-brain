#!/usr/bin/env python3
"""
obsidian-brain CLI
Usage:
    obrain init                    Create Karpathy wiki structure
    obrain audit                   Check vault compliance
    obrain push --agent NAME --title TITLE --content "..."
    obrain search QUERY
    obrain recent [--limit N]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from obsidian_brain import Brain


def cmd_init(args):
    """Initialize Karpathy wiki structure in vault."""
    brain = Brain()
    created = brain.init_wiki_structure(force=args.force)
    if created:
        print(f"Created {len(created)} paths:")
        for p in created:
            print(f"  + {p}")
    else:
        print("Vault already initialized. Use --force to overwrite templates.")
    print()
    print("Running audit...")
    print()
    cmd_audit(args)


def cmd_audit(args):
    """Audit vault for Karpathy compliance."""
    brain = Brain()
    result = brain.audit()
    from obsidian_brain.audit import format_report
    print(format_report(result))
    sys.exit(0 if result.passed else 1)


def cmd_push(args):
    brain = Brain()
    path = brain.push(
        agent=args.agent,
        title=args.title,
        content=args.content,
        tags=args.tags.split(",") if args.tags else [],
        auto_commit=True,
    )
    print(f"Pushed: {path}")


def cmd_search(args):
    brain = Brain()
    results = brain.search(args.query, agent=args.agent)
    if not results:
        print("No results.")
        return
    for r in results:
        print(f"  [{r['folder']}] {r['file']}")


def cmd_recent(args):
    brain = Brain()
    notes = brain.get_recent(agent=args.agent, limit=args.limit)
    for n in notes:
        print(f"  {n['modified'][:16]} [{n['folder']}] {n['file']}")


def cmd_watch(args):
    """Start auto-sync watcher."""
    from obsidian_brain.watch import run_watcher
    from obsidian_brain.config import Config
    config = Config.load()
    run_watcher(config.vault_path, debounce=args.debounce, push=not args.no_push)


def cmd_hook(args):
    """Record an event (ingest, note, query, etc.)."""
    from obsidian_brain.hooks import log_event
    from obsidian_brain.config import Config
    config = Config.load()

    tags = args.tags.split(",") if args.tags else []
    result = log_event(
        vault_path=config.vault_path,
        event_type=args.type,
        title=args.title,
        content=args.content or "",
        tags=tags,
        source=args.source,
    )
    print(f"Logged: {result}")


def main():
    parser = argparse.ArgumentParser(
        description="obsidian-brain — Connect LLM to Obsidian vault with Karpathy structure check",
    )
    sub = parser.add_subparsers()

    p_init = sub.add_parser("init", help="Initialize Karpathy wiki structure")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing templates")
    p_init.set_defaults(func=cmd_init)

    p_audit = sub.add_parser("audit", help="Audit vault for Karpathy compliance")
    p_audit.set_defaults(func=cmd_audit)

    p_push = sub.add_parser("push", help="Push a note to the vault")
    p_push.add_argument("--agent", required=True)
    p_push.add_argument("--title", required=True)
    p_push.add_argument("--content", required=True)
    p_push.add_argument("--tags", default="")
    p_push.set_defaults(func=cmd_push)

    p_search = sub.add_parser("search", help="Search the vault")
    p_search.add_argument("query")
    p_search.add_argument("--agent", default=None)
    p_search.set_defaults(func=cmd_search)

    p_recent = sub.add_parser("recent", help="Show recent notes")
    p_recent.add_argument("--agent", default=None)
    p_recent.add_argument("--limit", type=int, default=10)
    p_recent.set_defaults(func=cmd_recent)

    p_watch = sub.add_parser("watch", help="Watch vault and auto-sync (background)")
    p_watch.add_argument("--debounce", type=int, default=5, help="Seconds to wait before committing")
    p_watch.add_argument("--no-push", action="store_true", help="Commit locally but don't push")
    p_watch.set_defaults(func=cmd_watch)

    p_hook = sub.add_parser("hook", help="Log an event (ingest, note, query, etc.)")
    p_hook.add_argument("--type", required=True, choices=["ingest", "query", "lint", "note", "summary", "concept", "entity"])
    p_hook.add_argument("--title", required=True)
    p_hook.add_argument("--content", default="")
    p_hook.add_argument("--tags", default="")
    p_hook.add_argument("--source", default=None)
    p_hook.set_defaults(func=cmd_hook)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
