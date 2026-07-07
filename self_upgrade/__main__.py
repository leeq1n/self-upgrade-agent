"""self_upgrade — unified CLI for the self-upgrade agent.

Subcommands:
  run      "task"   Use the agent (single task, ~5-30s)
  evolve   [--live]  Self-improvement loop (7 stages, ~15min)
  status             Show history.db, manifest, planner version
  unlock             Reset quota_state dead marks
  cull               Cull low-effectiveness skills

Design: one CLI = one product.  v1.7.2 had two separate entry
points (`python -m core.agent` and `python run.py`) that felt
like different products.  This unifies them under one roof.
"""
import argparse
import os
import sys
import logging


def main():
    parser = argparse.ArgumentParser(
        prog="self-upgrade",
        description="Self-upgrade agent — use it, or watch it evolve itself",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # run: use the agent
    p_run = sub.add_parser("run", help="Run a task with the agent")
    p_run.add_argument("task", nargs="+", help="Task description")

    # evolve: self-upgrade loop
    p_ev = sub.add_parser("evolve", help="Run the self-upgrade loop")
    p_ev.add_argument(
        "--live", action="store_true",
        help="Real LLM calls (default: dry-run)",
    )
    p_ev.add_argument(
        "--config", default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )

    # status: show history
    sub.add_parser("status", help="Show history.db, manifest, planner version")

    # unlock: reset quota
    sub.add_parser("unlock", help="Reset quota_state dead marks")

    # cull: prune skills
    sub.add_parser("cull", help="Cull low-effectiveness skills")

    # audit: show audit history
    p_audit = sub.add_parser("audit", help="Show skill audit history (v1.8.0)")
    p_audit.add_argument(
        "--limit", type=int, default=10,
        help="Show last N audit runs (default 10)",
    )
    p_audit.add_argument(
        "--run", action="store_true",
        help="Run a skill audit right now (instead of showing history)",
    )

    # gc: garbage-collect cache + temp files
    p_gc = sub.add_parser("gc", help="Garbage-collect cache files (arxiv_cache, s2_cache, __pycache__, sandbox residue)")
    p_gc.add_argument(
        "--arxiv-cache-max-age-days", type=int, default=30,
        help="Delete arxiv_cache files older than N days (default: 30, 0=delete all)",
    )
    p_gc.add_argument(
        "--archive-history-older-than-rows", type=int, default=0,
        help="Archive history.db rows older than N rows (default: 0=keep all)",
    )
    p_gc.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    p_gc.add_argument(
        "--memory-policy", type=str, default=None,
        help="Emergent memory policy as 'module:function' (v1.8.1). "
             "Default: noop. LLM can install a smarter policy by editing "
             "src/learning.py:apply_memory_policy via patchgen, "
             "or by passing --memory-policy my_policies:trim_old.",
    )

    args = parser.parse_args()

    if args.cmd == "run":
        return cmd_run(" ".join(args.task))
    if args.cmd == "evolve":
        return cmd_evolve(live=args.live, config_path=args.config)
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "unlock":
        return cmd_unlock()
    if args.cmd == "cull":
        return cmd_cull()
    if args.cmd == "audit":
        return cmd_audit(limit=args.limit, run_now=args.run)
    if args.cmd == "gc":
        return cmd_gc(
            arxiv_max_age=args.arxiv_cache_max_age_days,
            history_archive_rows=args.archive_history_older_than_rows,
            dry_run=args.dry_run,
            memory_policy=args.memory_policy,
        )
    parser.print_help()
    return 1


# ── Subcommand implementations ─────────────────────────────────

def cmd_run(task: str) -> int:
    """Use the agent on a single task.

    This is the same as the old `python -m core.agent "task"` entry
    point, but now it lives under the unified CLI.
    """
    print(f"\nTask: {task}\n{'='*50}")
    from core.agent import quick_test
    result = quick_test(task)
    print(f"\n{'='*50}")
    if result.get("error"):
        print(f"Error: {result['error']}")
        return 1
    print(f"Steps planned:  {result['steps_planned']}")
    print(f"Tools used:     {result['tools_used']}")
    print(f"Time:           {result['elapsed']}s")
    print(f"Success:        {result['success']}")
    print(f"\nPlan:")
    for i, log in enumerate(result.get("logs", [])):
        print(f"  {i+1}. {log.get('step', '?')[:80]}")
    return 0


def cmd_evolve(live: bool, config_path: str) -> int:
    """Run the self-evolution loop.

    Same as the old `python run.py [--live]` entry point.
    """
    import src.pipeline_lg as plg
    from src.config import load_config
    cfg = load_config(config_path)
    if not live:
        cfg.dry_run = True
    print(f"Starting self-evolution (live={live}, config={config_path})")
    state = plg.run(cfg, dry_run=cfg.dry_run)
    print(f"\nDone: {state.get('done')}")
    decision = (state.get("decision") or {}).get("decision")
    if decision:
        print(f"Decision: {decision}")
    return 0 if state.get("done") else 1


def cmd_status() -> int:
    """Show history.db, manifest, planner version, etc."""
    print(f"\n{'='*50}")
    print("SELF-UPGRADE AGENT STATUS")
    print(f"{'='*50}\n")

    # Planner version
    planner_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "core", "planner.py",
    )
    if os.path.exists(planner_path):
        size = os.path.getsize(planner_path)
        with open(planner_path) as f:
            for line in f:
                if "__version__" in line:
                    print(f"core/planner.py: {size} bytes, {line.strip()}")
                    break
    else:
        print("core/planner.py: NOT FOUND")

    # History.db
    import sqlite3
    hist = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "upgrades", "history.db",
    )
    if os.path.exists(hist):
        conn = sqlite3.connect(hist)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM upgrades")
        n_total = c.fetchone()[0]
        c.execute("SELECT decision, COUNT(*) FROM upgrades GROUP BY decision")
        print(f"\nupgrades/history.db: {n_total} total attempts")
        for row in c.fetchall():
            print(f"  {row[0]}: {row[1]}")
        c.execute("SELECT id, decision, notes FROM upgrades ORDER BY id DESC LIMIT 3")
        print("  latest 3:")
        for row in c.fetchall():
            print(f"    id={row[0]} decision={row[1]!r} notes={row[2][:60]!r}")
        conn.close()
    else:
        print("\nupgrades/history.db: NOT FOUND")

    # Manifest.json
    manifest = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "upgrades", "manifest.json",
    )
    if os.path.exists(manifest):
        import json
        m = json.load(open(manifest))
        n_promoted = len(m.get("history", []))
        print(f"\nupgrades/manifest.json: {n_promoted} promoted")
    return 0


