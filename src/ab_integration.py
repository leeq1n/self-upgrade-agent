"""A/B integration with daily-loop (per v3.3.0 sub-task 2/3).

Per 你 vision (self-upgrade agent 终极目标):
- 自动 KEPT/REJECT decision based on A/B data
- daily-loop uses compare_runs logic

Per LITERATURE Signal-to-Fix:
- Real signals drive decisions (not heuristics)
- Per Nate Berkopec: data-driven > gut-feel

Per 自上而下/分治 (user meta-principle):
- Big task: v3.3.0 A/B benchmark
- Sub-task 1 (done 9c912a4): core comparison logic
- Sub-task 2 (this commit): integration with daily-loop
- Sub-task 3 (future): statistical significance

Per P18: regression tests required.
Per P23 doc-first: spec exists in PROJECT_STATE + LITERATURE.
"""
import time
from pathlib import Path


def decide_round(round_data, baseline_metrics=None, test_path=None,
                 cwd=None):
    """Decide whether to keep a candidate round based on A/B comparison.

    Per LITERATURE Signal-to-Fix:
    - If candidate has tests_passed info, use it directly
    - Otherwise, run tests on candidate, compare with baseline
    - Return decision: "KEPT" | "REJECT" | "NO_PATCH"

    Args:
        round_data: dict with decision, tests_passed, etc. (from v2_round)
        baseline_metrics: pre-computed baseline test metrics (optional)
        test_path: optional test path for A/B comparison
        cwd: working directory for test execution

    Returns: (decision, reason)
    """
    decision = round_data.get("decision", "NO_PATCH")
    # If already rejected or no patch, no A/B needed
    if decision in ("REJECT", "NO_PATCH"):
        return decision, round_data.get("reason", "no patch")
    # If KEPT decision, optionally verify with A/B
    if decision == "KEPT" and test_path and baseline_metrics:
        from src.ab_benchmark import run_tests, compare_runs
        candidate_metrics = run_tests(test_path, cwd=cwd)
        comparison = compare_runs(baseline_metrics, candidate_metrics)
        if comparison["decision"] == "regression":
            return "REJECT", (
                f"A/B detected regression: "
                f"passes {comparison['passed_delta']}, "
                f"reason: {comparison['reason']}"
            )
        return "KEPT", f"A/B confirmed: {comparison['reason']}"
    return decision, round_data.get("reason", "kept by harness")


def daily_loop_with_ab(do_round, max_rounds=None, interval=0,
                       test_path=None, cwd=None, state_path=None,
                       enable_ab=True):
    """Run daily-loop with A/B verification (per v3.3.0 sub-task 2/3).

    Per 你 vision: 真 autonomous KEPT/REJECT decision.
    Combines daily_loop_persisted (v3.1.2) + ab_benchmark (v3.3.0).

    Args:
        do_round: callable(round_index) -> round_data dict
        max_rounds: max rounds (None = forever)
        interval: seconds between rounds
        test_path: optional test path for A/B
        cwd: working directory
        state_path: optional state.json path
        enable_ab: enable A/B verification (default True)

    Returns: dict with rounds_run, kept_count, rejected_count, failures_count
    """
    from src.daily_loop_integration import (
        init_daily_loop, record_round, record_failure,
    )
    from src.state_persistence import load_state

    init_daily_loop(state_path=state_path)
    state = load_state(state_path)
    start_idx = (state.get("last_round_index") or 0) + 1

    # Get baseline metrics (HEAD state)
    baseline_metrics = None
    if enable_ab and test_path:
        from src.ab_benchmark import run_tests
        baseline_metrics = run_tests(test_path, cwd=cwd)

    rounds = 0
    kept = 0
    rejected = 0
    failures = 0
    try:
        while max_rounds is None or rounds < max_rounds:
            round_idx = start_idx + rounds
            rounds += 1
            try:
                r = do_round(round_idx)
            except Exception as e:
                record_failure(round_idx, str(e), state_path)
                failures += 1
                continue
            # A/B decision
            final_decision, final_reason = decide_round(
                r, baseline_metrics=baseline_metrics,
                test_path=test_path, cwd=cwd)
            # Update round with final decision
            r["decision"] = final_decision
            r["reason"] = final_reason
            record_round(round_idx, r, state_path)
            if final_decision == "KEPT":
                kept += 1
            elif final_decision == "REJECT":
                rejected += 1
    except KeyboardInterrupt:
        pass
    return {
        "rounds_run": rounds,
        "kept_count": kept,
        "rejected_count": rejected,
        "failures_count": failures,
    }


def main():
    """CLI: show A/B integration status."""
    print("A/B integration status:")
    print("  Per LITERATURE Signal-to-Fix: decisions driven by data")
    print("  Per 你 vision: 真 autonomous KEPT/REJECT")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())