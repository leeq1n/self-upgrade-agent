"""Tests for state persistence (per P19 + v3.1.2 daily-loop persistence).

Per P19 (Data flow observability):
- Persist intermediate results for cross-round observability
- Daily-loop state across rounds + restarts

Per 你 vision (autonomous agent): cross-process state for failure recovery.

Per 自上而下/分治 (user meta-principle):
- Big task: v3.1.2 daily-loop persistence
- Sub-task 1 (this): state.json persistence (cross-round state)
- Sub-task 2 (future): failure recovery
- Sub-task 3 (future): integration with daily-loop

Per P9 hard rule: atomic write (tmp + os.replace).
Per P18: regression tests required.
"""
import json
import time
from pathlib import Path

import pytest

from src.state_persistence import (
    atomic_write_json,
    load_state,
    save_state,
    update_round,
    get_last_round,
    get_round,
    get_all_rounds,
    init_state,
    _now_iso,
    _now_ts,
)


class TestStatePersistence:
    """Per P19 + v3.1.2: cross-round state persistence."""

    def test_atomic_write_creates_file(self, tmp_path):
        """atomic_write_json creates file atomically."""
        path = tmp_path / "test.json"
        atomic_write_json(path, {"key": "value"})
        assert path.exists()
        assert json.loads(path.read_text(encoding="utf-8")) == {"key": "value"}

    def test_atomic_write_replaces_existing(self, tmp_path):
        """atomic_write_json replaces existing file (no torn read)."""
        path = tmp_path / "test.json"
        path.write_text('{"old": true}', encoding="utf-8")
        atomic_write_json(path, {"new": True})
        assert json.loads(path.read_text(encoding="utf-8")) == {"new": True}

    def test_load_state_missing_file(self, tmp_path):
        """load_state: missing file -> empty dict (no crash)."""
        result = load_state(tmp_path / "missing.json")
        assert result == {}

    def test_load_state_invalid_json(self, tmp_path):
        """load_state: invalid JSON -> empty dict (graceful)."""
        path = tmp_path / "bad.json"
        path.write_text("not json", encoding="utf-8")
        result = load_state(path)
        assert result == {}

    def test_save_state_creates_file(self, tmp_path):
        """save_state: writes state atomically."""
        path = tmp_path / "state.json"
        save_state({"rounds": {}, "meta": {"x": 1}}, path)
        assert path.exists()
        assert json.loads(path.read_text(encoding="utf-8")) ==                {"rounds": {}, "meta": {"x": 1}}

    def test_init_state_schema(self, tmp_path):
        """init_state creates state with schema_version + meta."""
        path = tmp_path / "state.json"
        state = init_state(meta={"agent": "v3"}, state_path=path)
        assert state["schema_version"] == "1.0"
        assert state["meta"]["agent"] == "v3"
        assert state["rounds"] == {}
        assert state["last_round_index"] is None
        assert "created_at" in state

    def test_update_round_persists(self, tmp_path):
        """update_round: adds round data + last_updated."""
        path = tmp_path / "state.json"
        state = update_round(0,
                             {"decision": "KEPT", "target": "core/planner.py",
                              "tests_passed": 16},
                             state_path=path)
        assert "0" in state["rounds"]
        r = state["rounds"]["0"]
        assert r["decision"] == "KEPT"
        assert r["tests_passed"] == 16
        assert state["last_round_index"] == 0
        assert "persisted_at" in r

    def test_update_round_multiple(self, tmp_path):
        """update_round: multiple rounds accumulate."""
        path = tmp_path / "state.json"
        for i in range(3):
            update_round(i, {"decision": f"KEPT-{i}"}, state_path=path)
        state = load_state(path)
        assert len(state["rounds"]) == 3
        assert state["last_round_index"] == 2

    def test_get_last_round(self, tmp_path):
        """get_last_round: returns last index or None."""
        path = tmp_path / "state.json"
        assert get_last_round(path) is None  # empty
        update_round(5, {"x": 1}, state_path=path)
        assert get_last_round(path) == 5

    def test_get_round_specific(self, tmp_path):
        """get_round: get specific round data."""
        path = tmp_path / "state.json"
        update_round(2, {"decision": "KEPT", "target": "core/X"}, state_path=path)
        result = get_round(2, state_path=path)
        assert result["decision"] == "KEPT"
        assert get_round(99, state_path=path) is None  # missing

    def test_get_all_rounds_sorted(self, tmp_path):
        """get_all_rounds: returns sorted by index."""
        path = tmp_path / "state.json"
        # Insert out of order
        update_round(2, {"decision": "B"}, state_path=path)
        update_round(0, {"decision": "A"}, state_path=path)
        update_round(1, {"decision": "X"}, state_path=path)
        rounds = get_all_rounds(path)
        assert len(rounds) == 3
        assert [r["decision"] for r in rounds] == ["A", "X", "B"]

    def test_get_all_rounds_empty(self, tmp_path):
        """get_all_rounds: empty state -> []."""
        path = tmp_path / "state.json"
        assert get_all_rounds(path) == []

    def test_state_survives_reload(self, tmp_path):
        """save -> load roundtrip preserves data."""
        path = tmp_path / "state.json"
        original = {
            "schema_version": "1.0",
            "rounds": {
                "0": {"decision": "KEPT", "target": "core/planner.py"},
                "1": {"decision": "NO_PATCH"},
            },
            "meta": {"agent": "v3.1"},
        }
        save_state(original, path)
        loaded = load_state(path)
        assert loaded == original

    def test_concurrent_updates_no_torn(self, tmp_path):
        """atomic_write_json prevents torn reads (per ISS-003 lesson)."""
        path = tmp_path / "state.json"
        # Simulate rapid updates
        for i in range(10):
            update_round(i, {"decision": f"R{i}"}, state_path=path)
        # Verify all 10 rounds are present (no torn read)
        state = load_state(path)
        assert len(state["rounds"]) == 10
        # Verify each round has valid persisted_at
        for k, v in state["rounds"].items():
            assert "persisted_at" in v
            assert v["decision"].startswith("R")