def cmd_unlock() -> int:
    """Reset quota_state dead marks.

    Same as the old `python run.py --unlock-keys`.
    """
    import json
    qf = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "upgrades", "quota_state.json",
    )
    if not os.path.exists(qf):
        print("No quota_state.json — nothing to unlock")
        return 0
    state = json.load(open(qf))
    n = sum(1 for v in state.get("keys", {}).values() if v.get("dead_until", 0) > 0)
    for info in state.get("keys", {}).values():
        info["dead_until"] = 0
        info["failures_today"] = 0
    json.dump(state, open(qf, "w"), indent=2)
    print(f"Unlocked {n} keys in {qf}")
    return 0


def cmd_cull() -> int:
    """Cull low-effectiveness skills.

    Same as the old `python run.py --cull`.
    """
    from src.skill_lifecycle import cull_obsolete
    n = cull_obsolete()
    print(f"Culled {n} skills")
    return 0


# === v1.8.0: garbage-collect ===

def _file_age_days(path: str) -> float:
    """Return age of file in days (mtime)."""
    import time
    return (time.time() - os.path.getmtime(path)) / 86400.0


def cmd_gc(arxiv_max_age: int, history_archive_rows: int, dry_run: bool,
           memory_policy=None) -> int:
    """Garbage-collect runtime data.

    - arxiv_cache/ : delete pkl files older than --arxiv-cache-max-age-days
                     (default 30; 0 = delete all)
    - s2_cache/     : same rule
    - gh_cache/     : same rule
    - pwc_cache/    : same rule
    - __pycache__/  : always delete (Python rebuilds on import)
    - *.bench_bak / *.bench_tmp : always delete (transient)
    - history.db    : if --archive-history-older-than-rows > 0, archive
                     the oldest N rows to upgrades/history_archive_<ts>.json

    Default behavior (no flags) is conservative: 30-day cache TTL +
    no history archive.  Use --dry-run to see what would be deleted.
    """
    upgraded = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "upgrades",
    )
    if not os.path.exists(upgraded):
        print(f"upgrades/ does not exist ({upgraded})")
        return 0

    verb = "would delete" if dry_run else "deleted"
    n_files = 0
    n_bytes = 0

    # 1. Cache directories: arxiv_cache, s2_cache, gh_cache, pwc_cache
    cache_dirs = ["arxiv_cache", "s2_cache", "gh_cache", "pwc_cache"]
    for sub in cache_dirs:
        sub_path = os.path.join(upgraded, sub)
        if not os.path.exists(sub_path):
            continue
        for f in os.listdir(sub_path):
            full = os.path.join(sub_path, f)
            if not os.path.isfile(full):
                continue
            age = _file_age_days(full)
            keep = (arxiv_max_age > 0 and age < arxiv_max_age)
            if not keep:
                size = os.path.getsize(full)
                if not dry_run:
                    os.remove(full)
                n_files += 1
                n_bytes += size
                print(f"  {verb}: {sub}/{f} ({age:.1f}d, {size}B)")

    # 2. __pycache__ directories everywhere in repo
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for root, dirs, files in os.walk(project_root):
        # Skip .git, upgrades
        if ".git" in root or root.startswith(upgraded):
            continue
        for d in list(dirs):
            if d == "__pycache__":
                pycache = os.path.join(root, d)
                size = sum(
                    os.path.getsize(os.path.join(pycache, f))
                    for f in os.listdir(pycache)
                    if os.path.isfile(os.path.join(pycache, f))
                )
                if not dry_run:
                    import shutil
                    shutil.rmtree(pycache)
                n_files += 1
                n_bytes += size
                print(f"  {verb}: {pycache[len(project_root)+1:]} ({size}B)")
                dirs.remove(d)

    # 3. Sandbox residue
    for pattern in (".bench_bak", ".bench_tmp", ".v17_test_bak",
                    ".stress_bak", ".e2e_test_bak", ".test_bak"):
        for root, dirs, files in os.walk(project_root):
            if ".git" in root or root.startswith(upgraded):
                continue
            for f in files:
                if f.endswith(pattern):
                    full = os.path.join(root, f)
                    size = os.path.getsize(full)
                    if not dry_run:
                        os.remove(full)
                    n_files += 1
                    n_bytes += size
                    print(f"  {verb}: {full[len(project_root)+1:]} ({size}B)")

    # 4. history.db archive (if requested)
    if history_archive_rows > 0:
        import sqlite3
        hist_db = os.path.join(upgraded, "history.db")
        if os.path.exists(hist_db):
            conn = sqlite3.connect(hist_db)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM upgrades")
            n_total = c.fetchone()[0]
            if n_total > history_archive_rows:
                c.execute(
                    "SELECT id, decision, notes FROM upgrades ORDER BY id ASC LIMIT ?",
                    (n_total - history_archive_rows,),
                )
                old_rows = c.fetchall()
                conn.close()
                import datetime
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                arch_path = os.path.join(
                    upgraded, f"history_archive_{ts}.json")
                with open(arch_path, "w") as f:
                    json.dump(
                        {"archived_at": ts, "rows": [
                            {"id": r[0], "decision": r[1], "notes": r[2]}
                            for r in old_rows
                        ]},
                        f, indent=2,
                    )
                print(f"  archived {len(old_rows)} old rows to {arch_path}")
                if not dry_run:
                    # Delete the archived rows from main db
                    conn = sqlite3.connect(hist_db)
                    c = conn.cursor()
                    c.execute(
                        "DELETE FROM upgrades WHERE id <= ?",
                        (old_rows[-1][0],),
                    )
                    conn.commit()
                    conn.close()
                    n_files += 1
            else:
                conn.close()

    # 5. learning.db seen_papers (v1.8.1: 奥卡姆-涌现 — no hand-coded policy)
    # Default policy is noop.  LLM can install a smarter one via patchgen
    # editing apply_memory_policy() in src/learning.py.
    try:
        from src.learning import init_db, apply_memory_policy, MAX_LEARNING_ROWS
        learn_db = os.path.join(upgraded, "learning.db")
        if os.path.exists(learn_db):
            conn = init_db(learn_db)
            try:
                # If user passed --memory-policy, load it
                policy_fn = None
                if memory_policy:
                    try:
                        mod_name, fn_name = memory_policy.split(":", 1)
                        import importlib
                        mod = importlib.import_module(mod_name)
                        policy_fn = getattr(mod, fn_name)
                    except Exception as e:
                        print("  warning: --memory-policy load failed: %s" % e)
                        policy_fn = None

                if dry_run and memory_policy:
                    print("  dry-run: would apply policy %s" % memory_policy)
                    result = {"policy": "noop", "before": 0, "after": 0, "deleted": 0}
                else:
                    result = apply_memory_policy(conn, policy_fn)  # default = noop
                if result.get("hard_ceiling_fired"):
                    print("  seen_papers: hard ceiling fired — "
                          "deleted %d rows (now at %d, ceiling %d). "
                          "Install a smarter policy via patchgen."
                          % (result["deleted"], result["after"], MAX_LEARNING_ROWS))
                elif result["deleted"] > 0:
                    print("  seen_papers: policy %s deleted %d rows (%d -> %d)"
                          % (result["policy"], result["deleted"],
                             result["before"], result["after"]))
                else:
                    print("  seen_papers: %d rows (no policy active yet — "
                          "patchgen can install one)" % result["before"])
            finally:
                conn.close()
    except Exception as e:
        print(f"  seen_papers check failed (non-fatal): {e}")

    prefix = "would be " if dry_run else ""
    print(f"Total: {n_files} files {prefix}deleted, {n_bytes} bytes")
    return 0


