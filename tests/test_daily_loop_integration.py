"""Tests for daily-loop integration (per v3.1.2 sub-task 3/3).

Per 你 vision (autonomous agent):
- Persist round state at end of each round (per P19)
- Auto-mark failures (per failure_recovery)
- Recover from last persisted state on startup

Per 自上而下/分治:
- Big: v3.1.2 daily-loop persistence
- Sub-task 1 (done): state.json
- Sub-task 2 (done): failure recovery
- Sub-task 3 (this): integration with daily-loop

Per LITERATURE Signal-to-Fix: test integration separately (mock).
Per P18: regression tests required.
"""
import json
from pathlib import Path

import pytest

from src.daily_loop_integration import (
    record_round,
    record_failure,
    get_resume_state,
    init_daily_loop,
    daily_loop_persisted,
)


class TestDailyLoopIntegration:
    """Per v3.1.2 sub-task 3/3: integration of state + recovery into daily-loop."""

    def test_record_round(self, tmp_path):
        """record_round: persists round data to state.json."""
        path = tmp_path / "state.json"
        record_round(0,
                     {"decision": "KEPT", "target": "core/planner.py",
                      "tests_passed": 16},
                     state_path=path)
        from src.state_persistence import load_state
        state = load_state(path)
        assert "0" in state["rounds"]
        assert state["rounds"]["0"]["decision"] == "KEPT"

    def test_record_failure(self, tmp_path):
        """record_failure: persists failure to state.json."""
        path = tmp_path / "state.json"
        record_failure(3, "patch failed", state_path=path)
        state = load_state(path) if False else None
        from src.state_persistence import load_state
        state = load_state(path)
        assert "3" in state["failures"]
        assert state["failures"]["3"]["error"] == "patch failed"

    def test_get_resume_state_empty(self, tmp_path):
        """get_resume_state: missing state -> can_resume=False."""
        path = tmp_path / "missing.json"
        resume = get_resume_state(path)
        assert resume["can_resume"] is False
        assert resume["last_round_index"] is None

    def test_get_resume_state_with_history(self, tmp_path):
        """get_resume_state: with state -> can_resume=True."""
        path = tmp_path / "state.json"
        record_round(0, {"decision": "KEPT"}, state_path=path)
        record_round(1, {"decision": "NO_PATCH"}, state_path=path)
        record_failure(2, "err", state_path=path)
        resume = get_resume_state(path)
        assert resume["can_resume"] is True
        assert resume["last_round_index"] == 1
        assert "2" in resume["failures"]

    def test_init_daily_loop_first_time(self, tmp_path):
        """init_daily_loop: first time creates state.json."""
        path = tmp_path / "state.json"
        state = init_daily_loop(meta={"target": "core/X"}, state_path=path)
        assert state["schema_version"] == "1.0"
        assert state["meta"]["target"] == "core/X"
        assert "rounds" in state

    def test_init_daily_loop_idempotent(self, tmp_path):
        """init_daily_loop: second time preserves existing state."""
        path = tmp_path / "state.json"
        # First init
        init_daily_loop(meta={"target": "core/A"}, state_path=path)
        # Add a round
        record_round(0, {"decision": "KEPT"}, state_path=path)
        # Second init (should NOT clobber)
        state = init_daily_loop(meta={"target": "core/B"}, state_path=path)
        assert "0" in state["rounds"]
        # Meta preserved (not overwritten)
        assert state["meta"]["target"] == "core/A"

    def test_daily_loop_persisted_basic(self, tmp_path):
            """daily_loop_persisted: runs N rounds, persists all."""
            path = tmp_path / "state.json"
            def fake_round(round_idx):
                # Round 1 is odd (NO_PATCH), round 2 is even (KEPT), round 3 is odd (NO_PATCH)
                return {
                    "decision": "KEPT" if round_idx % 2 == 0 else "NO_PATCH",
                    "target": "core/test",
                    "tests_passed": 16,
                }
            result = daily_loop_persisted(fake_round, max_rounds=3,
                                           interval=0, state_path=path)
            assert result["rounds_run"] == 3
            assert result["kept_count"] == 1  # only round 2 (even)
            assert result["failures_count"] == 0
            from src.state_persistence import load_state
            state = load_state(path)
            assert len(state["rounds"]) == 3

    def test_daily_loop_persisted_failures_caught(self, tmp_path):
        """daily_loop_persisted: exceptions become failures, not crashes."""
        path = tmp_path / "state.json"
        def fake_round(round_idx):
            if round_idx == 2:
                raise ValueError("LLM did not produce patch")
            return {"decision": "KEPT", "target": "core/test"}
        result = daily_loop_persisted(fake_round, max_rounds=3,
                                       interval=0, state_path=path)
        assert result["rounds_run"] == 3
        assert result["failures_count"] == 1
        from src.state_persistence import load_state
        state = load_state(path)
        assert "2" in state["failures"]
        assert "LLM did not produce" in state["failures"]["2"]["error"]

    def test_daily_loop_persisted_resumable(self, tmp_path):
            """After first batch + restart, second batch continues from next idx."""
            path = tmp_path / "state.json"
            def round_a(idx):
                return {"decision": "KEPT", "target": "core/X"}
            # First batch (3 rounds): starts at idx 1
            daily_loop_persisted(round_a, max_rounds=3, state_path=path)
            # Restart simulation: get_resume_state should show round 3 done
            resume = get_resume_state(path)
            assert resume["can_resume"] is True
            assert resume["last_round_index"] == 3

            # Second batch (2 more rounds, starts at idx 4)
            def round_b(idx):
                return {"decision": "NO_PATCH", "target": "core/X"}
            daily_loop_persisted(round_b, max_rounds=2, state_path=path)
            from src.state_persistence import load_state
            state = load_state(path)
            # Total 5 rounds persisted (1,2,3 from batch 1 + 4,5 from batch 2)
            assert len(state["rounds"]) == 5
            assert state["last_round_index"] == 5
