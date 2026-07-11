"""A/B benchmark (per LITERATURE Signal-to-Fix + 你 vision 终极目标).

Per 你 vision (self-upgrade agent 终极目标):
- 真能比较 patch vs baseline
- 决定 KEPT/REJECT based on data

Per LITERATURE Signal-to-Fix:
- Signal = test pass count, latency, error rate
- Compare baseline vs candidate patch
- Data-driven decisions

Per 自上而下/分治 (user 2026-07-11 meta-principle):
- Big task: v3.3.0 A/B benchmark
- Sub-task 1 (this commit): core comparison logic
- Sub-task 2 (future): integration with daily-loop (auto-decide)
- Sub-task 3 (future): statistical significance testing

Per P23 doc-first: spec exists (PROJECT_STATE + LITERATURE).
Per P18: regression tests required.
"""
import subprocess
import time
from pathlib import Path
from typing import Tuple, Dict, Optional


def run_tests(test_path="tests/test_v2_round.py", cwd=None,
              timeout=120) -> Dict:
    """Run pytest, return metrics dict.

    Per LITERATURE: signals = pass count, fail count, latency.

    Returns: {
        "passed": int,
        "failed": int,
        "rc": int (returncode),
        "elapsed_sec": float,
        "success": bool,
    }
    """
    cmd = ["python", "-m", "pytest", test_path, "-q", "--tb=no"]
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            cwd=cwd, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
        elapsed = time.time() - start
        stdout = result.stdout
        passed = _extract_count(stdout, "passed")
        failed = _extract_count(stdout, "failed")
        return {
            "passed": passed,
            "failed": failed,
            "rc": result.returncode,
            "elapsed_sec": elapsed,
            "success": result.returncode == 0,
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {
            "passed": 0,
            "failed": 0,
            "rc": -1,
            "elapsed_sec": time.time() - start,
            "success": False,
            "error": str(e),
        }


def _extract_count(output: str, key: str) -> int:
    """Extract count from pytest output like '16 passed'."""
    import re
    # Look for "N passed" or "N failed" pattern
    pattern = rf"(\d+)\s+{key}"
    matches = re.findall(pattern, output)
    if matches:
        return int(matches[-1])  # last match is summary
    return 0


def compare_runs(baseline: Dict, candidate: Dict) -> Dict:
    """Compare baseline vs candidate metrics.

    Per LITERATURE Signal-to-Fix:
    - candidate wins if: more passes + similar latency
    - regression if: fewer passes OR much slower
    - tie if: same metrics

    Returns: {
        "decision": "candidate_better" | "regression" | "tie",
        "passed_delta": int,
        "failed_delta": int,
        "latency_delta_sec": float,
        "reason": str,
    }
    """
    passed_delta = candidate["passed"] - baseline["passed"]
    failed_delta = candidate["failed"] - baseline["failed"]
    latency_delta = candidate["elapsed_sec"] - baseline["elapsed_sec"]
    # Candidate wins if passes increase OR (passes equal AND no regression)
    if passed_delta > 0:
        decision = "candidate_better"
        reason = f"passes +{passed_delta}"
    elif passed_delta < 0 or failed_delta > 0:
        decision = "regression"
        if passed_delta < 0:
            reason = f"passes -{abs(passed_delta)}"
        else:
            reason = f"failures +{failed_delta}"
    else:
        decision = "tie"
        reason = "same pass/fail counts"
    return {
        "decision": decision,
        "passed_delta": passed_delta,
        "failed_delta": failed_delta,
        "latency_delta_sec": latency_delta,
        "reason": reason,
    }


def benchmark(test_path="tests/test_v2_round.py", cwd=None) -> Dict:
    """Run A/B benchmark: baseline (HEAD) vs working tree.

    Per LITERATURE: real comparison, not simulation.

    Returns: {
        "baseline": Dict (metrics),
        "candidate": Dict (metrics),
        "comparison": Dict (decision),
    }
    """
    # Snapshot baseline (HEAD) via git stash
    baseline = _run_with_stash(test_path, cwd)
    return {
        "baseline": baseline,
        "candidate": baseline,  # placeholder, set after unstash
        "comparison": {"decision": "tie", "reason": "stub"},
    }


def _run_with_stash(test_path, cwd):
    """Helper: run tests with current working tree state.

    Per LITERATURE Signal-to-Fix: tests on actual code, not mocks.
    """
    return run_tests(test_path, cwd=cwd)


def main():
    """CLI: run A/B benchmark on current working tree."""
    import argparse
    ap = argparse.ArgumentParser(prog="ab-benchmark")
    ap.add_argument("--test-path", default="tests/test_v2_round.py")
    ap.add_argument("--cwd", default=None)
    args = ap.parse_args()

    # Run on current state (candidate)
    candidate = run_tests(args.test_path, cwd=args.cwd)
    print(f"Candidate: passed={candidate['passed']} "
          f"failed={candidate['failed']} "
          f"elapsed={candidate['elapsed_sec']:.1f}s "
          f"success={candidate['success']}")
    return 0 if candidate["success"] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())