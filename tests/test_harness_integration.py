"""v1.8.0: tests for the harness integration.

These verify run_harness() and should_promote_with_harness().
"""
import os, sys
import pytest

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)


def test_run_harness_returns_valid_dict():
    """run_harness() must return a dict with the expected keys."""
    from src.evaluate import run_harness
    result = run_harness()
    assert isinstance(result, dict)
    for key in ("pass_rate", "passed", "failed", "total", "failures"):
        assert key in result, f"missing key: {key}"
    assert 0.0 <= result["pass_rate"] <= 1.0
    assert result["passed"] + result["failed"] == result["total"]


def test_run_harness_passes_on_clean_planner():
    """The current core/planner.py should pass all 8 harness tests."""
    from src.evaluate import run_harness
    result = run_harness()
    assert result["pass_rate"] == 1.0, (
        f"expected 100% pass, got {result['pass_rate']:.1%} "
        f"({result['failed']} failed: {result['failures']})"
    )
    assert result["total"] == 8, f"expected 8 tests, got {result['total']}"


def test_should_promote_with_harness_rejects_low_harness():
    """If harness fails, decision is REVERTED regardless of LLM score."""
    from src.evaluate import should_promote_with_harness

    # Mock: 3/8 tests pass (37.5%), LLM says +10% improvement
    harness = {"pass_rate": 0.375, "passed": 3, "failed": 5, "total": 8,
                "failures": ["test_a", "test_b", "test_c", "test_d", "test_e"]}
    llm_eval = {"success_rate_delta": 0.10, "cost_increase_ratio": 0.5}

    decision, reasons = should_promote_with_harness(harness, llm_eval)
    assert decision == "reverted"
    assert any("Harness REGRESSION" in r for r in reasons)


def test_should_promote_with_harness_accepts_good():
    """All conditions met: harness 100%, LLM delta >= 5%, cost <= 1.2x → KEPT."""
    from src.evaluate import should_promote_with_harness

    harness = {"pass_rate": 1.0, "passed": 8, "failed": 0, "total": 8,
                "failures": []}
    llm_eval = {"success_rate_delta": 0.10, "cost_increase_ratio": 0.5}

    decision, reasons = should_promote_with_harness(harness, llm_eval)
    assert decision == "kept"
    assert any("meets threshold" in r for r in reasons)


def test_should_promote_with_harness_rejects_low_delta():
    """harness 100% but LLM delta < 5% → REVERTED (LLM is the secondary signal)."""
    from src.evaluate import should_promote_with_harness

    harness = {"pass_rate": 1.0, "passed": 8, "failed": 0, "total": 8, "failures": []}
    llm_eval = {"success_rate_delta": 0.02, "cost_increase_ratio": 0.5}

    decision, reasons = should_promote_with_harness(harness, llm_eval)
    assert decision == "reverted"
    assert any("below minimum" in r for r in reasons)


def test_should_promote_with_harness_rejects_high_cost():
    """harness 100% + LLM delta OK but cost > 1.2x → REVERTED."""
    from src.evaluate import should_promote_with_harness

    harness = {"pass_rate": 1.0, "passed": 8, "failed": 0, "total": 8, "failures": []}
    llm_eval = {"success_rate_delta": 0.10, "cost_increase_ratio": 1.5}

    decision, reasons = should_promote_with_harness(harness, llm_eval)
    assert decision == "reverted"
    assert any("Cost increase" in r for r in reasons)


def test_should_promote_with_harness_legacy_mode():
    """If require_harness=False, behavior is legacy (LLM only)."""
    from src.evaluate import should_promote_with_harness

    # Even with broken harness, decision goes by LLM
    harness = {"pass_rate": 0.0, "passed": 0, "failed": 8, "total": 8, "failures": ["x"]}
    llm_eval = {"success_rate_delta": 0.10, "cost_increase_ratio": 0.5}

    decision, _ = should_promote_with_harness(
        harness, llm_eval, require_harness=False,
    )
    assert decision == "kept"
