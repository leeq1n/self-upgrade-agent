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


if __name__ == "__main__":
    sys.exit(main())
