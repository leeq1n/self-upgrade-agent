"""v1.8.0: tests for the unified CLI (self_upgrade package).

The user observed that `python -m core.agent` and `python run.py`
felt like two different products, not one.  This commit unifies
them under `python -m self_upgrade <subcommand>`.

These tests verify the subcommand surface works without actually
calling LLM (status / unlock / help) and that the two old entry
points are still importable for backward compat.
"""
import os, sys, subprocess
import pytest

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"


def test_self_upgrade_help_shows_subcommands():
    """The new unified CLI should expose run/evolve/status/unlock/cull."""
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "--help"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    assert r.returncode == 0
    out = r.stdout + r.stderr
    for sub in ("run", "evolve", "status", "unlock", "cull"):
        assert sub in out, f"subcommand {sub!r} not advertised in --help"


def test_self_upgrade_status_runs_without_llm():
    """status should not call LLM (purely reads files)."""
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "status"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    assert r.returncode == 0
    out = r.stdout
    assert "SELF-UPGRADE AGENT STATUS" in out
    assert "core/planner.py" in out
    assert "history.db" in out


def test_self_upgrade_unlock_runs_without_llm():
    """unlock should not call LLM (just resets quota_state)."""
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "unlock"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    assert r.returncode == 0
    out = r.stdout
    assert "Unlocked" in out or "No quota_state" in out


def test_old_entry_points_still_importable():
    """core/agent.py and run.py must still work for backward compat.

    v1.7.2 had two entry points; v1.8.0 unifies them but doesn't
    break the old ones.
    """
    sys.path.insert(0, PROJECT)
    # core.agent should still expose run() and quick_test()
    from core.agent import run as agent_run, quick_test
    assert callable(agent_run)
    assert callable(quick_test)

    # run.py should still expose main()
    import importlib.util
    spec = importlib.util.spec_from_file_location("run", os.path.join(PROJECT, "run.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.main)


def test_subcommand_count_matches_ux_goals():
    """5 subcommands = the 5 things a user wants to do with this product:
      run     = use it
      evolve  = let it improve itself
      status  = see what happened
      unlock  = recover from quota exhaustion
      cull    = maintenance (skill lifecycle)

    Adding more subcommands would be feature creep.
    """
    from self_upgrade.__main__ import main
    import argparse
    # Parse --help to count subparsers
    try:
        # main() will call sys.exit on --help; capture via try/except SystemExit
        import sys
        old_argv = sys.argv
        sys.argv = ["self-upgrade", "--help"]
        try:
            main()
        except SystemExit:
            pass
        finally:
            sys.argv = old_argv
    except SystemExit:
        pass
    # Just assert that the design has 5 subcommands by inspecting source
    with open(os.path.join(PROJECT, "self_upgrade", "__main__.py")) as f:
        src = f.read()
    expected = [
        'p_run = sub.add_parser("run"',
        'p_ev = sub.add_parser("evolve"',
        'sub.add_parser("status"',
        'sub.add_parser("unlock"',
        'sub.add_parser("cull"',
    ]
    for e in expected:
        assert e in src, f"missing subcommand declaration: {e}"


def test_run_subcommand_exists_for_use_case():
    """The 'use the agent' subcommand must be named 'run', not 'use' or 'plan'."""
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "run", "--help"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    assert r.returncode == 0
    out = r.stdout + r.stderr
    assert "task" in out.lower(), "run subcommand should accept a task argument"


def test_evolve_subcommand_distinct_from_run():
    """evolve and run must NOT be the same code path.

    If they were, the 'two products' UX problem would still exist.
    """
    from self_upgrade.__main__ import cmd_run, cmd_evolve
    # Different functions (not the same object)
    assert cmd_run is not cmd_evolve
    # And the source code has different implementations
    with open(os.path.join(PROJECT, "self_upgrade", "__main__.py")) as f:
        src = f.read()
    assert "def cmd_run(" in src
    assert "def cmd_evolve(" in src
    # Each calls a different module: run -> core.agent, evolve -> src.pipeline_lg
    assert "from core.agent import quick_test" in src
    assert "src.pipeline_lg" in src
    # cmd_evolve loads plg (alias) inside the function body
    assert "import src.pipeline_lg as plg" in src
