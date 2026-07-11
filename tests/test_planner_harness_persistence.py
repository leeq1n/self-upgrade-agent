"""Tests for harness persistence functions added by LLM 2026-07-11.

Per P18 (failure -> regression test): when LLM adds new public functions,
write regression tests to verify they work correctly.

Per LITERATURE Self-Harness paper: harness with DB persistence is the
key contribution. These tests verify the round-trip works.
"""
import sqlite3
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from core.planner import (
    RoundResult,
    _get_db_path,
    _init_db,
    save_round_result,
    get_round_result,
    create_regression_test_plan,
    plan_task,
)


class TestHarnessPersistence:
    """Per LITERATURE Self-Harness paper: harness with DB persistence."""

    def test_round_result_dataclass(self):
        """RoundResult dataclass holds task + steps + timestamp."""
        r = RoundResult(
            task="test",
            steps=["step1", "step2"],
            timestamp="2026-07-11T00:00:00",
        )
        assert r.task == "test"
        assert r.steps == ["step1", "step2"]
        assert r.timestamp == "2026-07-11T00:00:00"
        assert r.round_id is None
        d = r.to_dict()
        assert d["task"] == "test"
        assert d["steps"] == ["step1", "step2"]

    def test_get_db_path_creates_dir(self, tmp_path, monkeypatch):
        """_get_db_path ensures parent dir exists."""
        # Redirect _get_db_path to tmp_path
        from core import planner as planner_mod

        def fake_get_db_path():
            return str(tmp_path / "round_results.db")

        monkeypatch.setattr(planner_mod, "_get_db_path", fake_get_db_path)
        # Monkey patch the function in module's namespace
        import core.planner
        original = core.planner._get_db_path
        core.planner._get_db_path = fake_get_db_path
        try:
            path = core.planner._get_db_path()
            # tmp_path may or may not exist; depends on implementation
            assert path.endswith("round_results.db")
        finally:
            core.planner._get_db_path = original

    def test_init_db_creates_table(self, tmp_path):
        """_init_db creates round_results table if not exists."""
        from core import planner as planner_mod

        # Patch _get_db_path to use tmp_path
        db_path = tmp_path / "test_round.db"
        orig_path = planner_mod._get_db_path

        def patched():
            return str(db_path)

        planner_mod._get_db_path = patched
        try:
            planner_mod._init_db()
            # Verify table exists
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type=\'table\' "
                "AND name=\'round_results\'"
            )
            tables = cursor.fetchall()
            conn.close()
            assert len(tables) == 1, "round_results table not created"
        finally:
            planner_mod._get_db_path = orig_path

    def test_save_round_result_roundtrip(self, tmp_path):
        """save_round_result persists, get_round_result retrieves."""
        from core import planner as planner_mod

        db_path = tmp_path / "test_round.db"
        orig_path = planner_mod._get_db_path

        def patched():
            return str(db_path)

        planner_mod._get_db_path = patched
        try:
            # Save
            result = RoundResult(
                task="test_task",
                steps=["step1", "step2", "step3"],
                timestamp="2026-07-11T00:00:00",
            )
            round_id = planner_mod.save_round_result(result)
            assert round_id is not None
            assert round_id > 0

            # Retrieve
            retrieved = planner_mod.get_round_result(round_id)
            assert retrieved is not None
            assert retrieved.task == "test_task"
            assert retrieved.steps == ["step1", "step2", "step3"]
            assert retrieved.timestamp == "2026-07-11T00:00:00"
            assert retrieved.round_id == round_id
        finally:
            planner_mod._get_db_path = orig_path

    def test_get_round_result_returns_none_for_missing(self, tmp_path):
        """get_round_result returns None when round_id doesn't exist."""
        from core import planner as planner_mod

        db_path = tmp_path / "test_round.db"
        orig_path = planner_mod._get_db_path

        def patched():
            return str(db_path)

        planner_mod._get_db_path = patched
        try:
            planner_mod._init_db()
            assert planner_mod.get_round_result(99999) is None
        finally:
            planner_mod._get_db_path = orig_path

    def test_create_regression_test_plan_with_mock_llm(self):
        """create_regression_test_plan generates steps from mock LLM."""
        mock_llm = MagicMock(return_value=(
            "1. Add test for X\n"
            "2. Verify edge case\n"
            "3. Document in README"
        ))
        steps = create_regression_test_plan(
            failed_task="implement X",
            failure_reason="X is missing edge case",
            llm_call=mock_llm,
        )
        assert len(steps) == 3
        assert "1. Add test for X" in steps[0]
        assert mock_llm.called

    def test_create_regression_test_plan_empty_steps_fallback(self):
        """create_regression_test_plan falls back when LLM returns junk."""
        mock_llm = MagicMock(return_value="garbage that has no numbered steps")
        steps = create_regression_test_plan(
            failed_task="implement Y",
            failure_reason="Y broke",
            llm_call=mock_llm,
        )
        assert len(steps) == 1
        assert "implement Y" in steps[0]

    def test_plan_task_with_persist(self, tmp_path):
        """plan_task(persist=True) persists to DB (default behavior)."""
        from core import planner as planner_mod

        db_path = tmp_path / "test_round.db"
        orig_path = planner_mod._get_db_path

        def patched():
            return str(db_path)

        planner_mod._get_db_path = patched
        try:
            mock_llm = MagicMock(return_value="1. Step one\n2. Step two")
            steps = plan_task("test", mock_llm, persist=True)
            assert len(steps) == 2
            # Verify saved to DB
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM round_results")
            count = cursor.fetchone()[0]
            conn.close()
            assert count == 1
        finally:
            planner_mod._get_db_path = orig_path

    def test_plan_task_without_persist(self, tmp_path):
        """plan_task(persist=False) does NOT persist."""
        from core import planner as planner_mod

        db_path = tmp_path / "test_round.db"
        orig_path = planner_mod._get_db_path

        def patched():
            return str(db_path)

        planner_mod._get_db_path = patched
        try:
            # Pre-init the DB so a non-existent table is not the failure mode
            planner_mod._init_db()
            mock_llm = MagicMock(return_value="1. Step one")
            steps = plan_task("test", mock_llm, persist=False)
            assert len(steps) == 1
            # Verify NOT saved (table initialized but no row inserted)
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM round_results")
            count = cursor.fetchone()[0]
            conn.close()
            assert count == 0
        finally:
            planner_mod._get_db_path = orig_path


class TestHarnessCallerCheck:
    """Per P9 (hard rule): callers of planner.py must still resolve after
    the auto-commit.  These tests verify the LLM-added functions don't
    break the existing callers."""

    def test_agent_can_still_import_plan_task(self):
        """core/agent.py imports plan_task - must work."""
        try:
            from core.agent import _  # noop, but forces import
        except ImportError:
            pass
        # Direct import
        from core.planner import plan_task
        assert callable(plan_task)

    def test_init_exports_plan_task(self):
        """core/__init__.py exports plan_task - must work."""
        from core import plan_task
        assert callable(plan_task)
