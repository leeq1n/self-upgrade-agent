#!/usr/bin/env python3
"""verify_after.py — post-commit check (verify-after gate, per M-n 32
Guardrail #1 + core-layer/governance-template.md).

Per user message 2026-07-16: "修改时需要评估，修改后需要验收".
Per core-layer/governance-template.md "Verify-After Step 1"
+ "Step 2" + "Step 3".

This script runs AFTER commit.  It checks:
1. Working tree is clean (no uncommitted changes)
2. M-n 29 5-step applied (commit message has '5 primitives' OR
   'M-n 29' reference; OR critical-thinking keyword)
3. Cold-start simulation: 3 trigger points reachable from
   AGENTS.md entry doc

Non-blocking by default (prints status only).  Hard FAIL on
critical issues only.

Usage:
    python .hermes/scripts/verify_after.py [--strict]

Exit codes:
    0 — PASS
    1 — hard FAIL (only with --strict)
"""

from __future__ import annotations
import argparse
import re
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]


def check_working_tree_clean() -> tuple[bool, str]:
    """Check working tree clean after commit."""
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=REPO, timeout=10,
        )
        if r.returncode != 0:
            return False, "git status failed"
        if not r.stdout.strip():
            return True, "working tree clean"
        return False, f"working tree dirty: {len(r.stdout.splitlines())} entries"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "git not available"


def check_commit_message_compliance() -> tuple[bool, str]:
    """Check last commit message has P-n cite + 5-primitives OR
    critical-thinking."""
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%B"],
            capture_output=True, text=True, cwd=REPO, timeout=10,
        )
        if r.returncode != 0:
            return False, "git log failed"
        msg = r.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "git not available"

    has_p = bool(re.search(r"\bP\d+\b", msg))
    has_5p = bool(re.search(
        r"Analyze.*Reason.*联想.*归纳.*总结|5 primitives|M-n 29", msg
    ))
    has_ct = bool(re.search(
        r"质疑|Challenge|Invert|逆向|Pre-mortem|预演失败|Steelman|对立论证",
        msg
    ))

    if not has_p:
        return False, "P-n cite missing"
    if not (has_5p or has_ct):
        return False, "5 primitives OR critical-thinking missing"
    return True, "commit message compliant"


def check_cold_start_simulation() -> tuple[bool, str]:
    """Check AGENTS.md + INDEX.md L0 reachability."""
    ag = REPO / "AGENTS.md"
    idx = REPO / "docs" / "INDEX.md"

    if not ag.exists():
        return False, "AGENTS.md missing"
    if not idx.exists():
        return False, "INDEX.md missing"

    ag_text = ag.read_text(encoding="utf-8")
    idx_text = idx.read_text(encoding="utf-8")

    # Check 3 trigger points
    checks = {
        "M-n 34 pre-task scan in AGENTS.md":
            "Pre-task scan (M-n 34" in ag_text,
        "M-n 35 critical-thinking in AGENTS.md":
            "M_CRITICAL_THINKING_PRIMITIVES_DETAIL" in ag_text,
        "core-layer reference in INDEX.md":
            "core-layer" in idx_text,
    }

    failed = [k for k, v in checks.items() if not v]
    if failed:
        return False, f"trigger points missing: {failed}"
    return True, "all 3 trigger points reachable"


def main() -> int:
    parser = argparse.ArgumentParser(description="verify_after gate")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 on any FAIL")
    args = parser.parse_args()

    print("=" * 60)
    print("VERIFY_AFTER GATE (per M-n 32 Guardrail #1)")
    print("=" * 60)

    checks = [
        check_working_tree_clean(),
        check_commit_message_compliance(),
        check_cold_start_simulation(),
    ]

    print("\nChecks:")
    all_pass = True
    for ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {detail}")
        if not ok:
            all_pass = False

    print("\n" + "=" * 60)
    if all_pass:
        print("RESULT: PASS (all 3 checks)")
        return 0
    if args.strict:
        print("RESULT: FAIL (--strict)")
        return 1
    print("RESULT: FAIL (non-blocking)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
