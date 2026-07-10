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
              help="Paper arxiv_id (default: FIXED_PAPER = DyLAN 2310.02170). "
                   "Ignored when --multi is set.")
@click.option("--multi", is_flag=True, default=False,
              help="Use multi-paper selection (LLM judge picks best paper).")
@click.option("--max-retries", default=0, type=int,
              help="Retry up to N times on failure (default 0).")
@click.option("--count", default=1, type=int,
              help="Run N consecutive rounds (default 1).")
@click.option("--test-path", default=None,
              help="Test path used as the decision gate (default depends on mode).")
@click.pass_obj
def improve(obj, target, paper, multi, max_retries, count, test_path):
    """Run one round of self-improvement (generate + apply + decide).

    Modes (mutually compatible flags):
      (default)    Single paper, fixed DyLAN, no retry, 1 round.
      --multi      Multi-paper selection (LLM judge picks best paper).
      --max-retries N  Retry on failure (harness-style, per Self-Harness paper).
      --count N    Run N consecutive rounds (batch mode).

    Examples:
      python -m self_upgrade improve --target core/planner.py
      python -m self_upgrade improve --target core/planner.py --multi
      python -m self_upgrade improve --target core/planner.py --multi --max-retries 2
      python -m self_upgrade improve --target core/planner.py --multi --max-retries 2 --count 5
    """
    # Default test_path depends on mode
    if test_path is None:
        test_path = "tests/test_v2_round.py" if multi else "tests/test_pipeline.py"

    run_one_round, run_one_round_multi, _, run_with_harness, FIXED_PAPER, Paper = _lazy_v2()

    if obj["mock"] and not multi:
        click.echo("ERROR: --mock not yet supported for single-paper 'improve'. "
                   "Use --multi (mock judge) instead.", err=True)
        sys.exit(1)

    kept_count = 0
    for i in range(count):
        if count > 1:
            click.echo(f"===== Round {i + 1}/{count} =====")

        if multi:
            # Multi-paper mode (LLM or mock judge + retry-on-fail harness)
            from src.llm import LLMConfig
            config = LLMConfig.from_env() if obj["mock"] is False else None
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


def main():
    """Module entry point."""
    cli()


if __name__ == "__main__":
    main()