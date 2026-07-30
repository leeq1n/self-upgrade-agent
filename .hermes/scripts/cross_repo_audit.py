#!/usr/bin/env python3
"""SUA cross-repo audit (Q3 enforcement: principle-collapse prevention).

Why this exists:
  SUA hooks (commit-msg + pre-commit) enforce discipline within ONE repo.
  They do not enforce that sibling / consumer repos stay in sync with
  upstream SUA's principles. Result: a sibling repo can re-introduce
  `core-layer/`, `docs/`, `src/` mirrors of upstream without any local
  hook noticing. This script audits sibling repos from upstream's
  perspective, surfacing drift before it becomes principle collapse.

What it audits (read-only, output as JSON):
  1. sibling_path_to_adapter: each sibling must contain an `adapter/`
     directory (Leaf-Only contract per docs/PRINCIPLE_COLLAPSE_PREVENTION.md).
  2. sibling_no_mirror_files: sibling must NOT contain a top-level
     `core-layer/`, `docs/`, `hooks/`, or `src/` directory that mirrors
     upstream SUA's structure (P-11 mirror-not-replicate).
  3. sibling_agencies_md_self_contained: sibling AGENTS.md / README.md
     must not contain internal refs (round numbers, hermes-root paths,
     per-user-message phrases) per P-14 self-contained mandate.
  4. sibling_submodule_pinned: if sibling is configured as a submodule
     consumer of upstream, the submodule pointer should reference a
     release tag (not a moving branch head) per R3.

Output: JSON to stdout. CI integration: nonzero exit if any check
fails. By default the audit is advisory; the calling hook decides
enforcement (per STRICT_EVAL convention).

Run:
  python .hermes/scripts/cross_repo_audit.py
  python .hermes/scripts/cross_repo_audit.py --sibling /path/to/sibling
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SUA = Path(__file__).resolve().parents[2]

# Default sibling locations to audit. Override via --sibling flag or
# SIBLING_PATHS env var (colon-separated for portability).
DEFAULT_SIBLING_REL = [
    "../sua-start/self-upgrade-agent",  # tua-start legacy reference
]

# Mirror-pollution patterns: top-level paths that would indicate
# sibling is re-holding upstream content instead of referencing it.
MIRROR_FORBIDDEN_TOP_DIRS = [
    "core-layer", "docs", "hooks", "src", "benchmarks",
]

# Internal-reference patterns that should never appear in user-facing
# sibling files (per P-14 self-contained mandate).
INTERNAL_REF_PATTERNS = [
    (r"\b[Pp]er user message \d{4}-\d{2}-\d{2}\b", "per-user-message ref"),
    (r"\bper R\d+\b", "R-number ref"),
    (r"\bper R-\d+\b", "R-number ref"),
    (r"\bper c\d+\b", "c-number ref"),
    (r"\bhermes-root[/\\]", "hermes-root path"),
    (r"AGENTS_DETAIL\.md", "AGENTS_DETAIL cross-ref"),
]


def _git(*args, cwd=None):
    """Run a git command, return stdout (empty string on failure)."""
    try:
        return subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=10
        ).stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _resolve_sibling(path_str):
    """Resolve sibling path. If relative, treat as relative to SUA's parent."""
    p = Path(path_str)
    if p.is_absolute():
        return p.resolve()
    # Relative to SUA's parent (where sibling repos typically live)
    return (SUA.parent / p).resolve()


def audit_sibling_has_adapter(sibling_path):
    """Sibling must contain an `adapter/` directory.

    Per Leaf-Only contract: a sibling is allowed to exist ONLY if it
    owns adapter code that does not exist upstream. An empty sibling
    with no `adapter/` directory violates the contract and is drift
    toward principle collapse.
    """
    failed = []
    if not sibling_path.exists():
        failed.append("sibling path does not exist")
        return failed
    adapter_dir = sibling_path / "adapter"
    if not adapter_dir.is_dir():
        failed.append("missing adapter/ directory (Leaf-Only contract)")
    elif not any(adapter_dir.iterdir()):
        failed.append("adapter/ exists but is empty (no leaf content)")
    return failed


