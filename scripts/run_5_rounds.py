"""scripts/run_5_rounds.py - 5 consecutive KEPT rounds (stability test).

Usage:
    python scripts/run_5_rounds.py

For each of 5 rounds:
  - Runs run_one_round with FIXED_PAPER (DyLAN 2310.02170)
  - Target: core/planner.py
  - Test gate: tests/test_pipeline.py (fast)

Prints summary:
  - Per-round decision + elapsed time + tests pass/fail
  - Final summary with KEPT count

NOTE: A KEPT round WILL modify core/planner.py.  To restore,
just `git checkout core/planner.py` afterward.

P18 (PRINCIPLES.md) notes:
  - Each round may produce a NO_PATCH / APPLY_FAILED / REVERTED /
    KEPT decision.  This is expected — not all 5 will be KEPT.
  - The goal is to confirm the loop is stable, not to force
    5/5 KEPT.
"""
import json
import sys
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from src.v2_round import run_one_round
from src.v2_agent import FIXED_PAPER


def main():
    target = "core/planner.py"
    test_path = "tests/test_pipeline.py"
    results = []
    t0 = time.time()
    for i in range(1, 6):
        print(f"=== Round {i}/5 ===")
        round_t0 = time.time()
        r = run_one_round(
            paper=FIXED_PAPER,
            target_module=target,
            test_path=test_path,
        )
        round_t = time.time() - round_t0
        rec = {
            "round": i,
            "decision": r.decision,
            "elapsed_s": round(round_t, 1),
            "tests_passed": r.tests_passed,
            "tests_failed": r.tests_failed,
            "error": r.error,
        }
        results.append(rec)
        print(f"  decision={r.decision} elapsed={round_t:.1f}s "
              f"passed={r.tests_passed} failed={r.tests_failed}")
        if r.error:
            print(f"  error: {r.error[:120]}")
    total_t = time.time() - t0
    print()
    print("=== SUMMARY ===")
    decisions = [r["decision"] for r in results]
    print(f"Total elapsed: {total_t:.1f}s")
    print(f"Decisions: {decisions}")
    kept = decisions.count("KEPT")
    reverted = decisions.count("REVERTED")
    no_patch = decisions.count("NO_PATCH")
    apply_failed = decisions.count("APPLY_FAILED")
    print(f"KEPT: {kept}/5  REVERTED: {reverted}/5  "
          f"NO_PATCH: {no_patch}/5  APPLY_FAILED: {apply_failed}/5")
    print()
    if kept == 5:
        print("=> Loop is STABLE: 5/5 KEPT")
    elif kept == 0:
        print("=> Loop is BLOCKED: 0/5 KEPT (LLM may need prompt fix)")
    else:
        print(f"=> Loop is MIXED: {kept}/5 KEPT (LLM temperature is "
              "non-zero; may need prompt or seed)")
    print()
    print("To restore core/planner.py if a round KEPT:")
    print("  git checkout core/planner.py")


if __name__ == "__main__":
    main()