"""self_upgrade - unified CLI for the self-upgrade agent.

Per user feedback 2026-07-08: 'need unified management, can run
self-improvement, can use specifically, can keep project clean'.

This file is the unified CLI.  It uses Click and exposes:
  - improve:        one round with FIXED_PAPER (single paper)
  - replay:         replay failure log (P18)
  - test-scale:     N consecutive rounds (debug / load test)
  - improve-multi:  multi-paper selection + 1 round (v3.0.1)

Usage:
  python -m self_upgrade improve --target core/planner.py
  python -m self_upgrade replay
  python -m self_upgrade test-scale 5
  python -m self_upgrade improve-multi --target core/planner.py
  python -m self_upgrade --help
"""
import os
import sys
import json
import time

import click

# Lazy imports: tests and scripts that touch this module shouldn't
# trigger LLMConfig / v2 module loading at import time.

def _lazy_v2():
    from src.v2_round import run_one_round, run_one_round_multi, replay_all_failures
    from src.v2_round import run_one_round_with_harness
    from src.v2_agent import FIXED_PAPER, Paper
    return (run_one_round, run_one_round_multi, replay_all_failures,
            run_one_round_with_harness, FIXED_PAPER, Paper)


def _format_round_result(r) -> str:
    """One-line summary of a RoundResult."""
    return (f"decision={r.decision} elapsed={r.elapsed_s:.1f}s "
            f"tests_passed={r.tests_passed} tests_failed={r.tests_failed} "
            f"target={r.target_module}"
            + (f" error={r.error[:80]}" if r.error else ""))


def _do_auto_commit(target, r, multi):
    """Per user 2026-07-10: '区分开自动更新和手动更新'.

    When --auto-commit is set and round KEPT, commit the patched file
    with author 'Auto Upgrade <auto@self-upgrade.local>' and [auto]
    prefix.  Also write a patch bundle to upgrades/auto-patches/ for
    human review / selective apply / rejection.

    Per P7 奥卡姆: helper function, not a new abstraction.  Per
    P22 找共性: reuses v3_persist's save pattern (write to disk).
    Per P18: only commits KEPT (atomic + tested).
    """
    from src.v3_auto_commit import write_patch_bundle, auto_commit
    bundle = write_patch_bundle(target)
    paper_id = ""
    # Extract paper id if available
    if hasattr(r, "paper") and r.paper:
        paper_id = getattr(r.paper, "arxiv_id", "") or str(r.paper)
    commit_hash = auto_commit(
        target_module=target,
        paper_id=paper_id,
        tests_passed=getattr(r, "tests_passed", 0),
        bundle_path=bundle,
    )
    if commit_hash:
        click.echo(f"  [auto-commit] {commit_hash[:8]} by Auto Upgrade")
        click.echo(f"  [auto-commit] bundle: {bundle or '(no diff)'}")
    else:
        click.echo("  [auto-commit] FAILED (see git error above)")


@click.group()
@click.option("--mock/--no-mock", default=False,
              help="Use mocked LLM (no network, fast).")
def cli(mock):
    """self-upgrade-agent: a self-improving agent for code generation."""
    ctx = click.get_current_context()
    ctx.obj = {"mock": mock}


@cli.command()
@click.option("--target", default="core/planner.py",
              help="Target module to improve (default: core/planner.py).")
@click.option("--paper", default=None,
              help="Specific paper arxiv_id (single-paper mode only).")
@click.option("--test-path", default=None,
              help="Test path to run (default: tests/test_v2_round.py if --multi).")
@click.option("--multi/--single", default=True,
              help="Multi-paper (LLM judge, default) or single paper (--paper).")
@click.option("--max-retries", default=2, type=int,
              help="Harness retries on NO_PATCH/REVERTED (default: 2).")
@click.option("--count", default=1, type=int,
              help="Run N consecutive rounds (default: 1).")
@click.option("--auto-commit/--no-auto-commit", default=False,
              help="Auto-commit KEPT patches with [auto] author (default: no).")
@click.option("--interval", default=0, type=int,
              help="Seconds between rounds (default: 0; only used with --count > 1).")
@click.option("--mock/--no-mock", default=False,
              help="Use mock LLM (no API call, default: real LLM).")
