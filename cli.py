#!/usr/bin/env python3
"""
obsidian-brain CLI
Usage:
    obrain push --agent scout --title "Topic" --content "..."
    obrain search "query"
    obrain recent --limit 10
    obrain init --repo https://github.com/user/repo.git
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for local dev
sys.path.insert(0, str(Path(__file__).parent))

from obsidian_brain import Brain, Config


def cmd_push(args):
    brain = Brain()
    path = brain.push(
        agent=args.agent,
        title=args.title,
        content=args.content,
        tags=args.tags.split(",") if args.tags else [],
        auto_commit=True,
    )
    print(f"✅ Pushed to: {path}")


def cmd_search(args):
    brain = Brain()
    results = brain.search(args.query, agent=args.agent)
    if not results:
        print("No results found.")
        return
    for r in results:
        print(f"- [{r['folder']}] {r['file']}")


def cmd_recent(args):
    brain = Brain()
    notes = brain.get_recent(agent=args.agent, limit=args.limit)
    for n in notes:
        print(f"- {n['modified'][:16]} [{n['folder']}] {n['file']}")


def cmd_init(args):
    brain = Brain()
    brain.git.init(repo_url=args.repo)
    print(f"✅ Git initialized in vault: {brain.config.vault_path}")


def cmd_graph(args):
    brain = Brain()
    graph = brain.build_graph()
    print(f"Nodes: {len(graph['nodes'])}, Links: {len(graph['links'])}")


def main():
    parser = argparse.ArgumentParser(description="obsidian-brain CLI")
    sub = parser.add_subparsers()

    # push
    p = sub.add_parser("push", help="Push a note to the vault")
    p.add_argument("--agent", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--tags", default="")
    p.set_defaults(func=cmd_push)

    # search
    s = sub.add_parser("search", help="Search the vault")
    s.add_argument("query")
    s.add_argument("--agent", default=None)
    s.set_defaults(func=cmd_search)

    # recent
    r = sub.add_parser("recent", help="Show recent notes")
    r.add_argument("--agent", default=None)
    r.add_argument("--limit", type=int, default=10)
    r.set_defaults(func=cmd_recent)

    # init
    i = sub.add_parser("init", help="Initialize git repo")
    i.add_argument("--repo", default="")
    i.set_defaults(func=cmd_init)

    # graph
    g = sub.add_parser("graph", help="Show vault graph stats")
    g.set_defaults(func=cmd_graph)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
