#!/usr/bin/env python3
"""Self-Upgrade Agent — 通过论文搜索、代码生成、benchmark 评估来自主改进自身。

Pipelines:
    default  — LangGraph pipeline (research → filter → patchgen → sandbox → reflect → benchmark → decide)
    --legacy — 旧 pipeline (skillgen 路径，仅供兼容)

Usage:
    python run.py              # 运行默认 pipeline (dry-run: 跳过真实 benchmark)
    python run.py --live       # 真实评估 (LLM + benchmark)
    python run.py --legacy     # 使用旧版 pipeline
    python run.py --stats      # 查看升级历史
    python run.py --cull       # 修剪低效 skill
    python run.py --config PATH
    python run.py -v
"""
import argparse
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


def _print_pipeline_lg_result(state: dict):
    """Format and print the result of a pipeline_lg run."""
    papers = state.get("papers", [])
    scored = state.get("scored", [])
    patch = state.get("patch", {})
    ev = state.get("eval", {})
    dec = state.get("dec", {})
    errors = state.get("errors", [])
    best = state.get("c")

    print("\n" + "=" * 50)
    print("PIPELINE RESULT (LangGraph)")
    print("=" * 50)
    print(f"Papers found:      {len(papers):>4d}")
    print(f"Papers qualified:  {len(scored):>4d}")
    print(f"Sandbox passed:    {'YES' if state.get('ok') else 'NO'}")
    print(f"Reflect attempts:  {state.get('ra', 0):>4d}")

    if ev:
        print(f"\nEvaluation:")
        print(f"  Baseline rate:   {ev.get('br', 0):.3f}")
        print(f"  Upgraded rate:   {ev.get('ur', 0):.3f}")
        print(f"  Delta:           {ev.get('d', 0):+.3f}")
        print(f"  Cost ratio:      {ev.get('cr', 1.0):.2f}x")

    if dec:
        decision = dec.get("decision", "pending")
        symbol = "+" if decision == "keep" else "-"
        print(f"\nDecision: {symbol} {decision.upper()}")
        for reason in dec.get("reasons", []):
            print(f"  -> {reason}")

    if best and hasattr(best, 'paper'):
        p = best.paper
        print(f"\nPaper: {p.title[:80]}")
        print(f"  arXiv: {p.arxiv_id}")
        print(f"  Score: {best.total_score:.1f}")
        if patch:
            print(f"  Patch target: {patch.get('module', 'planner.py')}")
            print(f"  Code size:    {len(patch.get('function', ''))} chars")
            print(f"  Test size:    {len(patch.get('test', ''))} chars")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  ! {e}")

    if not papers:
        print("\n(No papers found — nothing to upgrade)")

    print("\nTip: Run `python run.py --stats` to see full upgrade history.")