@click.pass_obj
def improve(obj, target, paper, test_path, multi, max_retries, count,
            auto_commit, interval, mock):
    """Run one round of self-improvement (with flags).

    Default: multi-paper mode, harness with 2 retries.  Use --single
    for a specific paper (with --paper), or --mock for offline tests.

    Examples:
      improve                                    # 1 round multi, 2 retries
      improve --single --paper 2310.02170        # specific paper
      improve --count 5 --interval 0             # 5 rounds back-to-back
      improve --auto-commit                      # auto-commit KEPT with [auto]
    """
    if test_path is None:
        test_path = "tests/test_v2_round.py" if multi else "tests/test_pipeline.py"

    run_one_round, run_one_round_multi, _, run_with_harness, FIXED_PAPER, Paper = _lazy_v2()

    if mock and not multi:
        click.echo("ERROR: --mock not yet supported for single-paper 'improve'. "
                   "Use --multi (mock judge) instead.", err=True)
        sys.exit(1)

    kept_count = 0
    last_paper_id = ""
    for i in range(count):
        if count > 1:
            click.echo(f"===== Round {i + 1}/{count} =====")

        if multi:
            # Multi-paper mode (LLM or mock judge + retry-on-fail harness)
            from src.llm import LLMConfig
            config = LLMConfig.from_env() if not mock else None
            r = run_with_harness(
                target_module=target,
                config=config,
                max_retries=max_retries,
                test_path=test_path,
            )
        else:
            # Single-paper mode
            if paper is None:
                p = FIXED_PAPER
            else:
                p = Paper(arxiv_id=paper, title=paper, abstract="(manual)")
            r = run_one_round(paper=p, target_module=target,
                              test_path=test_path)

        click.echo(_format_round_result(r))
        if hasattr(r, "decision") and r.decision == "KEPT":
            kept_count += 1
            # Per user 2026-07-10: '区分开自动更新和手动更新'
            if auto_commit:
                _do_auto_commit(target, r, multi)
        elif auto_commit and hasattr(r, "decision") and r.decision in ("REVERTED", "APPLY_FAILED"):
            # Auto-commit was attempted but round failed: nothing to commit.
            click.echo("  [auto-commit skipped: round did not KEPT]")

        # Back-to-back: sleep between rounds if count > 1 and not last
        if count > 1 and i < count - 1 and interval > 0:
            click.echo(f"  Sleeping {interval}s... (Ctrl-C to stop)")
            time.sleep(interval)

    if count > 1:
        click.echo(f"===== Summary =====")
        click.echo(f"KEPT: {kept_count}/{count} ({100*kept_count//count}%)")
    sys.exit(0 if (count == 1 and hasattr(r, "decision") and r.decision == "KEPT")
                  or (count > 1 and kept_count == count) else 1)


@cli.command()
@click.option("--live/--no-live", default=False,
              help="If --live, actually replay (slow, real LLM). Default is "
                   "inspect (fast, no LLM) per user feedback 2026-07-10 "
                   "'跑的时候卡了 5+ min'.")
def replay(live):
    """Replay (or inspect) failures from upgrades/failures.jsonl (P18).

    By default, just inspects the log (no LLM call).  Pass --live to
    actually replay each unique failure through run_one_round (slow).
    """
    if not live:
        # Fast: just inspect the log
        from src.v3_replay import inspect_failures, format_inspect
        insp = inspect_failures()
        click.echo(format_inspect(insp))
        return

    # Live: actually replay (slow)
    _, _, replay_all_failures, _, _, _ = _lazy_v2()
    report = replay_all_failures(test_path="tests/test_pipeline.py")
    click.echo(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))


@cli.command(name="test-scale")
@click.argument("n_rounds", type=int)
@click.option("--target", default="core/planner.py",
              help="Target module (default: core/planner.py).")
@click.option("--paper", default=None,
              help="Paper arxiv_id (default: FIXED_PAPER = DyLAN 2310.02170).")
