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
    from src.v2_agent import FIXED_PAPER, Paper
    return run_one_round, run_one_round_multi, replay_all_failures, FIXED_PAPER, Paper


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
              help="Paper arxiv_id (default: FIXED_PAPER = DyLAN 2310.02170).")
@click.option("--test-path", default="tests/test_pipeline.py",
              help="Test path used as the decision gate.")
@click.pass_obj
def improve(obj, target, paper, test_path):
    """Run one round of self-improvement (generate + apply + decide)."""
    run_one_round, _, _, FIXED_PAPER, Paper = _lazy_v2()
    if obj["mock"]:
        click.echo("ERROR: --mock not yet supported for 'improve'. "
                   "Use 'test-scale' for now.", err=True)
        sys.exit(1)
    if paper is None:
        paper = FIXED_PAPER
    else:
        paper = Paper(arxiv_id=paper, title=paper, abstract="(manual)")
    r = run_one_round(paper=paper, target_module=target, test_path=test_path)
    click.echo(_format_round_result(r))


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
    _, _, replay_all_failures, _, _ = _lazy_v2()
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
    run_one_round, _, _, FIXED_PAPER, Paper = _lazy_v2()
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


@cli.command(name="improve-harness")
@click.option("--target", default="core/planner.py",
              help="Target module (default: core/planner.py).")
@click.option("--test-path", default="tests/test_v2_round.py",
              help="Test path used as the decision gate.")
@click.option("--max-retries", default=2, type=int,
              help="How many times to retry on failure (default 2).")
@click.option("--count", default=1, type=int,
              help="Run N consecutive harness rounds (default 1).")
@click.pass_obj
def improve_harness(obj, target, test_path, max_retries, count):
    """Harness-wrapped self-improvement (v3.0.2 follow-up).

    Per LITERATURE (Self-Harness 40->62%): iterative re-plan on
    failure.  Wraps run_one_round_multi in a Loop with retry-on-fail.
    Per P7 奥卡姆: simple retry wrapper.

    --count N: run N consecutive rounds (each is a fresh harness
    with its own retries).  Useful for stability testing.
    """
    from src.v2_round import run_one_round_with_harness
    from src.llm import LLMConfig
    config = LLMConfig.from_env() if obj["mock"] is False else None
    kept_count = 0
    for i in range(count):
        if count > 1:
            click.echo(f"===== Round {i + 1}/{count} =====")
        r = run_one_round_with_harness(
            target_module=target,
            config=config,
            max_retries=max_retries,
            test_path=test_path,
        )
        click.echo(_format_round_result(r))
        if r.decision == "KEPT":
            kept_count += 1
    if count > 1:
        click.echo(f"===== Summary =====")
        click.echo(f"KEPT: {kept_count}/{count} ({100*kept_count//count}%)")
    sys.exit(0 if kept_count == count else 1)


@cli.command(name="improve-multi")
@click.option("--target", default="core/planner.py",
              help="Target module (default: core/planner.py).")
@click.option("--test-path", default="tests/test_v2_round.py",
              help="Test path used as the decision gate.")
@click.option("--no-judge-llm/--judge-llm", default=True,
              help="Whether to use LLM for paper selection (mock if off).")
@click.option("--count", default=1, type=int,
              help="Run N consecutive multi-paper rounds (default 1).")
@click.pass_obj
def improve_multi(obj, target, test_path, no_judge_llm, count):
    """Multi-paper self-improvement (v3.0.1 step 1.4).

    Reads all papers from the catalog, uses LLM (or mock) to pick
    the best one, then runs the standard self-improvement loop
    on that paper.  Intermediate results are persisted per P19.

    --count N: run N consecutive rounds (useful for stability testing).
    """
    _, run_one_round_multi, _, _, _ = _lazy_v2()
    from src.llm import LLMConfig
    config = LLMConfig.from_env() if obj["mock"] is False else None
    llm_config = config if no_judge_llm else None
    kept_count = 0
    for i in range(count):
        if count > 1:
            click.echo(f"===== Round {i + 1}/{count} =====")
        r = run_one_round_multi(
            target_module=target,
            config=config,
            llm_config=llm_config,
            test_path=test_path,
        )
        click.echo(_format_round_result(r))
        click.echo(f"Decision source: "
                   f"{'llm' if no_judge_llm else 'mock'} (judge)")
        if r.decision == "KEPT":
            kept_count += 1
    if count > 1:
        click.echo(f"===== Summary =====")
        click.echo(f"KEPT: {kept_count}/{count} ({100*kept_count//count}%)")
    sys.exit(0 if kept_count == count else 1)


def main():
    """Module entry point."""
    cli()


if __name__ == "__main__":
    main()