def cmd_audit(limit: int, run_now: bool) -> int:
    """Show audit history, or run audit now.

    --run    : run a one-off audit (uses node_skill_audit logic)
    --limit N: show last N audit runs (default 10)
    """
    import os as _os
    db_path = _os.path.join(
        _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
        "upgrades", "history.db",
    )
    if run_now:
        # Run a one-off audit using the same logic as the pipeline node
        from src.db import UpgradeHistory
        from src.skill_lifecycle import evaluate_all_skills_static
        if not _os.path.exists(db_path):
            print(f"No history.db at {db_path} — nothing to audit")
            return 0
        h = UpgradeHistory(db_path)
        try:
            result = evaluate_all_skills_static(h, cull_threshold=0.0)
            culled = []
            for skill_name, info in result.items():
                if info["action"] == "culled":
                    h.archive_skill(skill_name)
                    culled.append(skill_name)
            # Persist to audit_history
            h.record_audit(
                n_skills=len(result),
                n_culled=len(culled),
                n_kept=len(result) - len(culled),
                details=result,
            )
        finally:
            h.close()
        print(f"Audit: {len(result)} skills evaluated, {len(culled)} culled")
        for n in culled:
            print(f"  culled: {n}")
        return 0

    # Show history
    if not _os.path.exists(db_path):
        print(f"No history.db at {db_path}")
        print("Run a round first: python -m self_upgrade evolve --live")
        return 0
    from src.db import UpgradeHistory
    h = UpgradeHistory(db_path)
    try:
        rows = h.get_audit_history(limit=limit)
    finally:
        h.close()
    if not rows:
        print("No audit history yet.")
        print("Audits happen automatically each round (or run one now:")
        print("  python -m self_upgrade audit --run")
        return 0
    print(f"Last {len(rows)} audit runs:")
    print()
    for r in rows:
        print(
            f"  id={r['id']} at={r['audited_at'][:19]} "
            f"skills={r['n_skills']} culled={r['n_culled']} kept={r['n_kept']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