@click.pass_obj
def test_scale(obj, n_rounds, target, paper):
    """Run N consecutive rounds (debug / load test / stability probe)."""
    run_one_round, _, _, _, FIXED_PAPER, Paper = _lazy_v2()
    if obj["mock"]:
        click.echo("ERROR: --mock not yet supported for 'test-scale'.",
                   err=True)
        sys.exit(1)
    if paper is None:
        paper = FIXED_PAPER
    else:
        paper = Paper(arxiv_id=paper, title=paper, abstract="(manual)")
    results = []
    t0 = time.time()
    for i in range(1, n_rounds + 1):
        click.echo(f"=== Round {i}/{n_rounds} ===")
        r = run_one_round(paper=paper, target_module=target,
                          test_path="tests/test_pipeline.py")
        results.append(r)
        click.echo(f"  {_format_round_result(r)}")
    total_t = time.time() - t0
    decisions = [r.decision for r in results]
    kept = decisions.count("KEPT")
    reverted = decisions.count("REVERTED")
    no_patch = decisions.count("NO_PATCH")
    apply_failed = decisions.count("APPLY_FAILED")
    click.echo()
    click.echo("=== SUMMARY ===")
    click.echo(f"Total elapsed: {total_t:.1f}s")
    click.echo(f"Decisions: {decisions}")
    click.echo(f"KEPT: {kept}/{n_rounds}  REVERTED: {reverted}/{n_rounds}  "
               f"NO_PATCH: {no_patch}/{n_rounds}  "
               f"APPLY_FAILED: {apply_failed}/{n_rounds}")
    if kept == n_rounds:
        click.echo("=> Loop is STABLE")
    elif kept == 0:
        click.echo("=> Loop is BLOCKED (LLM may need prompt fix)")
    else:
        click.echo("=> Loop is MIXED (LLM temperature is non-zero)")
    click.echo()
    click.echo("To restore core/planner.py if a round KEPT:")
    click.echo("  git checkout core/planner.py")


@cli.command(name="improve-harness", hidden=True)
@click.option("--target", default="core/planner.py")
@click.option("--test-path", default="tests/test_v2_round.py")
@click.option("--max-retries", default=2, type=int)
@click.option("--count", default=1, type=int)
@click.pass_obj
def improve_harness(obj, target, test_path, max_retries, count):
    """DEPRECATED: alias for `improve --multi --max-retries N`."""
    ctx = click.get_current_context()
    ctx.invoke(improve, target=target, test_path=test_path,
               multi=True, max_retries=max_retries, count=count)


@cli.command(name="improve-multi", hidden=True)
@click.option("--target", default="core/planner.py")
@click.option("--test-path", default="tests/test_v2_round.py")
@click.option("--no-judge-llm/--judge-llm", default=True)
@click.option("--count", default=1, type=int)
@click.pass_obj
def improve_multi(obj, target, test_path, no_judge_llm, count):
    """DEPRECATED: alias for `improve --multi`.  Kept for backward compat."""
    ctx = click.get_current_context()
    ctx.invoke(improve, target=target, test_path=test_path,
               multi=True, count=count)

@cli.command(name="daily-loop")
@click.option("--target", default="core/planner.py",
              help="Target module to improve (default: core/planner.py).")
@click.option("--interval", default=3600, type=int,
              help="Seconds between rounds (default: 3600 = 1h).")
@click.option("--max-rounds", default=None, type=int,
              help="Stop after N rounds (default: infinite, Ctrl-C to stop).")
@click.option("--multi/--single", default=True,
              help="Multi-paper (LLM judge, default) or single paper.")
@click.option("--max-retries", default=2, type=int,
              help="Harness retries per round (default: 2).")
@click.option("--test-path", default="tests/test_v2_round.py",
              help="Test path for decision gate (default: tests/test_v2_round.py).")
@click.option("--auto-commit/--no-auto-commit", default=False,
              help="Auto-commit KEPT patches with [auto] author (default: no).")
@click.option("--mock/--no-mock", default=False,
              help="Use mock LLM (no API call, default: real LLM).")
@click.option("--enable-ab/--no-ab", default=False,
              help="Enable A/B benchmark (per v3.3.0 MVP, statistical KEPT/REJECT).")
