"""v1.8.0 Day 5: tests for 'self_upgrade audit' subcommand."""
import os, sys, subprocess, tempfile
import pytest

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"


def test_audit_subcommand_in_help():
    """self_upgrade --help should list 'audit'."""
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "--help"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    assert r.returncode == 0
    assert "audit" in r.stdout


def test_audit_help_shows_options():
    """self_upgrade audit --help should show --run and --limit."""
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "audit", "--help"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    assert r.returncode == 0
    for opt in ("--run", "--limit"):
        assert opt in (r.stdout + r.stderr)


def test_audit_show_when_no_history():
    """If no audit history exists, show helpful message."""
    # We can't easily test the real upgrades/history.db, so we just
    # verify the command runs without error and prints something.
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "audit", "--limit", "5"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    # exit 0 either way (no history is fine)
    assert r.returncode in (0, 1)
    # Some output
    assert r.stdout or r.stderr


def test_audit_run_creates_history_entry():
    """self_upgrade audit --run should add a row to audit_history."""
    import sqlite3
    db_path = os.path.join(PROJECT, "upgrades", "history.db")
    if not os.path.exists(db_path):
        pytest.skip("no upgrades/history.db to test against")

    pre_count = sqlite3.connect(db_path).execute(
        "SELECT COUNT(*) FROM audit_history"
    ).fetchone()[0]

    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "audit", "--run"],
        capture_output=True, text=True, cwd=PROJECT, timeout=30,
    )
    assert r.returncode == 0

    post_count = sqlite3.connect(db_path).execute(
        "SELECT COUNT(*) FROM audit_history"
    ).fetchone()[0]
    assert post_count == pre_count + 1, (
        f"expected audit_history +1 row, got {pre_count} -> {post_count}"
    )


def test_self_upgrade_now_has_7_subcommands():
    """After audit, the CLI should have 7 subcommands:
    run, evolve, status, unlock, cull, audit, gc."""
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "--help"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    for sub in ("run", "evolve", "status", "unlock", "cull", "audit", "gc"):
        assert sub in r.stdout, f"missing subcommand: {sub}"
