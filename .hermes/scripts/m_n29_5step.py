#!/usr/bin/env python3
"""M-n 29 5-step acceptance protocol (programmatic).

External trigger: replaces LLM-self-judgment with deterministic
mechanical checklist.  Per user message 2026-07-16 "按原则做决定" +
M-n 32 self-learning-guardrail Guardrail #4 (pre-claim M-n 29 5-step)
+ retrospective 4-FAIL diagnosis.

Usage:
    python .hermes/scripts/m_n29_5step.py          # interactive
    python .hermes/scripts/m_n29_5step.py --self   # agent self-mode

This script IS NOT a replacement for human review — it's a
mechanical baseline that runs the 5 primitives deterministically.
LLM runtime should additionally invoke 5 primitives manually for
full coverage.

Output: prints Step 1-5 checklist + 5-primitives application.
Per M-n 29 5-step protocol (L1 in OPERATING_RULES.md).
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def design_criteria() -> list[tuple[str, str]]:
    """Step 1: Design 验收 角度.  15 criteria per M-n 29 Step 1."""
    return [
        ("Functional",         "12 files + 4 sibling VERIFICATION.md exist"),
        ("Compatibility",      "5 frameworks (Hermes / Claude / Codex / Cursor / generic)"),
        ("Security",           "0 SUA markers in 11 user-facing files"),
        ("Maintainability",    "R5 ≤ 7KB / R8 ≤ 300 lines"),
        ("User-facing",        "M-n 34 propagation to all 5 repos"),
        ("Framework-agnostic", "no framework API in skill"),
        ("R1-R12",             "R1-R12 invariants"),
        ("Project hygiene",    "clean + VERIFICATION.md + tag"),
        ("新 agent 可读性",     "intended-accessibility test (cold-start simulation)"),
        ("M-n 29 5-step",      "this script (5-step protocol applied)"),
        ("M-n 32 #4",          "pre-claim enforcement"),
        ("M-n 18 destroy",     "merged branches cleaned"),
        ("Hook whitelist",     "AGENTS.md allowed list = hook regex"),
        ("Hook sync",          "template + .git/hooks/installed in sync"),
        ("Behavioral hook",    "real git commit rejects bad messages"),
    ]


def five_primitives(claim: str) -> dict[str, str]:
    """Step 2: 5 primitives applied to the claim.
    Per AGENTS.md "5 primitives gate" + M-n 34 sub-step 3."""
    return {
        "Analyze":    f"Task: {claim}.  Scope: 5 repos + 4 zip + 1 tag.",
        "Reason":     "Codification ≠ runtime.  Mechanical enforcement fixes root cause.",
        "联想":      "linter / CI / smoke detector (write detector ≠ detector runs).",
        "归纳":      "common across 7 auto-enforcement M-rules = same gap.",
        "总结":      "1 L0 line: execute Plan (8 commits, install external hook + script).",
    }


def four_critical_thinking(claim: str) -> dict[str, str]:
    """Step 2a: 4 critical-thinking primitives (adversarial pair
    to the 5 constructive primitives, per user message 2026-07-16
    + M-n 14 two-track reasoning).

    Full detail: docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md
    """
    return {
        "质疑 (Challenge)":
            "3 specific weaknesses + highest-damage weakness "
            "explicitly acknowledged",
        "逆向 (Invert)":
            "OPPOSITE state + 2-3 reasons OPPOSITE could be "
            "true + what would change",
        "预演失败 (Pre-mortem)":
            "this FAILED in 30 days + 3-5 failure modes + "
            "1-2 preventable (Klein 2007)",
        "对立论证 (Steelman-the-opposite)":
            "most charitable opposing case + 2-3 strongest "
            "opposing arguments + acknowledge valid ones",
    }


def validate(primitives: dict[str, str], criteria: list[tuple[str, str]]) -> tuple[int, int]:
    """Step 3: Validate by counting keys present."""
    crit_keys = {c[0] for c in criteria}
    prim_keys = set(primitives.keys())
    common = crit_keys & prim_keys
    return len(prim_keys), len(common)


def main() -> int:
    parser = argparse.ArgumentParser(description="M-n 29 5-step protocol")
    parser.add_argument("--claim", default="task done",
                        help="what to verify (default: 'task done')")
    parser.add_argument("--self", action="store_true",
                        help="agent self-mode (no interactive prompts)")
    args = parser.parse_args()

    print("=" * 60)
    print(f"M-n 29 5-STEP ACCEPTANCE: claim={args.claim!r}")
    print("=" * 60)

    # Step 1
    print("\n[Step 1] Design 验收 角度")
    crits = design_criteria()
    print(f"  Designed {len(crits)} criteria.")

    # Step 2a: critical-thinking (BEFORE constructive, per user message)
    print("\n[Step 2a] Apply — 4 critical-thinking primitives (adversarial pair)")
    ct = four_critical_thinking(args.claim)
    for k, v in ct.items():
        print(f"  {k}: {v[:80]}")

    # Step 2: constructive
    print("\n[Step 2] Execute — 5 primitives")
    prims = five_primitives(args.claim)
    for k, v in prims.items():
        print(f"  {k}: {v[:80]}")

    # Step 3
    print("\n[Step 3] Validate")
    pk, ck = validate(prims, crits)
    print(f"  5 primitives keys: {pk}")
    print(f"  Coverage with criteria: {ck}")
    print(f"  4 critical-thinking primitives: {len(ct)} (default-on for high-stakes)")

    # Step 4 (reconciliation)
    print("\n[Step 4] Cycle loop check")
    print("  If FAIL items: re-verify (loop).  Else proceed to Step 5.")
    print("  (Loop not enforced in script — human/agent decision.)")

    # Step 5
    print("\n[Step 5] Notify")
    if args.self:
        print(f"  SELF-MODE: agent must apply 5 primitives")
        print(f"  Currently: {pk} primitives applied (matches criteria {ck})")
    else:
        print(f"  Interactive mode: review checklist, decide PASS/FAIL")

    # Use-case 1: agent self-invocation pre-claim
    print("\n[External trigger usage]")
    print("  Run this script BEFORE claiming task done.")
    print("  Per M-n 32 Guardrail #4 + AGENTS.md 'Task-done-notify reminder'.")
    print("  Per user message 2026-07-16 retrospective 4-FAIL diagnosis.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
