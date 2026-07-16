"""Tests for cron scheduler (per SA v4.0.0).

Per 你 vision 2026-07-08 '我希望这个项目之后可以自己独立运行':
- True autonomous deployment via cron

Per 自上而下/分治:
- Big: SA v4.0.0 cron execution
- Sub-task 1 (this): cron logic + CLI
- Sub-task 2-3 (future): OS cron integration + escalation

Per P18: regression tests required.
"""
import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.cron_scheduler import (
    parse_cron,
    seconds_until_next,
    should_run_now,
    schedule_loop,
)


class TestParseCron:
    """Test cron expression parser (per LITERATURE minimal cron)."""

    def test_parse_valid(self):
        """parse_cron: '2 0' -> {hour: 2, minute: 0}."""
        result = parse_cron("2 0")
        assert result == {"hour": 2, "minute": 0}

    def test_parse_valid_zero_padded(self):
        """parse_cron: '02 00' -> {hour: 2, minute: 0}."""
        result = parse_cron("02 00")
        assert result == {"hour": 2, "minute": 0}

    def test_parse_invalid_format(self):
        """parse_cron: missing parts -> None."""
        assert parse_cron("2") is None
        assert parse_cron("") is None
        assert parse_cron(None) is None

    def test_parse_invalid_hour(self):
        """parse_cron: hour > 23 -> None."""
        assert parse_cron("25 0") is None
        assert parse_cron("-1 0") is None

    def test_parse_invalid_minute(self):
        """parse_cron: minute > 59 -> None."""
        assert parse_cron("0 60") is None
        assert parse_cron("0 -1") is None

    def test_parse_non_integer(self):
        """parse_cron: non-integer -> None."""
        assert parse_cron("a b") is None
        assert parse_cron("2.5 0") is None


class TestSecondsUntilNext:
    """Test seconds-until-next calculation."""

    def test_seconds_future_today(self):
        """seconds_until_next: future today -> delta seconds."""
        now = datetime.datetime(2026, 7, 11, 10, 0, 0)
        # Next 14:00 today = 4 hours = 14400 seconds
        secs = seconds_until_next(14, 0, now=now)
        assert secs == 4 * 3600

    def test_seconds_past_today_rolls_to_tomorrow(self):
        """seconds_until_next: past today -> rolls to tomorrow."""
        now = datetime.datetime(2026, 7, 11, 14, 0, 0)
        # Next 10:00 already passed, so tomorrow
        secs = seconds_until_next(10, 0, now=now)
        # 24 - 4 = 20 hours = 72000 seconds
        assert secs == 20 * 3600

    def test_seconds_now_match(self):
        """seconds_until_next: now matches -> 0 (next occurrence)."""
        now = datetime.datetime(2026, 7, 11, 14, 0, 0)
        secs = seconds_until_next(14, 0, now=now)
        # 0 <= target (would be today 14:00 = now), so roll to tomorrow
        assert secs == 24 * 3600


class TestShouldRunNow:
    """Test should_run_now check."""

    def test_should_run_at_target(self):
        """should_run_now: at target time -> True."""
        now = datetime.datetime(2026, 7, 11, 14, 0, 0)
        assert should_run_now("14 0", now=now) is True

    def test_should_not_run_off_target(self):
        """should_run_now: off target -> False."""
        now = datetime.datetime(2026, 7, 11, 10, 0, 0)
        assert should_run_now("14 0", now=now) is False

    def test_should_run_invalid(self):
        """should_run_now: invalid expr -> False."""
        now = datetime.datetime(2026, 7, 11, 14, 0, 0)
        assert should_run_now("invalid", now=now) is False


class TestScheduleLoop:
    """Test schedule_loop with mocked time + daily-loop."""

    def test_schedule_loop_one_iteration(self, tmp_path):
        """schedule_loop: max_iterations=1 runs 1 time then exits."""
        path = tmp_path / "state.json"
        # Mock time.sleep to avoid real wait
        with patch("src.cron_scheduler.time.sleep") as mock_sleep:
            # Mock daily_loop_persisted to return immediately
            with patch("src.daily_loop_integration.daily_loop_persisted") as mock_loop:
                mock_loop.return_value = {"rounds_run": 1, "kept_count": 1,
                                          "failures_count": 0}
                def fake_round(idx):
                    return {"decision": "KEPT", "tests_passed": 16}
                result = schedule_loop(fake_round, cron_expr="14 0",
                                        max_iterations=1, state_path=path)
        assert result["runs_completed"] == 1
        assert result["last_run_at"] is not None
        # Sleep was called (waiting for next occurrence)
        assert mock_sleep.called

    def test_schedule_loop_invalid_cron(self):
        """schedule_loop: invalid cron -> ValueError."""
        with pytest.raises(ValueError):
            schedule_loop(lambda i: {}, cron_expr="invalid")

    def test_schedule_loop_keyboard_interrupt(self, tmp_path):
        """schedule_loop: KeyboardInterrupt handled gracefully."""
        path = tmp_path / "state.json"
        with patch("src.cron_scheduler.time.sleep",
                   side_effect=KeyboardInterrupt):
            with patch("src.daily_loop_integration.daily_loop_persisted") as mock_loop:
                mock_loop.return_value = {"rounds_run": 0}
                result = schedule_loop(lambda i: {}, cron_expr="14 0",
                                        max_iterations=10, state_path=path)
        # No runs completed (interrupted before first run)
        assert result["runs_completed"] == 0