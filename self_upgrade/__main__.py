"""self_upgrade - unified CLI for the self-upgrade agent.

Per user feedback 2026-07-08: '需要统一管理的功能, 能跑自进化,
能具体使用, 能整理项目使其干净'.

This file replaces the v1.8.x unified CLI (backed up in
self_upgrade/__main__.v18_backup.py).  The new CLI uses Click
and exposes the v2.x system: improve (1 round), replay (P18
regression pipeline), test-scale N (debug / load test).

Usage:
  python -m self_upgrade improve --target core/planner.py
  python -m self_upgrade replay
  python -m self_upgrade test-scale 5
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
    from src.v2_round import run_one_round, replay_all_failures
    from src.v2_agent import FIXED_PAPER, Paper
    return run_one_round, replay_all_failures, FIXED_PAPER, Paper


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
    run_one_round, _, FIXED_PAPER, Paper = _lazy_v2()
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
def replay():
    """Replay every unique failure in upgrades/failures.jsonl (P18)."""
    _, replay_all_failures, _, _ = _lazy_v2()
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
    run_one_round, _, FIXED_PAPER, Paper = _lazy_v2()
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


def main():
    """Module entry point."""
    cli()


if __name__ == "__main__":
    main()