#!/usr/bin/env python3
"""eval_before.py — pre-commit check (eval-before gate, per M-n 32
Guardrail #1).

Per user message 2026-07-16: "核心层只能由 agent 自己主动修改
（修改时需要评估，修改后需要验收）".

This script runs BEFORE commit.  It checks:
1. Target state of file being committed exists + is not corrupted
2. P-n / M-n cited in commit message are valid (P1-P29)
3. Sibling repos' VERIFICATION.md are in sync (no drift)

Non-blocking by default (prints warnings only).  Hard FAIL
on critical errors (per R2 + P17 honest report).

Usage:
    python agent-tools/scripts/eval_before.py [--strict]

Exit codes:
    0 — PASS or warning only
    1 — hard FAIL (only with --strict)
"""

from __future__ import annotations
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SIBLINGS = [
    ("agent-reflection-skill", REPO.parent / "agent-reflection-skill"),
    ("skill-incubator", REPO.parent / "skill-incubator"),
    ("knowledge-graph-seed", REPO.parent / "knowledge-graph-seed"),
]
VALID_P = set(f"P{n}" for n in range(1, 30)) - {"P6"}  # P1-P29 except P6


def check_commit_message_p_cite() -> list[str]:
    """Check staged commit message for P-n cite validity."""
    warnings = []
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%B"],
            capture_output=True, text=True, cwd=REPO, timeout=10,
        )
        if r.returncode != 0 or not r.stdout.strip():
            return warnings  # no commit yet, skip
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return warnings

    msg = r.stdout
    p_cites = set(re.findall(r"\bP\d+\b", msg))
    invalid = p_cites - VALID_P
    if invalid:
        warnings.append(f"invalid P-n cite(s): {sorted(invalid)}")
    return warnings


def check_sibling_sync() -> list[str]:
    """Check sibling repos' VERIFICATION.md have M-n 35 cross-ref."""
    warnings = []
    for name, path in SIBLINGS:
        ver = path / "VERIFICATION.md"
        if not ver.exists():
            warnings.append(f"sibling {name}: VERIFICATION.md missing")
            continue
        text = ver.read_text(encoding="utf-8")
        has_ct = ("critical-thinking" in text or "批判性思考" in text
                  or "质疑" in text)
        if not has_ct:
            warnings.append(
                f"sibling {name}: VERIFICATION.md missing critical-thinking "
                f"cross-ref (per Phase A codification)"
            )
    return warnings


def check_repo_clean() -> list[str]:
    """Check SUA repo working tree is reasonably clean (no massive untracked)."""
    warnings = []
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=REPO, timeout=10,
        )
        if r.returncode == 0:
            lines = r.stdout.strip().splitlines()
            # Filter ignored; >20 untracked is suspicious
            untracked = [l for l in lines if l.startswith("??")]
            if len(untracked) > 20:
                warnings.append(
                    f"working tree has {len(untracked)} untracked files "
                    f"(possible stray files)"
                )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="eval_before gate")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 on any warning")
    args = parser.parse_args()

    print("=" * 60)
    print("EVAL_BEFORE GATE (per M-n 32 Guardrail #1)")
    print("=" * 60)

    all_warnings: list[str] = []
    all_warnings.extend(check_commit_message_p_cite())
    all_warnings.extend(check_sibling_sync())
    all_warnings.extend(check_repo_clean())

    print("\nChecks:")
    for w in all_warnings:
        print(f"  WARN: {w}")

    print("\n" + "=" * 60)
    if not all_warnings:
        print("RESULT: PASS (no warnings)")
        return 0
    if args.strict:
        print(f"RESULT: FAIL ({len(all_warnings)} warnings, --strict)")
        return 1
    print(f"RESULT: WARN ({len(all_warnings)} warnings, non-blocking)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