@click.pass_obj
def daily_loop(obj, target, interval, max_rounds, multi, max_retries,
               test_path, auto_commit, mock, enable_ab):
    """Autonomous daily loop: keep improving target forever (or until max-rounds).

    Per user vision 2026-07-08 '我希望这个项目之后可以自己独立运行':
    Runs rounds back-to-back, waiting `--interval` seconds between each.
    Stop with Ctrl-C.  All flags match the unified `improve` subcommand.

    Examples:
      python -m self_upgrade daily-loop                       # 1h interval, forever
      python -m self_upgrade daily-loop --interval 60         # 1 min (testing)
      python -m self_upgrade daily-loop --max-rounds 5        # 5 rounds then stop
      python -m self_upgrade daily-loop --target core/x.py    # different target
      python -m self_upgrade daily-loop --auto-commit         # auto-commit KEPT
    """
    run_one_round, run_one_round_multi, _, run_with_harness, _, _ = _lazy_v2()
    from src.llm import LLMConfig
    config = LLMConfig.from_env() if not mock else None

    # Per v3.3.0 sub-task 4/3: wire A/B benchmark into daily-loop CLI
    # When --enable-ab, use A/B-verified KEPT/REJECT decision (statistical)
    from src.ab_benchmark import run_tests as ab_run_tests
    ab_baseline = None
    if enable_ab:
        click.echo("[ab] A/B baseline tests...")
        ab_baseline = ab_run_tests(test_path, cwd=".")

    rounds = 0
    kept = 0
    rejected = 0
    try:
        while max_rounds is None or rounds < max_rounds:
            rounds += 1
            click.echo(f"\n===== Round {rounds} @ {time.strftime('%Y-%m-%d %H:%M:%S')} =====")
            if multi:
                r = run_with_harness(target_module=target, config=config,
                                     max_retries=max_retries, test_path=test_path)
            else:
                _, _, _, FIXED_PAPER, Paper = _lazy_v2()
                r = run_one_round_multi(target_module=target, config=config,
                                         llm_config=config, test_path=test_path)
            click.echo(_format_round_result(r))
            # Per v3.3.0 sub-task 4/3: A/B verification when --enable-ab
            if enable_ab and hasattr(r, "decision") and r.decision == "KEPT":
                from src.ab_benchmark import compare_runs
                ab_candidate = ab_run_tests(test_path, cwd=".")
                comparison = compare_runs(ab_baseline or {"passed": 0, "failed": 0, "elapsed_sec": 0}, ab_candidate)
                if comparison["decision"] == "regression":
                    click.echo(f"[ab] REGRESSION detected: {comparison['reason']}")
                    r.decision = "REJECT"
                else:
                    click.echo(f"[ab] confirmed: {comparison['reason']}")
            if hasattr(r, "decision") and r.decision == "KEPT":
                kept += 1
                # Per user 2026-07-10: '区分开自动更新和手动更新'
                if auto_commit:
                    _do_auto_commit(target, r, multi)
            elif hasattr(r, "decision") and r.decision == "REJECT":
                rejected += 1
            if max_rounds is None or rounds < max_rounds:
                click.echo(f"  Sleeping {interval}s... (Ctrl-C to stop)")
                time.sleep(interval)
    except KeyboardInterrupt:
        click.echo("\n[stopped by user]")

    click.echo(f"\n===== Daily loop done: {rounds} rounds, {kept} KEPT, {rejected} REJECT =====")
    sys.exit(0 if kept > 0 else 1)


@cli.command(name="cron")
@click.option("--install", "do_install", is_flag=True, default=False,
              help="Generate OS cron config (dry-run by default per P9).")
@click.option("--apply", "do_apply", is_flag=True, default=False,
              help="Actually write config to disk (CAUTION: real install).")
@click.option("--show", is_flag=True, default=False,
              help="Show the generated OS cron config (dry-run, no install).")
@click.option("--cron-expr", default="0 2",
              help="Cron expression 'H M' (default: 0 2 = 02:00 daily).")
@click.pass_obj
def cron(obj, do_install, do_apply, show, cron_expr):
    """v4.0.0 cron deployment (per 你 vision 2026-07-08).

    Per 自上而下/分治 (user meta-principle):
    - Big: SA v4.0.0 cron execution
    - Sub-task 2 (c7998fa): OS cron integration

    Per P9 hard rule: dry_run=True by default (safe).
    """
    from src.os_cron_installer import install_cron
    if not (do_install or show):
        click.echo("Use --show (dry-run) or --install --apply (real install). Try --help.")
        return
    dry_run = not do_apply
    result = install_cron(cron_expr=cron_expr, dry_run=dry_run)
    if show or dry_run:
        click.echo(f"OS: {result.get('os')}")
        click.echo(f"Config path: {result.get('config_path')}")
        click.echo(f"Dry run: {result.get('dry_run')}")
        click.echo("---")
        click.echo(result.get('config_content', ''))
        click.echo("---")
        click.echo(f"To install, run: {result.get('install_command')}")
    else:
        click.echo(f"Installed: {result.get('config_path')}")
        click.echo(f"Manual step: {result.get('install_command')}")


def main():
    """Module entry point."""
    cli()


if __name__ == "__main__":
    main()