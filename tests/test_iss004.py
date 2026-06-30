"""Tests for ISS-004: a single A/B evaluation path.

Before v1.5.1, ``pipeline_lg.node_evaluate`` and ``src.skill_lifecycle``
(``evaluate_all_skills``) both ran A/B benchmarks but via two
independent code paths.  They drifted: same patch, two different
success rates.

v1.5.1 makes ``src.evaluate.evaluate_skill`` a thin wrapper over
``src.benchmark.run_all``, and ``node_evaluate`` imports
``src.evaluate.compare_results`` for the compare step.  These tests
verify that the two paths can't drift again.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestSingleEvaluationPath:
    """``src.evaluate`` must delegate to ``src.benchmark``."""

    def test_evaluate_skill_calls_benchmark_run_all(self, monkeypatch):
        """evaluate_skill must call benchmark.run_all (not implement
        its own task loop).  This is the whole point of ISS-004."""
        from src import evaluate, benchmark

        called = {"n": 0}
        original_run_all = benchmark.run_all

        def fake_run_all(tasks, llm_config=None, verbose=False, skill_context=""):
            called["n"] += 1
            # Return a valid aggregate that downstream code expects.
            return {
                "results": [
                    {"task_id": "t1", "success": True, "elapsed": 0.1},
                    {"task_id": "t2", "success": False, "elapsed": 0.1},
                ],
                "total": 2,
                "successes": 1,
                "success_rate": 0.5,
                "categories": {},
            }

        monkeypatch.setattr(benchmark, "run_all", fake_run_all)
        # Also patch the import inside src.evaluate if needed.
        import src.benchmark as bm
        monkeypatch.setattr(bm, "run_all", fake_run_all)

        # Run evaluate_skill with no skill context — should still
        # call run_all (the baseline arm).
        result = evaluate.evaluate_skill(
            skill_context="",
            tasks=[{"id": "t1", "task": "x", "category": "x"},
                   {"id": "t2", "task": "x", "category": "x"}],
            llm_config=None,
        )
        assert called["n"] >= 1, "evaluate_skill did not call benchmark.run_all"

    def test_node_evaluate_uses_src_evaluate_compare_results(self):
        """pipeline_lg.node_evaluate must import compare_results from
        src.evaluate (not benchmark.compare), so the two paths
        use the same compare function."""
        from src import pipeline_lg
        src = open(pipeline_lg.__file__, encoding="utf-8").read()
        evaluate_start = src.find("def node_evaluate(")
        evaluate_end = src.find("\ndef ", evaluate_start + 1)
        evaluate_body = src[evaluate_start:evaluate_end]
        # Must import compare_results from src.evaluate
        assert "from src.evaluate import compare_results" in evaluate_body
        # Must not import benchmark.compare (renamed to bench_compare
        # in the legacy import).
        assert "from src.benchmark import compare" not in evaluate_body
        assert "bench_compare" not in evaluate_body

    def test_evaluate_skill_signature_preserved(self):
        """Backward compat: skill_lifecycle.py calls evaluate_skill
        with these exact kwargs.  Don't change them without updating
        that caller too."""
        import inspect
        from src.evaluate import evaluate_skill
        sig = inspect.signature(evaluate_skill)
        params = list(sig.parameters.keys())
        # Must accept these kwargs (order can vary, but names matter)
        for expected in ["skill_context", "tasks", "config", "llm_config"]:
            assert expected in params, f"missing param: {expected}"

    def test_compute_statistics_unchanged(self):
        """compute_statistics has a separate test file already; we
        only verify it's still importable + still returns the same
        shape."""
        from src.evaluate import compute_statistics
        result = compute_statistics([0.8, 0.85, 0.9])
        assert result["mean"] == round((0.8 + 0.85 + 0.9) / 3, 4)
        assert "min" in result and "max" in result and "stdev" in result

    def test_compare_results_unchanged(self):
        """compare_results is called by decide.py.  Don't change the
        return shape."""
        from src.evaluate import compare_results
        result = compare_results(0.8, 0.9, 100, 110, min_delta=0.05, max_cost_ratio=1.2)
        # Decision: delta = 0.1, cost_ratio = 1.1.  Both pass thresholds.
        assert result["recommendation"] == "kept"
        assert result["success_rate_delta"] == 0.1
        assert result["cost_increase_ratio"] == 1.1


class TestBenchmarkCompareIsUnusedByNodeEvaluate:
    """After ISS-004, node_evaluate no longer imports benchmark.compare
    (renamed bench_compare) directly.  This test guards against
    accidental regression."""

    def test_node_evaluate_does_not_use_bench_compare(self):
        from src import pipeline_lg
        src = open(pipeline_lg.__file__, encoding="utf-8").read()
        evaluate_start = src.find("def node_evaluate(")
        evaluate_end = src.find("\ndef ", evaluate_start + 1)
        evaluate_body = src[evaluate_start:evaluate_end]
        # bench_compare is the OLD name.  We use _eval_compare now.
        assert "bench_compare" not in evaluate_body
