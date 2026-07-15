"""
Audit module for obsidian-brain.
Checks if a vault follows the Karpathy LLM-wiki structure.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class AuditResult:
    """Result of a vault structure audit."""
    passed: bool
    score: int  # 0-100
    findings: List[dict]  # List of {severity, message, suggestion}
    structure: dict  # Current vault structure


def audit_vault(vault_path: str) -> AuditResult:
    """
    Audit a vault for Karpathy LLM-wiki compliance.

    Reference: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

    Expected structure:
        vault/
        ├── sources/        (immutable raw materials)
        ├── wiki/           (LLM-maintained markdown)
        │   ├── concepts/
        │   ├── entities/
        │   └── summaries/
        ├── queries/        (Q&A records)
        ├── index.md        (content catalog)
        ├── log.md          (chronological log)
        └── CLAUDE.md       (schema / operations guide)
    """
    vault = Path(vault_path)
    if not vault.exists():
        return AuditResult(
            passed=False,
            score=0,
            findings=[{
                "severity": "error",
                "message": f"Vault not found: {vault_path}",
                "suggestion": "Verify the path or create a new Obsidian vault.",
            }],
            structure={},
        )

    findings = []
    structure = _map_structure(vault)

    # Required top-level folders
    required_folders = {
        "sources": "Immutable raw materials - articles, papers, images, data files.",
        "wiki": "LLM-maintained markdown - the structured, interlinked wiki.",
    }
    for folder, purpose in required_folders.items():
        if not (vault / folder).exists():
            findings.append({
                "severity": "warning",
                "message": f"Missing folder: `{folder}/`",
                "suggestion": f"Create this folder. Purpose: {purpose}",
            })

    # Recommended wiki subfolders
    wiki_subfolders = ["concepts", "entities", "summaries"]
    if (vault / "wiki").exists():
        for sub in wiki_subfolders:
            if not (vault / "wiki" / sub).exists():
                findings.append({
                    "severity": "info",
                    "message": f"Missing wiki subfolder: `wiki/{sub}/`",
                    "suggestion": f"Create `wiki/{sub}/` for organized wiki content.",
                })

    # Recommended folders
    recommended = ["queries"]
    for folder in recommended:
        if not (vault / folder).exists():
            findings.append({
                "severity": "info",
                "message": f"Missing recommended folder: `{folder}/`",
                "suggestion": f"Create this folder to track Q&A and exploration history.",
            })

    # Required files
    required_files = {
        "index.md": "Content catalog - list every page with one-line summary.",
        "log.md": "Chronological log - record ingests, queries, lint passes.",
        "CLAUDE.md": "Schema file - tell the LLM how the wiki is structured and how to operate on it.",
    }
    for fname, purpose in required_files.items():
        if not (vault / fname).exists():
            severity = "error" if fname == "CLAUDE.md" else "warning"
            findings.append({
                "severity": severity,
                "message": f"Missing file: `{fname}`",
                "suggestion": f"Create this file. Purpose: {purpose}",
            })

    # Calculate score
    score = _calculate_score(findings, structure)

    # Determine pass status
    errors = sum(1 for f in findings if f["severity"] == "error")
    passed = errors == 0 and score >= 60

    return AuditResult(
        passed=passed,
        score=score,
        findings=findings,
        structure=structure,
    )


def _map_structure(vault: Path) -> dict:
    """Map the current vault directory structure."""
    structure = {"folders": [], "files": [], "markdown_count": 0}

    for item in sorted(vault.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir():
            structure["folders"].append(item.name)
        elif item.is_file():
            structure["files"].append(item.name)
            if item.suffix == ".md":
                structure["markdown_count"] += 1

    return structure


def _calculate_score(findings: list, structure: dict) -> int:
    """Calculate a 0-100 compliance score."""
    score = 100

    for f in findings:
        if f["severity"] == "error":
            score -= 20
        elif f["severity"] == "warning":
            score -= 10
        elif f["severity"] == "info":
            score -= 3

    return max(0, score)


def format_report(result: AuditResult) -> str:
    """Format audit result as a readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("  obsidian-brain  /  Karpathy LLM-wiki Audit")
    lines.append("=" * 60)
    lines.append("")

    status = "PASS" if result.passed else "NEEDS WORK"
    lines.append(f"Status: {status}")
    lines.append(f"Score:  {result.score} / 100")
    lines.append("")

    lines.append("Current Structure:")
    if result.structure.get("folders"):
        for f in result.structure["folders"]:
            lines.append(f"  [DIR]  {f}/")
    if result.structure.get("files"):
        for f in result.structure["files"]:
            lines.append(f"  [FILE] {f}")
    lines.append(f"  Markdown notes: {result.structure.get('markdown_count', 0)}")
    lines.append("")

    if not result.findings:
        lines.append("No issues found! Your vault follows the LLM-wiki pattern.")
        return "\n".join(lines)

    # Group by severity
    for severity in ["error", "warning", "info"]:
        items = [f for f in result.findings if f["severity"] == severity]
        if not items:
            continue

        icon = {"error": "[X]", "warning": "[!]", "info": "[i]"}[severity]
        lines.append(f"{icon} {severity.upper()}S ({len(items)})")
        for item in items:
            lines.append(f"   - {item['message']}")
            lines.append(f"     -> {item['suggestion']}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("Quick fixes:")
    lines.append("  - Run `obrain init` to create the recommended structure")
    lines.append("  - See templates/CLAUDE.md for the schema template")
    lines.append("  - Re-run `obrain audit` after manual changes")
    lines.append("=" * 60)

    return "\n".join(lines)
