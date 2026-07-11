"""Tests for A/B benchmark (per LITERATURE Signal-to-Fix + v3.3.0).

Per 你 vision (self-upgrade agent 终极目标):
- 真能比较 patch vs baseline
- 决定 KEPT/REJECT based on data

Per 自上而下/分治:
- Big: v3.3.0 A/B benchmark
- Sub-task 1 (this): core comparison logic
- Sub-task 2 (future): integration with daily-loop
- Sub-task 3 (future): statistical significance

Per P18: regression tests required.
"""
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.ab_benchmark import (
    run_tests,
    _extract_count,
    compare_runs,
    benchmark,
    main,
)


class TestExtractCount:
    """Test pytest output parsing (per LITERATURE Signal-to-Fix)."""

    def test_extract_count_passed(self):
        """Extract '16 passed' from pytest output."""
        output = "===== 16 passed in 0.5s ====="
        assert _extract_count(output, "passed") == 16

    def test_extract_count_failed(self):
        """Extract '2 failed' from pytest output."""
        output = "===== 14 passed, 2 failed in 1.0s ====="
        assert _extract_count(output, "failed") == 2

    def test_extract_count_missing(self):
        """Missing key -> 0."""
        assert _extract_count("no output", "passed") == 0


class TestCompareRuns:
    """Test baseline vs candidate comparison logic."""

    def test_compare_candidate_better(self):
        """More passes -> candidate_better."""
        baseline = {"passed": 10, "failed": 0, "elapsed_sec": 1.0}
        candidate = {"passed": 12, "failed": 0, "elapsed_sec": 1.1}
        result = compare_runs(baseline, candidate)
        assert result["decision"] == "candidate_better"
        assert result["passed_delta"] == 2

    def test_compare_regression_fewer_passes(self):
        """Fewer passes -> regression."""
        baseline = {"passed": 10, "failed": 0, "elapsed_sec": 1.0}
        candidate = {"passed": 8, "failed": 0, "elapsed_sec": 1.0}
        result = compare_runs(baseline, candidate)
        assert result["decision"] == "regression"
        assert result["passed_delta"] == -2

    def test_compare_regression_more_failures(self):
        """Same passes but more failures -> regression."""
        baseline = {"passed": 10, "failed": 0, "elapsed_sec": 1.0}
        candidate = {"passed": 10, "failed": 2, "elapsed_sec": 1.0}
        result = compare_runs(baseline, candidate)
        assert result["decision"] == "regression"
        assert result["failed_delta"] == 2

    def test_compare_tie(self):
        """Same pass/fail counts -> tie."""
        baseline = {"passed": 10, "failed": 0, "elapsed_sec": 1.0}
        candidate = {"passed": 10, "failed": 0, "elapsed_sec": 1.5}
        result = compare_runs(baseline, candidate)
        assert result["decision"] == "tie"
        assert result["reason"] == "same pass/fail counts"

    def test_compare_latency_delta(self):
        """Latency delta tracked."""
        baseline = {"passed": 10, "failed": 0, "elapsed_sec": 1.0}
        candidate = {"passed": 10, "failed": 0, "elapsed_sec": 1.5}
        result = compare_runs(baseline, candidate)
        assert result["latency_delta_sec"] == 0.5


class TestRunTests:
    """Test run_tests integration with subprocess (mocked)."""

    def test_run_tests_success(self):
        """run_tests: success when rc=0."""
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="===== 10 passed in 1.0s =====", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            result = run_tests("tests/test_x.py", cwd=".")
        assert result["success"] is True
        assert result["passed"] == 10
        assert result["rc"] == 0

    def test_run_tests_failure(self):
        """run_tests: success=False when rc!=0."""
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=1,
            stdout="===== 5 passed, 2 failed in 1.0s =====", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            result = run_tests("tests/test_x.py", cwd=".")
        assert result["success"] is False
        assert result["passed"] == 5
        assert result["failed"] == 2
        assert result["rc"] == 1

    def test_run_tests_timeout(self):
        """run_tests: timeout returns error metrics."""
        with patch("subprocess.run",
                   side_effect=subprocess.TimeoutExpired("pytest", 120)):
            result = run_tests("tests/test_x.py", cwd=".", timeout=60)
        assert result["success"] is False
        assert result["rc"] == -1
        assert "error" in result


class TestBenchmark:
    """Test benchmark orchestration (real tests, single run)."""

    def test_benchmark_returns_candidate(self, tmp_path):
        """benchmark returns candidate metrics from current state."""
        # Use a real test file that passes
        test_file = tmp_path / "test_simple.py"
        test_file.write_text("def test_pass(): assert True\n")
        result = benchmark(test_path=str(test_file), cwd=str(tmp_path))
        assert "baseline" in result
        assert result["baseline"]["success"] is True
