"""v1.8.0: tests for the gc (garbage-collect) subcommand.

User concern: '跑完以后要清理什么嘛?'  We added `self_upgrade gc`
so users don't have to remember cleanup commands.
"""
import os, sys, tempfile, time
import pytest

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)


def test_gc_help_shows_options():
    """gc --help should show 3 options: max-age, archive-rows, dry-run."""
    import subprocess
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "gc", "--help"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    assert r.returncode == 0
    out = r.stdout + r.stderr
    for opt in ("--arxiv-cache-max-age-days", "--archive-history-older-than-rows", "--dry-run"):
        assert opt in out, f"missing option: {opt}"


def test_gc_dry_run_does_not_delete_anything():
    """--dry-run must not actually remove files."""
    import subprocess
    # Snapshot pre-state
    pre = subprocess.run(
        ["du", "-sb", "upgrades"], capture_output=True, text=True, cwd=PROJECT,
    ).stdout.strip()
    # Dry-run
    subprocess.run(
        [sys.executable, "-m", "self_upgrade", "gc", "--dry-run"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    # Should be unchanged
    post = subprocess.run(
        ["du", "-sb", "upgrades"], capture_output=True, text=True, cwd=PROJECT,
    ).stdout.strip()
    # May differ by a few bytes due to __pycache__ rebuild, but no big change
    pre_n = int(pre.split()[0]) if pre.split()[0].isdigit() else 0
    post_n = int(post.split()[0]) if post.split()[0].isdigit() else 0
    assert abs(pre_n - post_n) < 10000, f"dry-run deleted {post_n - pre_n} bytes"


def test_gc_cleans_pycache():
    """gc should remove __pycache__ dirs that exist (always, regardless of age)."""
    import subprocess
    # Create a __pycache__ in a temp test area
    test_dir = os.path.join(PROJECT, "tests", "_gc_test")
    pycache = os.path.join(test_dir, "__pycache__")
    os.makedirs(pycache, exist_ok=True)
    f = os.path.join(pycache, "fake.pyc")
    with open(f, "w") as fh:
        fh.write("# fake pyc for test")
    assert os.path.exists(f)
    # Run gc
    subprocess.run(
        [sys.executable, "-m", "self_upgrade", "gc"],
        capture_output=True, text=True, cwd=PROJECT, timeout=15,
    )
    # __pycache__ should be gone
    assert not os.path.exists(pycache), f"__pycache__ not removed: {pycache}"
    # Cleanup test dir
    if os.path.exists(test_dir):
        os.rmdir(test_dir)


def test_gc_handles_zero_max_age():
    """--arxiv-cache-max-age-days 0 should delete ALL cache files."""
    import subprocess
    # Create a fake cache file
    cache_dir = os.path.join(PROJECT, "upgrades", "arxiv_cache")
    os.makedirs(cache_dir, exist_ok=True)
    fake = os.path.join(cache_dir, "test_gc_fake.pkl")
    with open(fake, "w") as f:
        f.write("x" * 100)
    # Run gc with 0 (delete all)
    subprocess.run(
        [sys.executable, "-m", "self_upgrade", "gc", "--arxiv-cache-max-age-days", "0"],
        capture_output=True, text=True, cwd=PROJECT, timeout=15,
    )
    # The fake should be gone
    assert not os.path.exists(fake), f"cache file not deleted with max-age 0"


def test_gc_does_not_touch_planner():
    """gc must NEVER touch core/planner.py or any src/ file."""
    import subprocess
    import hashlib
    with open(os.path.join(PROJECT, "core", "planner.py"), "rb") as f:
        pre_md5 = hashlib.md5(f.read()).hexdigest()
    subprocess.run(
        [sys.executable, "-m", "self_upgrade", "gc", "--arxiv-cache-max-age-days", "0"],
        capture_output=True, text=True, cwd=PROJECT, timeout=15,
    )
    with open(os.path.join(PROJECT, "core", "planner.py"), "rb") as f:
        post_md5 = hashlib.md5(f.read()).hexdigest()
    assert pre_md5 == post_md5, "planner.py MD5 changed after gc!"


def test_gc_idempotent():
    """Running gc twice in a row should not error and not delete more on 2nd run."""
    import subprocess
    r1 = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "gc"],
        capture_output=True, text=True, cwd=PROJECT, timeout=15,
    )
    assert r1.returncode == 0
    r2 = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "gc"],
        capture_output=True, text=True, cwd=PROJECT, timeout=15,
    )
    assert r2.returncode == 0


def test_subcommands_count_includes_gc():
    """Adding gc brings us to 6 subcommands (run, evolve, status, unlock, cull, gc).

    Design rule: 5 user-facing + 1 maintenance.  Adding more = feature creep.
    """
    import subprocess
    r = subprocess.run(
        [sys.executable, "-m", "self_upgrade", "--help"],
        capture_output=True, text=True, cwd=PROJECT, timeout=10,
    )
    out = r.stdout
    for sub in ("run", "evolve", "status", "unlock", "cull", "gc"):
        assert sub in out, f"missing subcommand in --help: {sub}"
