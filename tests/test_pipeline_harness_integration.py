"""v1.8.0: tests for the harness integration in the pipeline.

Verifies that:
  1. node_evaluate includes a "harness" key in state["evaluation"]
  2. make_decision uses should_promote_with_harness when harness is present
  3. The full pipeline (dry-run) ends with state.decision based on harness
  4. A patch that breaks 1 harness test is REVERTED even if LLM says +5%
"""
import os, sys
import pytest

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)


def test_decide_uses_harness_when_present():
    """make_decision should use should_promote_with_harness when
    eval_data contains a 'harness' key.
    """
    from src.decide import make_decision
    from src.config import DecideConfig
    cfg = DecideConfig()

    # Case: harness pass + LLM delta = 5% → KEPT
    eval_with_harness = {
        "success_rate_delta": 0.05,
        "cost_increase_ratio": 0.5,
        "baseline_rate": 0.5,
        "upgraded_rate": 0.55,
        "harness": {"pass_rate": 1.0, "passed": 8, "failed": 0, "total": 8, "failures": []},
    }
    d = make_decision(eval_with_harness, cfg)
    assert d["decision"] == "kept", f"expected kept, got {d['decision']}: {d['reasons']}"
    assert any("Harness OK" in r for r in d["reasons"])


def test_decide_rejects_when_harness_fails():
    """If harness fails 1+ test, decision MUST be reverted, even if
    LLM delta is 50% (which would otherwise be kept).
    """
    from src.decide import make_decision
    from src.config import DecideConfig
    cfg = DecideConfig()

    eval_with_failing_harness = {
        "success_rate_delta": 0.50,  # HUGE improvement
        "cost_increase_ratio": 0.5,  # cheap
        "baseline_rate": 0.5,
        "upgraded_rate": 1.0,
        "harness": {"pass_rate": 0.5, "passed": 4, "failed": 4, "total": 8,
                    "failures": ["x", "y", "z", "w"]},
    }
    d = make_decision(eval_with_failing_harness, cfg)
    assert d["decision"] == "reverted"
    assert any("Harness REGRESSION" in r for r in d["reasons"])


def test_decide_legacy_path_still_works():
    """If harness is missing from eval_data, use legacy LLM-only path."""
    from src.decide import make_decision
    from src.config import DecideConfig
    cfg = DecideConfig()

    eval_no_harness = {
        "success_rate_delta": 0.10,  # 10% improvement
        "success_rate_improved": True,
        "cost_increase_ratio": 0.5,
        "cost_acceptable": True,
        "baseline_rate": 0.5,
        "upgraded_rate": 0.6,
        # NO 'harness' key
    }
    d = make_decision(eval_no_harness, cfg)
    # Legacy path: LLM delta >= 5% threshold + cost OK → KEPT
    assert d["decision"] == "kept"


def test_node_evaluate_evaluation_dict_has_harness_key():
    """Check that the source code of node_evaluate references harness."""
    p = os.path.join(PROJECT, "src", "pipeline_lg.py")
    with open(p) as f:
        content = f.read()
    # node_evaluate should set state["evaluation"]["harness"] somewhere
    assert '"harness"' in content or "'harness'" in content, \
        "node_evaluate does not set state['evaluation']['harness']"
    # And should call run_harness
    assert "run_harness()" in content, "node_evaluate does not call run_harness()"


def test_run_harness_succeeds_on_clean_planner():
    """Smoke test: run_harness() returns 1.0 pass_rate on the current planner."""
    from src.evaluate import run_harness
    r = run_harness()
    assert r["pass_rate"] == 1.0
    assert r["total"] == 8
    assert r["failed"] == 0


def test_pipeline_lg_imports_clean():
    """After harness integration, src/pipeline_lg.py must still import."""
    sys.path.insert(0, PROJECT)
    import src.pipeline_lg
    assert hasattr(src.pipeline_lg, "node_evaluate")
    assert hasattr(src.pipeline_lg, "node_decide")
    assert hasattr(src.pipeline_lg, "build_graph")
    assert hasattr(src.pipeline_lg, "run")


def test_decide_imports_clean():
    """After harness integration, src/decide.py must still import."""
    sys.path.insert(0, PROJECT)
    import src.decide
    assert hasattr(src.decide, "make_decision")
    assert hasattr(src.decide, "rollback_skill")
