"""Tests for A/B integration (per v3.3.0 sub-task 2/3).

Per 你 vision (self-upgrade agent 终极目标):
- 自动 KEPT/REJECT based on A/B data

Per LITERATURE Signal-to-Fix: real signals drive decisions.

Per 自上而下/分治:
- Big: v3.3.0 A/B benchmark
- Sub-task 1 (done): core comparison logic
- Sub-task 2 (this): integration with daily-loop
- Sub-task 3 (future): statistical significance

Per P18: regression tests required.
"""
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.ab_integration import (
    decide_round,
    daily_loop_with_ab,
    main,
)


class TestDecideRound:
    """Test A/B decision logic (per LITERATURE Signal-to-Fix)."""

    def test_decide_reject_unchanged(self):
        """REJECT decision -> stays REJECT (no A/B needed)."""
        r = {"decision": "REJECT", "reason": "patch broken"}
        decision, reason = decide_round(r)
        assert decision == "REJECT"
        assert reason == "patch broken"

    def test_decide_no_patch_unchanged(self):
        """NO_PATCH decision -> stays NO_PATCH."""
        r = {"decision": "NO_PATCH", "reason": "no improvement"}
        decision, reason = decide_round(r)
        assert decision == "NO_PATCH"

    def test_decide_kept_no_baseline(self):
        """KEPT without baseline -> stays KEPT."""
        r = {"decision": "KEPT", "tests_passed": 16}
        decision, reason = decide_round(r)
        assert decision == "KEPT"

    def test_decide_kept_ab_confirmed(self):
        """KEPT + A/B confirms -> stays KEPT."""
        r = {"decision": "KEPT", "tests_passed": 16}
        # Mock baseline + candidate metrics
        baseline = {"passed": 10, "failed": 0, "elapsed_sec": 1.0}
        # Patch candidate should have more passes
        with patch("src.ab_benchmark.run_tests") as mock_run:
            mock_run.return_value = {
                "passed": 12, "failed": 0,
                "elapsed_sec": 1.1, "success": True,
            }
            decision, reason = decide_round(
                r, baseline_metrics=baseline,
                test_path="tests/test_x.py", cwd=".")
        assert decision == "KEPT"
        assert "A/B confirmed" in reason

    def test_decide_kept_ab_regression_overrides(self):
        """KEPT + A/B regression -> REJECT (per 你 vision)."""
        r = {"decision": "KEPT", "tests_passed": 16}
        baseline = {"passed": 10, "failed": 0, "elapsed_sec": 1.0}
        # Patch candidate has fewer passes (regression)
        with patch("src.ab_benchmark.run_tests") as mock_run:
            mock_run.return_value = {
                "passed": 5, "failed": 5,
                "elapsed_sec": 1.0, "success": False,
            }
            decision, reason = decide_round(
                r, baseline_metrics=baseline,
                test_path="tests/test_x.py", cwd=".")
        assert decision == "REJECT"
        assert "A/B detected regression" in reason


class TestDailyLoopWithAB:
    """Test daily-loop + A/B integration."""

    def test_daily_loop_with_ab_basic(self, tmp_path):
        """daily_loop_with_ab: runs N rounds, A/B verifies KEPT."""
        path = tmp_path / "state.json"
        # Mock baseline metrics: 10 passes
        with patch("src.ab_benchmark.run_tests") as mock_run:
            mock_run.return_value = {
                "passed": 10, "failed": 0,
                "elapsed_sec": 1.0, "success": True,
            }
            def fake_round(idx):
                # All KEPT with 10 passes (matches baseline)
                return {"decision": "KEPT", "tests_passed": 10,
                        "target": "core/test"}
            result = daily_loop_with_ab(
                fake_round, max_rounds=3, interval=0,
                test_path="tests/test_x.py", cwd=str(tmp_path),
                state_path=path, enable_ab=True)
        assert result["rounds_run"] == 3
        # All KEPT (A/B confirms: same passes as baseline)
        assert result["kept_count"] == 3
        assert result["rejected_count"] == 0

    def test_daily_loop_with_ab_disabled(self, tmp_path):
        """daily_loop_with_ab: enable_ab=False skips A/B verification."""
        path = tmp_path / "state.json"
        def fake_round(idx):
            return {"decision": "KEPT", "tests_passed": 10}
        result = daily_loop_with_ab(
            fake_round, max_rounds=2, interval=0,
            state_path=path, enable_ab=False)
        assert result["rounds_run"] == 2
        assert result["kept_count"] == 2

    def test_daily_loop_with_ab_regression_caught(self, tmp_path):
        """daily_loop_with_ab: regression detected, REJECT instead of KEPT."""
        path = tmp_path / "state.json"
        with patch("src.ab_benchmark.run_tests") as mock_run:
            # Baseline: 10 passes
            # Candidate: 5 passes (regression)
            call_count = [0]
            def fake_run(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    # Baseline
                    return {"passed": 10, "failed": 0,
                            "elapsed_sec": 1.0, "success": True}
                else:
                    # Candidate
                    return {"passed": 5, "failed": 5,
                            "elapsed_sec": 1.0, "success": False}
            mock_run.side_effect = fake_run
            def fake_round(idx):
                return {"decision": "KEPT", "tests_passed": 10}
            result = daily_loop_with_ab(
                fake_round, max_rounds=2, interval=0,
                test_path="tests/test_x.py", cwd=str(tmp_path),
                state_path=path, enable_ab=True)
        # Regression detected: should be REJECT, not KEPT
        assert result["kept_count"] == 0
        assert result["rejected_count"] == 2

    def test_daily_loop_with_ab_failures_caught(self, tmp_path):
        """daily_loop_with_ab: exceptions become failures."""
        path = tmp_path / "state.json"
        with patch("src.ab_benchmark.run_tests") as mock_run:
            mock_run.return_value = {
                "passed": 10, "failed": 0,
                "elapsed_sec": 1.0, "success": True,
            }
            def fake_round(idx):
                if idx == 2:
                    raise ValueError("LLM failed")
                return {"decision": "KEPT", "tests_passed": 10}
            result = daily_loop_with_ab(
                fake_round, max_rounds=3, interval=0,
                test_path="tests/test_x.py", cwd=str(tmp_path),
                state_path=path, enable_ab=True)
        assert result["failures_count"] == 1
