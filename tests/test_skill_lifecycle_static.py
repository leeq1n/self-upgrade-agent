"""v1.8.0 Day 3: tests for evaluate_all_skills_static (0 LLM)."""
import os, sys, tempfile
import pytest

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)


def _make_temp_db():
    """Create a minimal UpgradeHistory db for testing."""
    from src.db import UpgradeHistory
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = UpgradeHistory(tmp.name)
    return db, tmp.name


def _add_skill(db, name, use_count, avg_improvement):
    """Register a skill + manually set use_count and avg_improvement."""
    db.register_skill(
        skill_name=name, skill_path="/tmp/x.py",
        paper_arxiv_id="x", paper_title="x",
    )
    db.conn.execute(
        "UPDATE skill_registry SET use_count=?, avg_improvement=? WHERE skill_name=?",
        (use_count, avg_improvement, name),
    )
    db.conn.commit()


def test_evaluate_all_skills_static_empty():
    """No skills → empty dict, 0 LLM."""
    db, _ = _make_temp_db()
    try:
        from src.skill_lifecycle import evaluate_all_skills_static
        result = evaluate_all_skills_static(db)
        assert result == {}
    finally:
        db.close()


def test_evaluate_all_skills_static_one_skill_kept():
    """Skill with avg_improvement=0.1, use_count=10 → kept (quality=1.0)."""
    db, _ = _make_temp_db()
    try:
        from src.skill_lifecycle import evaluate_all_skills_static
        _add_skill(db, "good_skill", use_count=10, avg_improvement=0.1)
        result = evaluate_all_skills_static(db)
        assert "good_skill" in result
        assert result["good_skill"]["quality_score"] == 1.0
        assert result["good_skill"]["action"] == "kept"
    finally:
        db.close()


def test_evaluate_all_skills_static_one_skill_culled():
    """Skill with avg_improvement=-0.05, use_count=3 → culled (quality<0)."""
    db, _ = _make_temp_db()
    try:
        from src.skill_lifecycle import evaluate_all_skills_static
        _add_skill(db, "bad_skill", use_count=3, avg_improvement=-0.05)
        result = evaluate_all_skills_static(db, cull_threshold=0.0)
        assert "bad_skill" in result
        assert result["bad_skill"]["quality_score"] < 0
        assert result["bad_skill"]["action"] == "culled"
    finally:
        db.close()


def test_evaluate_all_skills_static_mixed():
    """Multiple skills with different qualities."""
    db, _ = _make_temp_db()
    try:
        from src.skill_lifecycle import evaluate_all_skills_static
        _add_skill(db, "a", use_count=5, avg_improvement=0.10)   # quality=0.5
        _add_skill(db, "b", use_count=100, avg_improvement=0.02)  # quality=2.0
        _add_skill(db, "c", use_count=1, avg_improvement=-0.10)  # quality=-0.1
        result = evaluate_all_skills_static(db)
        assert result["b"]["quality_score"] == 2.0
        assert result["a"]["quality_score"] == 0.5
        assert result["c"]["quality_score"] < 0
        assert result["c"]["action"] == "culled"
        assert result["a"]["action"] == "kept"
        assert result["b"]["action"] == "kept"
    finally:
        db.close()


def test_evaluate_all_skills_static_read_only():
    """evaluate_all_skills_static must NOT modify the database."""
    db, _ = _make_temp_db()
    try:
        from src.skill_lifecycle import evaluate_all_skills_static
        _add_skill(db, "x", use_count=10, avg_improvement=0.5)
        before = db.get_active_skills()
        assert len(before) == 1
        result = evaluate_all_skills_static(db)
        after = db.get_active_skills()
        # Same number of active skills (culling is separate concern)
        assert len(after) == 1
        assert result["x"]["action"] == "kept"
    finally:
        db.close()


def test_skill_lifecycle_imports():
    """Both functions must be importable."""
    from src.skill_lifecycle import (
        evaluate_all_skills_static,
        evaluate_all_skills,  # legacy LLM-based
        cull_obsolete,
    )
    assert callable(evaluate_all_skills_static)
    assert callable(evaluate_all_skills)
    assert callable(cull_obsolete)
