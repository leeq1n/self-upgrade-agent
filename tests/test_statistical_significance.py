"""Tests for statistical significance (per v3.3.0 sub-task 3/3).

Per 你 vision (self-upgrade agent 终极目标):
- 真 autonomous KEPT/REJECT with confidence
- Statistical confidence, not gut-feel

Per LITERATURE Signal-to-Fix: multiple runs + t-test for confidence.

Per 自上而下/分治:
- Big: v3.3.0 A/B benchmark
- Sub-task 1 (done): core comparison
- Sub-task 2 (done): daily-loop integration
- Sub-task 3 (this): statistical significance

Per P18: regression tests required.
"""
import pytest

from src.statistical_significance import (
    run_multiple,
    compute_stats,
    welch_t_test,
    decide_with_significance,
    _approx_two_tail_p,
)


class TestRunMultiple:
    """Test N-run measurement (per LITERATURE multiple runs)."""

    def test_run_multiple_basic(self):
        """run_multiple: returns N samples."""
        counter = [0]
        def measure():
            counter[0] += 1
            return counter[0]
        samples = run_multiple(measure, n_runs=5)
        assert len(samples) == 5
        assert samples == [1, 2, 3, 4, 5]

    def test_run_multiple_n_runs(self):
        """run_multiple: respects n_runs."""
        def measure():
            return 10
        samples = run_multiple(measure, n_runs=10)
        assert len(samples) == 10


class TestComputeStats:
    """Test descriptive stats (per LITERATURE)."""

    def test_compute_stats_basic(self):
        """compute_stats: mean + stdev correct."""
        samples = [10.0, 10.0, 10.0, 10.0, 10.0]
        stats = compute_stats(samples)
        assert stats["mean"] == 10.0
        assert stats["stdev"] == 0.0
        assert stats["n"] == 5
        assert stats["sem"] == 0.0

    def test_compute_stats_with_variance(self):
        """compute_stats: variance > 0 -> stdev > 0."""
        samples = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = compute_stats(samples)
        assert stats["mean"] == 3.0
        assert stats["stdev"] > 0
        assert stats["n"] == 5
        assert stats["sem"] > 0

    def test_compute_stats_single_sample(self):
        """compute_stats: n=1 -> stdev=0 (no variance)."""
        stats = compute_stats([5.0])
        assert stats["mean"] == 5.0
        assert stats["stdev"] == 0
        assert stats["n"] == 1

    def test_compute_stats_empty(self):
        """compute_stats: empty list -> all zeros."""
        stats = compute_stats([])
        assert stats["mean"] == 0
        assert stats["n"] == 0


class TestWelchTTest:
    """Test Welch's t-test (per LITERATURE)."""

    def test_welch_t_test_significant_difference(self):
        """welch_t_test: clearly different samples -> p < 0.05."""
        baseline = [10.0] * 5
        candidate = [20.0] * 5
        result = welch_t_test(baseline, candidate)
        assert result["significant"] is True
        assert result["delta"] == 10.0
        assert result["p_value"] < 0.05

    def test_welch_t_test_no_difference(self):
        """welch_t_test: identical samples -> p ~ 1.0."""
        baseline = [10.0] * 5
        candidate = [10.0] * 5
        result = welch_t_test(baseline, candidate)
        # With zero variance, falls through to "zero variance" warning
        assert result["warning"] == "zero variance"
        assert result["significant"] is False

    def test_welch_t_test_small_difference(self):
            """welch_t_test: very small overlap -> not significant."""
            # Means differ by 0.1, high variance -> t small
            baseline = [10.0, 12.0, 9.0, 11.5, 8.5, 10.5, 9.5, 11.0]
            candidate = [10.1, 12.1, 9.1, 11.6, 8.6, 10.6, 9.6, 11.1]
            result = welch_t_test(baseline, candidate)
            # Not significant (tiny effect, high variance)
            assert result["significant"] is False

    def test_welch_t_test_insufficient_samples(self):
        """welch_t_test: n<2 -> warning + safe default."""
        result = welch_t_test([10.0], [10.0, 11.0])
        assert result["warning"] == "insufficient samples"
        assert result["significant"] is False


class TestDecideWithSignificance:
    """Test full decision logic (per LITERATURE Signal-to-Fix)."""

    def test_decide_significant_improvement(self):
        """decide_with_significance: clear improvement -> candidate_better."""
        baseline = [10.0, 10.1, 9.9, 10.2, 9.8]
        candidate = [15.0, 14.8, 15.2, 14.9, 15.1]
        result = decide_with_significance(baseline, candidate,
                                          higher_is_better=True)
        assert result["decision"] == "candidate_better"
        assert result["significant"] is True

    def test_decide_significant_regression(self):
        """decide_with_significance: clear regression -> regression."""
        baseline = [15.0, 14.8, 15.2, 14.9, 15.1]
        candidate = [10.0, 10.1, 9.9, 10.2, 9.8]
        result = decide_with_significance(baseline, candidate,
                                          higher_is_better=True)
        assert result["decision"] == "regression"

    def test_decide_no_significant_difference(self):
            """decide_with_significance: tiny effect, high variance -> tie."""
            baseline = [10.0, 12.0, 9.0, 11.5, 8.5, 10.5, 9.5, 11.0]
            candidate = [10.1, 12.1, 9.1, 11.6, 8.6, 10.6, 9.6, 11.1]
            result = decide_with_significance(baseline, candidate,
                                              higher_is_better=True)
            assert result["decision"] == "tie"
            assert result["significant"] is False

    def test_decide_lower_is_better(self):
        """decide_with_significance: lower_is_better (e.g. latency)."""
        # Higher latency = worse, so lower candidate is better
        baseline = [10.0] * 5  # baseline = 10s
        candidate = [5.0] * 5  # candidate = 5s (faster = better)
        result = decide_with_significance(baseline, candidate,
                                          higher_is_better=False)
        assert result["decision"] == "candidate_better"


class TestApproxPValue:
    """Test p-value approximation (per LITERATURE conservative approach)."""

    def test_approx_p_value_large_t(self):
        """Large |t| -> very small p."""
        p = _approx_two_tail_p(5.0, 100)
        assert p < 0.01

    def test_approx_p_value_zero_t(self):
        """|t| = 0 -> p ~ 1 (no difference)."""
        p = _approx_two_tail_p(0.0, 100)
        assert p > 0.9

    def test_approx_p_value_bounded(self):
        """p is always in [0, 1]."""
        for t in [-10, -5, -1, 0, 1, 5, 10]:
            for df in [2, 5, 10, 100]:
                p = _approx_two_tail_p(t, df)
                assert 0 <= p <= 1.0
