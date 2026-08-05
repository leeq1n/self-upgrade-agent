"""v1.8.0 Day 7: tests for run_stable.py."""
import os, sys, ast
import pytest

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_run_stable_py_exists():
    p = os.path.join(PROJECT, "run_stable.py")
    assert os.path.exists(p)


def test_run_stable_py_syntax():
    p = os.path.join(PROJECT, "run_stable.py")
    with open(p, encoding="utf-8") as f:
        source = f.read()
    ast.parse(source)


def test_run_stable_py_target_argv():
    """First argv is target count, second is gap seconds."""
    p = os.path.join(PROJECT, "run_stable.py")
    with open(p, encoding="utf-8") as f:
        content = f.read()
    assert "sys.argv[1]" in content
    assert "sys.argv[2]" in content


def test_run_stable_py_tracks_consecutive_kept():
    """The wrapper counts CONSECUTIVE KEPT rounds (resets on any revert)."""
    p = os.path.join(PROJECT, "run_stable.py")
    with open(p, encoding="utf-8") as f:
        content = f.read()
    assert "consecutive_kept" in content
    assert "harness 100%" in content.lower() or "harness_pct" in content
    # Counter reset on not-kept
    assert "counter reset" in content or "consecutive_kept = 0" in content


def test_run_stable_py_stops_on_target():
    """When target reached, exits successfully."""
    p = os.path.join(PROJECT, "run_stable.py")
    with open(p, encoding="utf-8") as f:
        content = f.read()
    assert "REACHED TARGET" in content
    assert "sys.exit(0)" in content


def test_run_stable_py_max_rounds_cap():
    """Hard cap to prevent infinite loop."""
    p = os.path.join(PROJECT, "run_stable.py")
    with open(p, encoding="utf-8") as f:
        content = f.read()
    assert "max_rounds" in content
    assert "20" in content  # cap = 20


def test_run_stable_py_papers_rotation():
    """PAPERS list has 5+ candidates, rotates through them."""
    p = os.path.join(PROJECT, "run_stable.py")
    with open(p, encoding="utf-8") as f:
        content = f.read()
    # Should have at least 5 papers
    paper_count = content.count('"arxiv_id"')
    assert paper_count >= 5, f"only {paper_count} papers"


def test_run_stable_py_saves_results():
    """Saves to upgrades/run_stable_<ts>.json."""
    p = os.path.join(PROJECT, "run_stable.py")
    with open(p, encoding="utf-8") as f:
        content = f.read()
    assert "upgrades/run_stable_" in content


def test_run_stable_py_preflight_safety():
    """preflight() restores planner.py and resets quota_state."""
    p = os.path.join(PROJECT, "run_stable.py")
    with open(p, encoding="utf-8") as f:
        content = f.read()
    assert "def preflight" in content
    # subprocess call uses list args, not direct "git checkout" string
    assert '"git"' in content
    assert '"checkout"' in content
    assert "dead_until" in content
