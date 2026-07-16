"""Tests for failure recovery (per v3.1.2 sub-task 2/3).

Per 你 vision (autonomous agent):
- Cross-process recovery from last persisted state
- Exponential backoff + jitter (per Nate Berkopec)

Per 自上而下/分治:
- Big: v3.1.2 daily-loop persistence
- Sub-task 1 (done): state.json
- Sub-task 2 (this): failure recovery
- Sub-task 3 (future): integration with daily-loop

Per P18: regression tests.
"""
import json
import time
from pathlib import Path

import pytest

from src.failure_recovery import (
    compute_backoff_delay,
    should_retry,
    mark_failure,
    get_failure_count,
    get_all_failures,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_BASE_DELAY_SEC,
    DEFAULT_MAX_DELAY_SEC,
)


class TestBackoff:
    """Per Nate Berkopec: exponential backoff with jitter."""

    def test_backoff_exponential_growth(self):
        """Each attempt doubles the delay (until cap)."""
        d1 = compute_backoff_delay(1, base_delay=1.0, max_delay=100.0,
                                   jitter_seed=42)
        d2 = compute_backoff_delay(2, base_delay=1.0, max_delay=100.0,
                                   jitter_seed=42)
        d3 = compute_backoff_delay(3, base_delay=1.0, max_delay=100.0,
                                   jitter_seed=42)
        # Within +/-10% jitter, expect d2 ~ 2*d1, d3 ~ 4*d1
        assert 1.8 <= d2 / d1 <= 2.2
        assert 3.6 <= d3 / d1 <= 4.4

    def test_backoff_respects_max_delay(self):
        """Backoff caps at max_delay."""
        # attempt 10 with base 1, no cap -> 512s
        # with max 5s -> 5s
        d = compute_backoff_delay(10, base_delay=1.0, max_delay=5.0,
                                  jitter_seed=42)
        # Should be <= 5 + jitter (5.5)
        assert d <= 6.0

    def test_backoff_zero_attempt(self):
        """attempt < 1 returns 0."""
        assert compute_backoff_delay(0, jitter_seed=42) == 0

    def test_backoff_deterministic_with_seed(self):
        """Same jitter_seed -> same delay (testable)."""
        d1 = compute_backoff_delay(3, base_delay=1.0, jitter_seed=123)
        d2 = compute_backoff_delay(3, base_delay=1.0, jitter_seed=123)
        assert d1 == d2

    def test_backoff_jitter_present(self):
        """Without seed, jitter still within +/- 10%."""
        d = compute_backoff_delay(2, base_delay=1.0, max_delay=100.0)
        # d ~ 2 (with +/- 10% jitter)
        assert 1.7 <= d <= 2.3


class TestRetry:
    """Per Nate Berkopec: retry policy."""

    def test_should_retry_under_max(self):
        """Under max attempts -> retry."""
        assert should_retry(1, max_attempts=5) is True
        assert should_retry(4, max_attempts=5) is True

    def test_should_retry_at_max(self):
        """At max attempts -> no retry."""
        assert should_retry(5, max_attempts=5) is False
        assert should_retry(10, max_attempts=5) is False


class TestFailureMarking:
    """Per P19: persist failure for observability."""

    def test_mark_failure_persists(self, tmp_path):
        """mark_failure: persists error to state.json."""
        path = tmp_path / "state.json"
        # Initialize empty state
        from src.state_persistence import save_state
        save_state({"rounds": {}, "failures": {}}, path)
        mark_failure(5, "patch failed", state_path=path)
        from src.state_persistence import load_state
        state = load_state(path)
        assert "5" in state["failures"]
        assert state["failures"]["5"]["error"] == "patch failed"
        assert "timestamp" in state["failures"]["5"]

    def test_mark_failure_multiple_rounds(self, tmp_path):
        """mark_failure: multiple rounds tracked separately."""
        path = tmp_path / "state.json"
        from src.state_persistence import save_state
        save_state({"rounds": {}, "failures": {}}, path)
        mark_failure(0, "err1", state_path=path)
        mark_failure(1, "err2", state_path=path)
        mark_failure(2, "err3", state_path=path)
        failures = get_all_failures(state_path=path)
        assert len(failures) == 3
        assert failures["0"]["error"] == "err1"
        assert failures["2"]["error"] == "err3"

    def test_get_failure_count_specific(self, tmp_path):
        """get_failure_count: count failures for specific round."""
        path = tmp_path / "state.json"
        mark_failure(3, "err", state_path=path)
        assert get_failure_count(3, state_path=path) >= 1
        assert get_failure_count(99, state_path=path) == 0

    def test_get_failure_count_empty(self, tmp_path):
        """get_failure_count: missing state -> 0."""
        path = tmp_path / "missing.json"
        assert get_failure_count(0, state_path=path) == 0

    def test_get_all_failures_empty(self, tmp_path):
        """get_all_failures: missing state -> {}."""
        path = tmp_path / "missing.json"
        assert get_all_failures(state_path=path) == {}
