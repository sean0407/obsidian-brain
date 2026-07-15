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

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
