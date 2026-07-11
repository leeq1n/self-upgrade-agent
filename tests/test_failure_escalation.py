"""Tests for failure escalation (per v4.0.0 sub-task 3/3).

Per 你 vision 2026-07-08 '我希望这个项目之后可以自己独立运行':
- True autonomous, but with visibility

Per 自上而下/分治:
- Big: SA v4.0.0 cron execution
- Sub-task 1 done (cron logic)
- Sub-task 2 done (OS integration)
- Sub-task 3 (this): failure escalation (LAST)

Per P18: regression tests required.
"""
import json
from pathlib import Path

import pytest

from src.failure_escalation import (
    compute_backoff_seconds,
    FailureTracker,
)


class TestComputeBackoff:
    """Test exponential backoff calculation (per Nate Berkopec)."""

    def test_zero_failures(self):
        """compute_backoff_seconds: 0 failures -> 0 seconds."""
        assert compute_backoff_seconds(0) == 0

    def test_one_failure(self):
        """compute_backoff_seconds: 1 failure -> base."""
        assert compute_backoff_seconds(1, base=60) == 60

    def test_exponential_growth(self):
        """compute_backoff_seconds: exponential growth."""
        # 60, 120, 240, 480
        assert compute_backoff_seconds(1, base=60) == 60
        assert compute_backoff_seconds(2, base=60) == 120
        assert compute_backoff_seconds(3, base=60) == 240
        assert compute_backoff_seconds(4, base=60) == 480

    def test_max_cap(self):
        """compute_backoff_seconds: max delay cap."""
        # base=60, max=3600 -> cap at 3600
        assert compute_backoff_seconds(20, base=60, max_delay=3600) == 3600

    def test_custom_base(self):
        """compute_backoff_seconds: custom base."""
        assert compute_backoff_seconds(2, base=30) == 60


class TestFailureTracker:
    """Test failure tracker (per LITERATURE Signal-to-Fix)."""

    def test_initial_state(self):
        """FailureTracker: initial state has 0 failures."""
        tracker = FailureTracker()
        assert tracker.consecutive_failures == 0
        assert tracker.total_failures == 0

    def test_record_failure_increments(self):
        """FailureTracker: record_failure increments counters."""
        tracker = FailureTracker()
        result = tracker.record_failure("test error")
        assert tracker.consecutive_failures == 1
        assert tracker.total_failures == 1
        assert result["consecutive_failures"] == 1

    def test_record_success_resets_consecutive(self):
        """FailureTracker: record_success resets consecutive (not total)."""
        tracker = FailureTracker()
        tracker.record_failure("e1")
        tracker.record_failure("e2")
        tracker.record_success()
        assert tracker.consecutive_failures == 0
        assert tracker.total_failures == 2  # total NOT reset

    def test_action_continue_for_first_failure(self):
        """FailureTracker: action=continue for first failure."""
        tracker = FailureTracker(max_consecutive=3)
        result = tracker.record_failure("e1")
        assert result["action"] == "continue"

    def test_action_backoff_for_intermediate(self):
        """FailureTracker: action=backoff for 2nd failure."""
        tracker = FailureTracker(max_consecutive=3)
        tracker.record_failure("e1")
        result = tracker.record_failure("e2")
        assert result["action"] == "backoff"

    def test_action_alert_at_threshold(self):
        """FailureTracker: action=alert at max_consecutive threshold."""
        tracker = FailureTracker(max_consecutive=3)
        tracker.record_failure("e1")
        tracker.record_failure("e2")
        result = tracker.record_failure("e3")
        assert result["action"] == "alert"

    def test_alert_logged_to_file(self, tmp_path):
        """FailureTracker: alert written to alert_log_path."""
        log_path = tmp_path / "alerts.jsonl"
        tracker = FailureTracker(max_consecutive=2,
                                 alert_log_path=log_path)
        tracker.record_failure("e1")
        tracker.record_failure("e2")  # triggers alert
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert "alert" in content

    def test_state_persistence(self, tmp_path):
        """FailureTracker: state persists across instances (per P19)."""
        state_path = tmp_path / "state.json"
        t1 = FailureTracker(state_path=state_path)
        t1.record_failure("e1")
        t1.record_failure("e2")
        # New instance loads from state
        t2 = FailureTracker(state_path=state_path)
        assert t2.consecutive_failures == 2
        assert t2.total_failures == 2

    def test_get_status(self):
        """FailureTracker: get_status returns dict."""
        tracker = FailureTracker()
        tracker.record_failure("e1")
        status = tracker.get_status()
        assert status["consecutive_failures"] == 1
        assert status["total_failures"] == 1
        assert status["last_failure_at"] is not None