def audit_sibling_no_mirror(sibling_path):
    """Sibling must NOT mirror upstream SUA content.

    Per P-11 mirror-not-replicate. If sibling contains a top-level
    `core-layer/`, `docs/`, `hooks/`, `src/`, or `benchmarks/` that
    has identical structure to upstream, that's mirror pollution.
    """
    failed = []
    if not sibling_path.exists():
        return failed
    for dirname in MIRROR_FORBIDDEN_TOP_DIRS:
        target = sibling_path / dirname
        if target.is_dir():
            # Count files; if it has more than 5 entries it's likely mirror.
            count = sum(1 for _ in target.rglob("*") if _.is_file())
            if count > 5:
                failed.append(
                    f"top-level {dirname}/ has {count} files "
                    f"(looks like upstream mirror pollution)"
                )
    return failed


def audit_sibling_self_contained(sibling_path):
    """Sibling user-facing files must not contain internal refs.

    Per P-14 self-contained mandate. AGENTS.md / README.md / TASK_HANDOVER.md
    are user-facing and must not leak dev-internal references.
    """
    failed = []
    if not sibling_path.exists():
        return failed
    user_facing_files = ["AGENTS.md", "README.md", "TASK_HANDOVER.md"]
    for filename in user_facing_files:
        fp = sibling_path / filename
        if not fp.is_file():
            continue
        content = fp.read_text(encoding="utf-8", errors="ignore")
        for pattern, label in INTERNAL_REF_PATTERNS:
            if re.search(pattern, content):
                failed.append(f"{filename} contains {label}")
    return failed


def audit_sibling_submodule_pinned(sibling_path):
    """If sibling uses submodule to reference SUA, submodule should pin
    to a release tag (not branch head)."""
    failed = []
    if not sibling_path.exists():
        return failed
    gitmodules = sibling_path / ".gitmodules"
    if not gitmodules.is_file():
        # No submodule configured — not necessarily a failure.
        return failed
    content = gitmodules.read_text(encoding="utf-8")
    # Look for branch = (not tag =). Tag-pinned submodules are explicit.
    if re.search(r"branch\s*=\s*\w+", content) and not re.search(
        r"tag\s*=\s*\w+", content
    ):
        # Submodule pins to a branch, not a tag. Tag pinning is preferred.
        failed.append(
            ".gitmodules pins submodule to branch (prefer tag =)"
        )
    return failed


def audit_one_sibling(sibling_path):
    """Run all checks on one sibling path. Return dict of check results."""
    return {
        "path": str(sibling_path),
        "exists": sibling_path.exists(),
        "checks": {
            "has_adapter": audit_sibling_has_adapter(sibling_path),
            "no_mirror_files": audit_sibling_no_mirror(sibling_path),
            "agencies_md_self_contained": audit_sibling_self_contained(sibling_path),
            "submodule_pinned": audit_sibling_submodule_pinned(sibling_path),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="SUA cross-repo audit (Q3 principle-collapse prevention)"
    )
    parser.add_argument(
        "--sibling", action="append", default=[],
        help="Sibling path to audit (can repeat). Default: ../sua-start",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit nonzero on any failure (default: advisory only)",
    )
    args = parser.parse_args()

    siblings = args.sibling if args.sibling else DEFAULT_SIBLING_REL
    sibling_paths = [_resolve_sibling(s) for s in siblings]

    results = [audit_one_sibling(p) for p in sibling_paths]
    total_failures = sum(
        sum(len(v) for v in r["checks"].values()) for r in results
    )

    output = {
        "audit": "cross_repo_audit",
        "upstream": str(SUA),
        "siblings_audited": len(results),
        "total_failures": total_failures,
        "results": results,
        "verdict": "PASS" if total_failures == 0 else "FAIL",
    }
    print(json.dumps(output, indent=2))

    if args.strict and total_failures > 0:
        sys.exit(1)
    # Advisory by default; let the calling hook decide.
    sys.exit(0)


if __name__ == "__main__":
    main()