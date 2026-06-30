#!/usr/bin/env python3
"""Self-Upgrade Agent — autonomous agent improvement via research.

Searches arXiv for latest papers, filters applicable innovations, generates
Hermes Agent skills, evaluates them via A/B benchmark, and decides whether
to keep or revert each upgrade.

Usage:
    python run.py              # Full pipeline (dry-run by default)
    python run.py --live       # Live evaluation (calls Hermes CLI)
    python run.py --stats      # Show upgrade history
    python run.py --config PATH  # Custom config path
    python run.py -v           # Verbose logging
"""
import argparse
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import run_pipeline, PipelineResult
from src.db import UpgradeHistory
from src.config import load_config


def show_stats(config_path: str):
    """Display upgrade history statistics."""
    config = load_config(config_path)
    history = UpgradeHistory(config.database.path)
    stats = history.get_stats()

    total = stats["total"] or 0
    print("\n=== Upgrade History ===")
    print(f"Total attempts:  {total}")
    print(f"Kept:            {stats['kept'] or 0}")
    print(f"Reverted:        {stats['reverted'] or 0}")
    print(f"Failed:          {stats['failed'] or 0}")
    print(f"Avg improvement: {stats['avg_delta'] or 0:.4f}")
    print()

    if total > 0:
        records = history.get_all()
        print(f"Latest {min(10, total)} upgrades:")
        print(f"  {'Decision':>8s} | {'Skill':>20s} | {'Delta':>6s} | Paper")
        print(f"  {'-'*8}-+-{'-'*20}-+-{'-'*6}-+-------")
        for r in records[:10]:
            delta = r.upgraded_success_rate - r.baseline_success_rate
            print(f"  {r.decision:>8s} | {r.skill_name:>20s} | {delta:+.3f} | "
                  f"{r.paper_title[:50]}")

    history.close()


def main():
    parser = argparse.ArgumentParser(
        description="Self-Upgrade Agent — autonomously improves through research"
    )
    parser.add_argument(
        "--live", action="store_true",
        help="Run live evaluation (calls Hermes CLI for benchmarks)"
    )
    parser.add_argument(
        "--cull", action="store_true",
        help="Archive underperforming/inactive skills"
    )
    parser.add_argument(
        "--evaluate-skills", action="store_true",
        help="Re-evaluate all active skills with LLM"
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="Show upgrade history statistics and exit"
    )
    parser.add_argument(
        "--config", default="config.yaml",
        help="Path to config file (default: config.yaml)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable DEBUG-level logging"
    )
    parser.add_argument(
        "--schedule", action="store_true",
        help="Print crontab entry for daily scheduling and exit"
    )
    parser.add_argument(
        "--daemon", action="store_true",
        help="Run pipeline every 24h in background (no external cron needed)"
    )
    parser.add_argument(
        "--promote", type=str, default=None, metavar="SKILL",
        help="Manually promote a candidate skill to active"
    )

    args = parser.parse_args()

    if args.daemon:
        import threading, time as _time
        logger.info("Daemon mode: running pipeline every 24h")
        def daily():
            while True:
                try:
                    run_pipeline(load_config(), verbose=args.verbose)
                except Exception as e:
                    logger.error(f"Pipeline error: {e}")
                logger.info("Next run in 24h...")
                _time.sleep(86400)
        t = threading.Thread(target=daily, daemon=True)
        t.start()
        try:
            while True:
                _time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Daemon stopped")
        return


    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.schedule:
        import os
        script_path = os.path.abspath(__file__)
        work_dir = os.path.dirname(script_path)
        print("Add this to your crontab (crontab -e):")
        print()
        print(f"0 2 * * * cd {work_dir} && python {script_path} >> upgrades/cron.log 2>&1")
        print()
        print("For Windows Task Scheduler:")
        print(f"  Action: python {script_path}")
        print(f"  Start in: {work_dir}")
        print(f"  Trigger: Daily at 2:00 AM")
        return
    if args.stats:
        show_stats(args.config)
        return

    config = load_config(args.config)
    history = UpgradeHistory(config.database.path)

    if args.cull:
        from src.skill_lifecycle import cull_obsolete
        archived = cull_obsolete(history, 
            max_active=config.lifecycle.max_active_skills,
            inactivity_days=config.lifecycle.inactivity_days)
        if archived:
            print("")
            for name, reason in archived:
                print(f"  - {name}: {reason}")
        else:
            print("No skills needed archiving.")
        history.close()
        return

    if args.promote:
        from src.switcher import promote_candidate, get_active_skills
        result = promote_candidate(args.promote)
        print(f"Promote {args.promote}: {result['status']}")
        if result.get('backup'):
            print(f"Backup: {result['backup']}")
        print()
        active = get_active_skills()
        print(f"Active skills: {list(active.keys())}")
        for name, info in active.items():
            has_code = 'code_path' in info
            print(f"  {name}: skill={len(info.get('skill_md',''))} chars, code={'yes' if has_code else 'no'}")
        history.close()
        return

    if args.evaluate_skills:
        from src.skill_lifecycle import evaluate_all_skills
        print("Re-evaluating all active skills...")
        results = evaluate_all_skills(history, config=config.evaluate)
        print("Evaluation complete: %d skills" % len(results))
        for name, delta in sorted(results.items(), key=lambda x: x[1], reverse=True):
            print(f"  {delta:+.2%}  {name}")
        history.close()
        return

    config = load_config(args.config)

    # Run pipeline
    config = load_config(args.config)
    logger = logging.getLogger(__name__)
    logger.info("Starting self-upgrade pipeline...")

    result = run_pipeline(
        config=config,
        dry_run=not args.live,
    )

    # Print summary
    print("\n" + "=" * 50)
    print("PIPELINE RESULT")
    print("=" * 50)
    print(f"Papers found:      {result.papers_found:>4d}")
    print(f"Papers qualified:  {result.papers_qualified:>4d}")
    print(f"Skills generated:  {result.skills_generated:>4d}")
    print(f"Upgrades kept:     {result.upgrades_kept:>4d}")
    print(f"Upgrades reverted: {result.upgrades_reverted:>4d}")

    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for e in result.errors:
            print(f"  ! {e}")

    if result.details:
        print(f"\nDetails:")
        for d in result.details:
            symbol = "+" if d["decision"] == "keep" else "-"
            print(f"  {symbol} [{d['decision']:>7s}] {d['paper_title'][:60]}")
            print(f"      Skill: {d['skill_name']}")
            print(f"      Score: {d['total_score']:.1f}  |  "
                  f"Δ={d['metrics']['success_rate_delta']:+.3f}  |  "
                  f"Cost:{d['metrics']['cost_increase_ratio']:.2f}x")
            for r in d["reasons"]:
                print(f"      -> {r}")

    print("\nTip: Run `python run.py --stats` to see full upgrade history.")


if __name__ == "__main__":
    main()
