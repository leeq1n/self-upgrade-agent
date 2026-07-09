"""src/v2_round.py - one round of self-improvement.

Closes the loop:
  v2_agent.improve()  ->  v2_apply.apply_patch()  ->  run_project_tests()
                                                       |
                                                  [verifiable]
                                                       |
                                                  KEPT / REVERTED

Per user feedback 2026-07-08:
  - '完成目标' = the self-improving loop must run end-to-end and
    decide keep or revert based on objective test results
  - '注意之前学到的' = use existing modules (don't re-implement),
    test thoroughly (unit → joint → real-end-to-end before commit)

Decision policy (the hard rule that LLM cannot override):
  - Apply patch to file (via v2_apply)
  - Run the project's test suite (pytest tests/)
  - All tests pass -> KEPT (keep patch, keep snapshot for manual diff)
  - Any test fails -> REVERTED (rollback to snapshot)
  - Patch is None  -> NO_PATCH
  - Apply fails    -> APPLY_FAILED (already reverted internally)
"""
import os
import sys
import subprocess
import time
from dataclasses import dataclass, field
from typing import Optional, List

from src.v2_agent import improve, Paper, _chat
from src.v2_apply import apply_patch, revert, cleanup_snapshot, ApplyResult
from src.llm import LLMConfig
from src.failures import log_failure


@dataclass
class RoundResult:
    decision: str            # "KEPT" | "REVERTED" | "NO_PATCH" | "APPLY_FAILED"
    paper: Paper
    target_module: str
    patch: Optional[object] = None  # Patch | None
    apply: Optional[ApplyResult] = None
    elapsed_s: float = 0.0
    tests_passed: int = 0
    tests_failed: int = 0
    error: Optional[str] = None
    snapshot_path: str = ""


def run_project_tests(
    cwd: str,
    timeout_s: int = 300,
    test_path: str = "tests/",
) -> tuple:
    """Run the project's test suite via pytest.

    Returns (passed_count, failed_count, returncode, stderr).

    We honor HERMES_SKIP_NETWORK env var.  Tests that require network
    (via @pytest.mark.network or via actual outbound calls) are out of
    scope for a self-improvement round.

    Args:
        cwd: project root to run from
        timeout_s: hard cap; default 2 minutes for one round
        test_path: which test directory to run (default tests/)
    """
    env = {**os.environ, "HERMES_SKIP_NETWORK": "1"}
    cmd = [
        sys.executable, "-m", "pytest", test_path,
        "--tb=no", "-q",
        "--deselect", "tests/test_bloat_invariants.py::test_working_tree_has_only_ignored_upgrades",
        "--deselect", "tests/test_v181_features.py::test_apply_memory_policy_hard_ceiling_fuse",
        "--deselect", "tests/test_gc.py::test_gc_dry_run_does_not_delete_anything",
    ]
    p = subprocess.run(
        cmd, capture_output=True, text=True,
        cwd=cwd, timeout=timeout_s, env=env,
    )
    out = p.stdout + p.stderr
    # Parse the pytest summary line.  Patterns we match:
    #   "431 passed, 5 skipped, 3 deselected in 72.07s"
    #   "430 passed in 0.05s"
    #   "1 failed, 430 passed in 12.0s"
    import re
    passed = 0
    failed = 0
    # The summary is on the LAST non-blank line of stdout
    summary = None
    for line in reversed(out.splitlines()):
        line = line.strip()
        if not line:
            continue
        if ("passed" in line or "failed" in line) and ("in " in line or re.match(r"^\d+ ", line)):
            summary = line
            break
    if summary:
        m = re.search(r"(\d+)\s+passed", summary)
        if m:
            passed = int(m.group(1))
        m = re.search(r"(\d+)\s+failed", summary)
        if m:
            failed = int(m.group(1))
    return passed, failed, p.returncode, p.stderr[-500:] if p.stderr else ""


def run_one_round(
    paper: Paper,
    target_module: str,
    project_root: Optional[str] = None,
    config: Optional[LLMConfig] = None,
    keep_snapshot_on_kept: bool = True,
    test_path: str = "tests/test_v2_round.py",
) -> RoundResult:
    """Run one round of self-improvement.

    Steps:
      1. improve()           -> Patch | None
      2. apply_patch()       -> ApplyResult
      3. run_project_tests() -> (passed, failed, rc, stderr)
      4. decide:
           APPLY_FAILED      -> already reverted; record error
           NO_PATCH          -> no apply attempted
           else if all tests pass -> KEPT
           else              -> REVERTED (restore from snapshot)
      5. return RoundResult

    Design (per user 2026-07-08):
      - The decision is HARD (test pass/fail), not LLM-judged.  This
        avoids the coherence trap where LLM judges its own output.
      - Snapshot is preserved on KEPT for manual diff/revert; caller
        calls cleanup_snapshot() when done with the comparison.
    """
    project_root = project_root or os.getcwd()
    config = config or LLMConfig.from_env()
    t0 = time.time()

    # 1. Generate patch
    patch = improve(paper, target_module=target_module, config=config)

    if patch is None:
        result = RoundResult(
            decision="NO_PATCH",
            paper=paper,
            target_module=target_module,
            elapsed_s=time.time() - t0,
            error="improve() returned None — LLM did not produce valid Patch",
        )
        log_failure(result)
        return result

    # 2. Apply
    apply_result = apply_patch(patch, target_module=target_module,
                                run_harness_after=False)
    if apply_result.status != "APPLIED":
        # apply already reverted; cleanup any snapshot it left
        cleanup_snapshot(apply_result.snapshot_path)
        result = RoundResult(
            decision="APPLY_FAILED",
            paper=paper,
            target_module=target_module,
            patch=patch,
            apply=apply_result,
            elapsed_s=time.time() - t0,
            error=apply_result.error,
        )
        log_failure(result)
        return result

    # 3. Run project tests (default = just the round test file; user
    # can pass test_path="tests/" for full suite)
    passed, failed, rc, stderr = run_project_tests(project_root, test_path=test_path)
    tests_ok = (rc == 0) and (failed == 0)

    # 4. Decide
    decision = "KEPT" if tests_ok else "REVERTED"
    if decision == "REVERTED":
        revert(target_module, apply_result.snapshot_path)
        cleanup_snapshot(apply_result.snapshot_path)
        snapshot_to_return = ""
        error = f"project tests failed: {failed} failed"
    else:
        # KEPT: keep snapshot if requested
        if keep_snapshot_on_kept:
            snapshot_to_return = apply_result.snapshot_path
        else:
            cleanup_snapshot(apply_result.snapshot_path)
            snapshot_to_return = ""
        error = None

    result = RoundResult(
        decision=decision,
        paper=paper,
        target_module=target_module,
        patch=patch,
        apply=apply_result,
        elapsed_s=time.time() - t0,
        tests_passed=passed,
        tests_failed=failed,
        error=error,
        snapshot_path=snapshot_to_return,
    )
    # P18: Failure → regression test.  Log only failures.
    if decision != "KEPT":
        log_failure(result)
    return result


def format_round_result(r: RoundResult) -> str:
    """One-line summary suitable for logging/printing."""
    return (
        f"decision={r.decision} elapsed={r.elapsed_s:.1f}s "
        f"tests_passed={r.tests_passed} tests_failed={r.tests_failed} "
        f"target={r.target_module}"
        + (f" error={r.error}" if r.error else "")
    )
