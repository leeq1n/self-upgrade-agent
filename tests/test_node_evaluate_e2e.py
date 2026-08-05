"""v1.8.0 Day 3: end-to-end test for node_evaluate harness integration.

Two paths:
  1. dry_run=True: simulated data, harness = 1.0
  2. dry_run=False with trivial patch: real run_harness() runs pytest
     in a subprocess while the patch is applied to core/planner.py.

The second path is the REAL one — it proves the harness actually
executes the 8 unit tests against a (trivially) patched planner.
"""
import os, sys, shutil, hashlib, subprocess
import pytest

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)


def _pre_md5():
    return hashlib.md5(open(os.path.join(PROJECT, "core", "planner.py"), "rb").read()).hexdigest()


def test_node_evaluate_dry_run_sets_harness():
    """dry_run path: state['evaluation']['harness'] must be present
    and reflect 8/8 pass (simulated)."""
    from src.config import load_config
    import src.pipeline_lg as plg
    cfg = load_config("config.yaml")
    state = {"config": cfg, "dry_run": True, "patch": {}, "errors": []}
    result = plg.node_evaluate(state)
    ev = result["evaluation"]
    assert "harness" in ev
    h = ev["harness"]
    assert h["pass_rate"] == 1.0
    assert h["total"] == 8
    assert h["failed"] == 0


def test_node_evaluate_real_calls_run_harness_mocked():
    """Non-dry-run path with MOCKED benchmark: verify that the real
    run_harness() is called and the harness result is included in
    state['evaluation'].

    We mock src.benchmark.run_all to avoid real LLM calls — this test
    proves the integration shape, not the LLM correctness.  The real
    LLM end-to-end test is Day 3.3 (separate run).
    """
    from unittest.mock import patch as mock_patch
    from src.config import load_config
    import src.pipeline_lg as plg

    cfg = load_config("config.yaml")
    trivial_patch = open(os.path.join(PROJECT, "core", "planner.py"), encoding="utf-8").read()

    state = {
        "config": cfg,
        "dry_run": False,
        "patch": {"function": trivial_patch, "test": "pass", "module": "planner.py"},
        "errors": [],
    }

    # Mock run_all to return 100% success (no LLM calls)
    mock_run_all = lambda tasks, llm_config=None, skill_context="": {
        "success_rate": 1.0, "successes": 21, "total": 21,
        "results": [{"success": True, "elapsed": 0.0} for _ in range(21)],
    }
    mock_load = lambda: [{"id": f"t{i}", "task": "x"} for i in range(21)]

    pre_md5 = _pre_md5()
    with mock_patch("src.benchmark.run_all", mock_run_all), \
         mock_patch("src.benchmark.load_tasks", mock_load):
        try:
            result = plg.node_evaluate(state)
        finally:
            post_md5 = _pre_md5()
            if pre_md5 != post_md5:
                subprocess.run(
                    ["git", "checkout", "HEAD", "--", "core/planner.py"],
                    cwd=PROJECT, capture_output=True,
                )

    ev = result["evaluation"]
    assert "harness" in ev, f"harness missing from real path: {list(ev.keys())}"
    h = ev["harness"]
    assert h["pass_rate"] == 1.0, f"expected 100%% pass on trivial patch, got {h}"
    assert h["total"] == 8


def test_node_evaluate_real_no_patch_returns_early():
    """If patch is empty, node_evaluate returns state without writing
    state['evaluation'] — but state['evaluation']['harness'] should not
    exist (no patch = no real evaluation)."""
    from src.config import load_config
    import src.pipeline_lg as plg
    cfg = load_config("config.yaml")
    state = {"config": cfg, "dry_run": False, "patch": {}, "errors": []}
    result = plg.node_evaluate(state)
    # With no patch, the early-return path runs and state is unchanged
    # (state['evaluation'] is whatever the caller set, or missing)
    assert result is state  # same dict, no copy


def test_pipeline_lg_safety_net_works():
    """Verify the v1.7.1 _safety_restore_planner works on a fake corruption."""
    import src.pipeline_lg as plg
    pre_md5 = _pre_md5()
    # Manually corrupt planner.py
    p = os.path.join(PROJECT, "core", "planner.py")
    with open(p, "r+b") as f:
        f.write(b"# corrupted\n")
    corrupted = hashlib.md5(open(p, "rb").read()).hexdigest()
    assert corrupted != pre_md5
    # Run safety restore
    restored = plg._safety_restore_planner()
    assert restored, "safety restore returned False"
    # Verify restored
    post_md5 = _pre_md5()
    assert post_md5 == pre_md5, f"safety restore failed: {pre_md5} != {post_md5}"
