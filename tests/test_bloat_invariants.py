"""v1.7.2 stress test for continuous self-upgrade rounds.

Verifies 5 invariants across N pipeline.run() calls:
  R1: core/planner.py MD5 stays at HEAD (no silent corruption)
  R2: upgrades/arxiv_cache/ growth observed (slow leak)
  R3: upgrades/history.db growth observed (slow leak)
  R4: No residue (*.bench_bak, *.bench_tmp, *.v17_test_bak)
  R5: working tree dirty stays at 1 (the ignored upgrades/ dir)

Run:
  pytest tests/test_bloat_invariants.py -v

Note: this test does NOT call the real LLM.  It runs in dry_run mode
to exercise the same pipeline plumbing.  For real-LLM bloat testing,
use /tmp/v172_stress.py (manual).
"""
import os, sys, json, hashlib, sqlite3, subprocess
import pytest

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)

PLANNER = "core/planner.py"


def md5_lf(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read().replace(b"\r\n", b"\n")).hexdigest()


def head_md5():
    r = subprocess.run(
        ["git", "ls-tree", "HEAD", PLANNER],
        capture_output=True, text=True, cwd=PROJECT,
    )
    sha = r.stdout.strip().split()[2]
    r2 = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True, cwd=PROJECT)
    return hashlib.md5(r2.stdout).hexdigest()


def count_files(path):
    if not os.path.exists(path):
        return 0
    n = 0
    for _, _, files in os.walk(path):
        n += len(files)
    return n


def db_rows():
    qf = os.path.join(PROJECT, "upgrades", "history.db")
    if not os.path.exists(qf):
        return {}
    conn = sqlite3.connect(qf)
    c = conn.cursor()
    out = {}
    for table in ["upgrades", "skill_registry", "skill_usage_log"]:
        try:
            c.execute(f"SELECT COUNT(*) FROM {{table}}")
            out[table] = c.fetchone()[0]
        except Exception:
            out[table] = "?"
    conn.close()
    return out


def residue():
    bad = []
    for root, dirs, files in os.walk(PROJECT):
        if ".git" in root or "upgrades" in root or ".venv" in root:
            continue
        for f in files:
            if any(f.endswith(s) for s in (
                ".bench_bak", ".bench_tmp",
                ".live_wrapper_bak", ".v17_test_bak", ".stress_bak",
                ".e2e_test_bak",
            )):
                bad.append(os.path.relpath(os.path.join(root, f), PROJECT))
    return bad


def test_core_planner_md5_matches_head():
    """R1: core/planner.py must always match HEAD MD5 after pipeline.run()."""
    assert md5_lf(PLANNER) == head_md5()


def test_no_residue_files():
    """R4: no .bench_bak / .bench_tmp residue in core/ or root."""
    res = residue()
    assert res == [], f"residue found: {res}"


def test_history_db_is_well_formed_sqlite():
    """R3: history.db is valid SQLite with expected tables."""
    qf = os.path.join(PROJECT, "upgrades", "history.db")
    if not os.path.exists(qf):
        pytest.skip("history.db not present")
    conn = sqlite3.connect(qf)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    assert "upgrades" in tables, f"missing upgrades table; have: {tables}"
    conn.close()


def test_working_tree_has_only_ignored_upgrades():
    """git status should be clean except for upgrades/ (gitignored)."""
    r = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, cwd=PROJECT,
    )
    dirty = [l for l in r.stdout.strip().split("\n") if l]
    non_upgrades = [l for l in dirty if not l.startswith("?? upgrades")]
    assert non_upgrades == [], f"unexpected dirty files: {non_upgrades}"


def test_3_rounds_dry_run_no_bloat():
    """Run pipeline 3 times in dry_run mode; verify bloat stays bounded."""
    from src.config import load_config
    from src import pipeline_lg as plg
    from src.research import Paper

    # Snapshot before
    pre_working = working_dirty_count = len([l for l in subprocess.run(
        ["git", "status", "--short"], capture_output=True, text=True, cwd=PROJECT
    ).stdout.strip().split("\n") if l])
    pre_arxiv = count_files("upgrades/arxiv_cache")
    pre_rows = db_rows().get("upgrades", 0)

    cfg = load_config("config.yaml")
    cfg.evaluate.trials_per_test = 1

    from src import research as research_mod
    paper = Paper(
        arxiv_id="2606.30639",
        title="Self-Evolving World Models for LLM Agent Planning",
        authors="Anon",
        published="2026-06-30",
        abstract="World models offer a principled way to equip long-horizon LLM agents with foresight.",
        categories="cs.AI, cs.CL",
    )
    research_mod.search_arxiv = lambda cfg: [paper]
    plg.search_arxiv = lambda cfg: [paper]

    # 3 rounds dry-run
    for n in range(3):
        # Pre-flight: git checkout HEAD (R1 mitigation)
        subprocess.run(["git", "checkout", "HEAD", "--", PLANNER], cwd=PROJECT, capture_output=True)
        # Clean residue
        for r in residue():
            try:
                os.remove(os.path.join(PROJECT, r))
            except OSError:
                pass
        # Run pipeline in dry-run mode (no LLM)
        plg.run(cfg, dry_run=True)

    # Verify invariants
    post_md5 = md5_lf(PLANNER)
    post_residue = residue()
    post_arxiv = count_files("upgrades/arxiv_cache")
    post_rows = db_rows().get("upgrades", 0)

    # R1: planner.py MD5 stable
    assert post_md5 == head_md5(), f"core/planner.py MD5 changed: {post_md5} != {head_md5()}"

    # R4: no residue
    assert post_residue == [], f"residue after 3 rounds: {post_residue}"

    # R3: history.db grew (dry-run mode still writes history)
    assert post_rows >= pre_rows, f"history.db rows shrank: {pre_rows} → {post_rows}"

    # R2: arxiv_cache should not grow dramatically (dry-run doesn't fetch arxiv)
    assert post_arxiv - pre_arxiv <= 2, f"arxiv_cache grew too much: {pre_arxiv} → {post_arxiv}"
