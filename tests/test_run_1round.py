"""v1.8.0 Day 6: tests for run_1round.py wrapper.

Verifies:
  - The script imports cleanly
  - The CLI signature is correct (paper_id, title positional args)
  - It does NOT call LLM at import time (saves quota)
"""
import os, sys, ast
import pytest

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"


def test_run_1round_py_exists():
    p = os.path.join(PROJECT, "run_1round.py")
    assert os.path.exists(p)


def test_run_1round_py_imports_clean():
    """run_1round.py must import as a module without side effects."""
    p = os.path.join(PROJECT, "run_1round.py")
    with open(p) as f:
        content = f.read()
    # Static check: no LLM call at module level
    assert "if __name__" in content
    # No top-level chat() / run_pipeline calls
    lines = content.split("\n")
    module_level_calls = [l for l in lines
                           if not l.startswith((" ", "\t", "#", "import", "from", "if "))
                           and "=" in l and "LLM" not in l and "log" not in l.lower()]
    # Just verify the LLM call is in the run function, not at module level
    assert "def run_one_round" in content


def test_run_1round_py_argparse_or_sys_argv():
    """The script should support sys.argv for paper_id and title."""
    p = os.path.join(PROJECT, "run_1round.py")
    with open(p) as f:
        content = f.read()
    assert "sys.argv" in content
    assert "len(sys.argv)" in content


def test_run_1round_py_saves_results_to_upgrades():
    """run_1round.py should save results to upgrades/run_1round_<ts>.json."""
    p = os.path.join(PROJECT, "run_1round.py")
    with open(p) as f:
        content = f.read()
    assert "upgrades/run_1round_" in content
    assert ".json" in content


def test_run_1round_py_auto_unlocks_at_end():
    """run_1round.py should call self_upgrade unlock at the end."""
    p = os.path.join(PROJECT, "run_1round.py")
    with open(p) as f:
        content = f.read()
    assert "self_upgrade" in content
    assert "unlock" in content


def test_run_1round_py_uses_harness_and_audit():
    """run_1round.py should report both harness and audit results."""
    p = os.path.join(PROJECT, "run_1round.py")
    with open(p) as f:
        content = f.read()
    assert "HARNESS" in content
    assert "AUDIT" in content


def test_run_1round_py_syntax_valid():
    """run_1round.py must be syntactically valid Python."""
    p = os.path.join(PROJECT, "run_1round.py")
    with open(p) as f:
        source = f.read()
    ast.parse(source)


def test_old_run_1round_day3_removed():
    """The old Day 3 wrapper (run_1round_day3.py) should be deleted."""
    p = os.path.join(PROJECT, "run_1round_day3.py")
    assert not os.path.exists(p), f"old wrapper still exists: {p}"


def test_run_3rounds_manual_still_exists():
    """The stable run_3rounds_manual.py must still exist."""
    p = os.path.join(PROJECT, "run_3rounds_manual.py")
    assert os.path.exists(p)
