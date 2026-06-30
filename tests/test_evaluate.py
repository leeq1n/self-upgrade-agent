"""Tests for src/evaluate.py"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.evaluate import (
    BenchmarkTask, BenchmarkResult, compute_statistics,
    compare_results, DEFAULT_TASKS,
    run_benchmark_trial, evaluate_skill,
)
from src.evaluate import LLMConfig


class TestBasicFunctions:
    def test_default_tasks_are_defined(self):
        assert len(DEFAULT_TASKS) >= 3

    def test_benchmark_task_creation(self):
        t = BenchmarkTask(id="t1", description="d", query="q", expected_output_pattern="p")
        assert t.id == "t1"

    def test_compute_statistics_empty(self):
        s = compute_statistics([])
        assert s["mean"] == 0.0

    def test_compute_statistics_values(self):
        s = compute_statistics([0.8, 0.85, 0.9])
        assert abs(s["mean"] - 0.85) < 0.001


class TestCompareResults:
    def test_detects_improvement(self):
        r = compare_results(0.80, 0.88, 1000, 1100, 0.05, 1.2)
        assert r["recommendation"] == "kept"

    def test_reverts_no_improvement(self):
        r = compare_results(0.80, 0.81, 1000, 1000, 0.05, 1.2)
        assert r["recommendation"] == "reverted"

    def test_reverts_cost_too_high(self):
        r = compare_results(0.80, 0.88, 1000, 2000, 0.05, 1.2)
        assert r["recommendation"] == "reverted"


@pytest.mark.llm
class TestLLMIntegration:
    """These tests call the actual LLM (requires .env with API key)."""

    def test_benchmark_returns_result_structure(self):
        task = DEFAULT_TASKS[0]
        result = run_benchmark_trial(task)
        assert isinstance(result, BenchmarkResult)
        assert result.task_id == task.id
        assert isinstance(result.success, bool)

    def test_benchmark_with_skill_context(self):
        task = DEFAULT_TASKS[0]
        result = run_benchmark_trial(task, skill_context="You are an expert planner.")
        assert isinstance(result.success, bool)

    def test_evaluate_without_skill(self):
        """evaluate_skill with empty string should produce baseline metrics."""
        config = type("Cfg", (), {"trials_per_test": 1})()
        results = evaluate_skill(skill_context="", tasks=DEFAULT_TASKS[:1], config=config)
        assert "baseline_success_rate" in results
        assert results["upgraded_success_rate"] == 0.0

    def test_evaluate_with_skill(self):
        """evaluate_skill with skill context should produce comparison."""
        config = type("Cfg", (), {"trials_per_test": 1,
            "min_success_rate_delta": 0.05, "max_cost_increase_ratio": 1.2})()
        results = evaluate_skill(
            skill_context="You are an expert in all domains.",
            tasks=DEFAULT_TASKS[:1],
            config=config,
        )
        assert "comparison" in results
        assert "recommendation" in results["comparison"]