def main():
    parser = argparse.ArgumentParser(
        description="Self-Upgrade Agent — 通过论文搜索自主改进自身代码"
    )
    parser.add_argument(
        "--live", action="store_true",
        help="真实评估模式（启用 LLM benchmark，否则用模拟数据快速验证）"
    )
    parser.add_argument(
        "--legacy", action="store_true",
        help="使用旧版 pipeline（skillgen 路径，仅供兼容）"
    )
    parser.add_argument(
        "--cull", action="store_true",
        help="归档低效/过期 skill"
    )
    parser.add_argument(
        "--evaluate-skills", action="store_true",
        help="重新评估所有活跃 skill"
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="显示升级历史统计"
    )
    parser.add_argument(
        "--config", default="config.yaml",
        help="配置文件路径 (default: config.yaml)"
    )
    parser.add_argument(
        "--version", action="store_true",
        help="显示版本信息"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="DEBUG 级别日志"
    )
    parser.add_argument(
        "--schedule", action="store_true",
        help="输出 crontab 调度配置"
    )
    parser.add_argument(
        "--daemon", action="store_true",
        help="后台守护模式，每 24h 自动运行"
    )
    parser.add_argument(
        "--promote", type=str, default=None, metavar="PATCH_NAME",
        help="手动将候选补丁提升为活跃版本"
    )

    args = parser.parse_args()

    if args.version:
        print("Self-Upgrade Agent v1.1.0 (2026-06-30)")
        print("Autonomous agent improvement via paper discovery and code patching.")
        import importlib
        for mod_name in ["core", "src.pipeline_lg"]:
            try:
                m = importlib.import_module(mod_name)
                v = getattr(m, "__version__", "unknown")
                print(f"  {mod_name}: v{v}")
            except Exception:
                pass
        return

    # ═══ Initialize logging first (used by all code paths) ═══
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    if args.daemon:
        import threading, time as _time
        import json as _json
        import traceback

        state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "upgrades", "daemon_state.json")
        os.makedirs(os.path.dirname(state_file), exist_ok=True)

        def _save_state(status, error=None):
            try:
                with open(state_file, "w") as f:
                    _json.dump({"last_run": _time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "status": status, "error": error}, f)
            except Exception:
                pass

        logger.info("Daemon mode: running pipeline every 24h")
        consecutive_failures = 0

        def daily():
            nonlocal consecutive_failures
            while True:
                try:
                    logger.info("Daemon: starting pipeline run")
                    if args.legacy:
                        from src.pipeline import run_pipeline as run_p
                        run_p(load_config(args.config), verbose=args.verbose)
                    else:
                        from src.pipeline_lg import run as run_plg
                        run_plg(load_config(args.config))
                    _save_state("success")
                    consecutive_failures = 0
                except Exception as e:
                    consecutive_failures += 1
                    logger.error(f"Pipeline error (failure #{consecutive_failures}): {e}")
                    logger.debug(traceback.format_exc())
                    _save_state("error", str(e))
                    if consecutive_failures >= 3:
                        logger.warning("3 consecutive failures — skipping this cycle")
                        consecutive_failures = 0
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

    if args.schedule:
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
            print()
            for name, reason in archived:
                print(f"  - {name}: {reason}")
        else:
            print("No skills needed archiving.")
        history.close()
        return

    if args.promote:
        from src.switcher import promote_candidate, get_active_skills, get_module_versions
        result = promote_candidate(args.promote)
        print(f"Promote {args.promote}: {result['status']}")
        if result.get('backup'):
            print(f"Backup: {result['backup']}")
        if result.get('target_module'):
            print(f"Target: core/{result['target_module']}")
        print()
        # Show core module versions
        versions = get_module_versions()
        print("Core module versions:")
        for name, info in versions.items():
            status = "EXISTS" if info["exists"] else "MISSING"
            promoted = info.get("last_promoted", "never")[:19]
            print(f"  core/{name}: {status} ({info['size']} bytes)")
            if info.get("last_promoted"):
                print(f"    Last patched: {promoted} via {info.get('last_skill', 'N/A')}")
        print()
        active = get_active_skills()
        print(f"Legacy active skills: {list(active.keys())}")
        history.close()
        return

    if args.evaluate_skills:
        from src.skill_lifecycle import evaluate_all_skills
        print("Re-evaluating all active skills...")
        results = evaluate_all_skills(history, config=config.evaluate)
        print(f"Evaluation complete: {len(results)} skills")
        for name, delta in sorted(results.items(), key=lambda x: x[1], reverse=True):
            print(f"  {delta:+.2%}  {name}")
        history.close()
        return

    # ═══ Run pipeline ═══
    if args.legacy:
        # ── Legacy pipeline (skillgen path) ──
        from src.pipeline import run_pipeline

        logger.info("Starting legacy pipeline (skillgen path)...")
        legacy_result = run_pipeline(config=config, dry_run=not args.live)

        print("\n" + "=" * 50)
        print("PIPELINE RESULT (Legacy)")
        print("=" * 50)
        print(f"Papers found:      {legacy_result.papers_found:>4d}")
        print(f"Papers qualified:  {legacy_result.papers_qualified:>4d}")
        print(f"Skills generated:  {legacy_result.skills_generated:>4d}")
        print(f"Upgrades kept:     {legacy_result.upgrades_kept:>4d}")
        print(f"Upgrades reverted: {legacy_result.upgrades_reverted:>4d}")

        if legacy_result.errors:
            print(f"\nErrors ({len(legacy_result.errors)}):")
            for e in legacy_result.errors:
                print(f"  ! {e}")

        if legacy_result.details:
            print("\nDetails:")
            for d in legacy_result.details:
                symbol = "+" if d["decision"] == "keep" else "-"
                print(f"  {symbol} [{d['decision']:>7s}] {d['paper_title'][:60]}")
                print(f"      Skill: {d['skill_name']}")
                print(f"      Score: {d['total_score']:.1f}  |  "
                      f"Δ={d['metrics']['success_rate_delta']:+.3f}  |  "
                      f"Cost:{d['metrics']['cost_increase_ratio']:.2f}x")
                for r in d["reasons"]:
                    print(f"      -> {r}")

        print("\nTip: Run `python run.py --stats` to see full upgrade history.")
    else:
        # ── Default pipeline (patchgen path via LangGraph) ──
        from src.pipeline_lg import run as run_pipeline_lg

        logger.info("Starting self-upgrade pipeline (LangGraph)...")
        if not args.live:
            logger.info("Dry-run mode: benchmark will use simulated data on failure")

        state = run_pipeline_lg(config)
        _print_pipeline_lg_result(state)

    history.close()


if __name__ == "__main__":
    main()
