"""Tests for src/decide.py"""
import pytest
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.decide import make_decision, rollback_skill
from src.config import DecideConfig


def test_make_decision_keep():
    eval_data = {
        "baseline_rate": 0.80,
        "upgraded_rate": 0.88,
        "success_rate_delta": 0.08,
        "success_rate_improved": True,
        "cost_increase_ratio": 1.1,
        "cost_acceptable": True,
        "recommendation": "kept",
    }
    config = DecideConfig(min_success_rate_delta=0.05, max_cost_increase_ratio=1.2)
    decision = make_decision(eval_data, config)
    assert decision["decision"] == "kept"
    assert len(decision["reasons"]) >= 1


def test_make_decision_revert_no_improvement():
    eval_data = {
        "baseline_rate": 0.80,
        "upgraded_rate": 0.81,
        "success_rate_delta": 0.01,
        "success_rate_improved": False,
        "cost_increase_ratio": 1.0,
        "cost_acceptable": True,
        "recommendation": "reverted",
    }
    config = DecideConfig(min_success_rate_delta=0.05, max_cost_increase_ratio=1.2)
    decision = make_decision(eval_data, config)
    assert decision["decision"] == "reverted"


def test_make_decision_revert_cost_too_high():
    eval_data = {
        "baseline_rate": 0.80,
        "upgraded_rate": 0.88,
        "success_rate_delta": 0.08,
        "success_rate_improved": True,
        "cost_increase_ratio": 2.0,
        "cost_acceptable": False,
        "recommendation": "reverted",
    }
    config = DecideConfig(min_success_rate_delta=0.05, max_cost_increase_ratio=1.2)
    decision = make_decision(eval_data, config)
    assert decision["decision"] == "reverted"


def test_make_decision_auto_revert_on_regression():
    """Regression: worse results at higher cost should always revert."""
    eval_data = {
        "baseline_rate": 0.80,
        "upgraded_rate": 0.70,
        "success_rate_delta": -0.10,
        "success_rate_improved": False,
        "cost_increase_ratio": 1.5,
        "cost_acceptable": False,
        "recommendation": "reverted",
    }
    config = DecideConfig()
    decision = make_decision(eval_data, config)
    assert decision["decision"] == "reverted"
    assert any("regression" in r.lower() for r in decision["reasons"])


def test_rollback_skill_removes_file():
    with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
        path = f.name
        f.write(b"test")
    skill_path = f.name

    success = rollback_skill(skill_path)
    assert success is True
    assert not os.path.exists(skill_path)


def test_rollback_skill_nonexistent():
    success = rollback_skill("/tmp/nonexistent_skill_file_xyz.md")
    assert success is False


def test_rollback_skill_restores_backup(tmp_path):
    original = tmp_path / "SKILL.md"
    original.write_text("original content")
    backup = tmp_path / "SKILL.md.bak"
    backup.write_text("backup content")

    # Simulate overwrite: change original
    original.write_text("new content")

    # Rollback from backup
    success = rollback_skill(str(original), str(backup))
    assert success is True
    assert original.read_text() == "backup content"
