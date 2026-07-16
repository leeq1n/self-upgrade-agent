"""Skill dashboard (per v3.2.0 dashboard sub-task, 1 commit).

Per LITERATURE Signal-to-Fix:
- Observability tool (fail-fast + dashboard together)
- Per P14 docs stay current: visualize state.json + skill metas

Per SKILLS.md spec:
- Lifecycle: candidate -> active -> archived -> superseded
- Visualize all states + counts

Per 自上而下/分治 (user 2026-07-11 meta-principle):
- Big task: skill lifecycle v3.2.0
- Sub-task 1-3 (done): metadata + promotion + archive
- Sub-task 4 (this commit): dashboard (visualization)
- Future sub-tasks: skill dashboard web UI, retention tuning

Per P23 doc-first: SKILLS.md spec existed.
Per P18: regression tests required.
"""
import json
from collections import Counter
from pathlib import Path


def list_skill_metas(upgrades_dir=None):
    """List all skill meta.json files (reuse skill_promotion logic)."""
    from src.skill_promotion import list_skill_metas as _list
    return _list(upgrades_dir)


def summarize_skills(upgrades_dir=None):
    """Summarize skill state (counts per status + per target).

    Returns dict with totals, by_status, by_target.
    """
    metas = list_skill_metas(upgrades_dir)
    by_status = Counter()
    by_target = Counter()
    for _, meta in metas:
        status = meta.get("status", "unknown")
        target = meta.get("target_module", "unknown")
        by_status[status] += 1
        by_target[target] += 1
    return {
        "total": len(metas),
        "by_status": dict(by_status),
        "by_target": dict(by_target),
    }


def render_dashboard(upgrades_dir=None, state_path=None, output_format="text"):
    """Render skill dashboard in text or JSON format.

    Per P14: dashboard shows current state (docs stay current).
    Per SKILLS.md: candidate/active/archived/superseded lifecycle.

    Returns: str (text format) or dict (json format)
    """
    skill_summary = summarize_skills(upgrades_dir)
    # Also show state.json summary
    from src.state_persistence import load_state
    state = load_state(state_path)
    state_summary = {
        "last_round_index": state.get("last_round_index"),
        "rounds_persisted": len(state.get("rounds", {})),
        "failures_recorded": len(state.get("failures", {})),
        "schema_version": state.get("schema_version"),
    }
    if output_format == "json":
        return {
            "skills": skill_summary,
            "state": state_summary,
        }
    # Text format
    lines = []
    lines.append("=== Skill Dashboard ===")
    lines.append(f"Total skills: {skill_summary['total']}")
    lines.append("By status:")
    for status, count in sorted(skill_summary["by_status"].items()):
        lines.append(f"  {status}: {count}")
    if skill_summary["by_target"]:
        lines.append("By target module:")
        # Sort by count DESC, then by name ASC (consistent ordering)
        for target, count in sorted(skill_summary["by_target"].items(),
                                    key=lambda x: (-x[1], x[0]))[:10]:
            lines.append(f"  {target}: {count}")
    lines.append("")
    lines.append("=== State ===")
    lines.append(f"last_round_index: {state_summary['last_round_index']}")
    lines.append(f"rounds_persisted: {state_summary['rounds_persisted']}")
    lines.append(f"failures_recorded: {state_summary['failures_recorded']}")
    lines.append(f"schema_version: {state_summary['schema_version']}")
    return "\n".join(lines)


def main():
    """CLI entry: render skill dashboard."""
    import argparse
    ap = argparse.ArgumentParser(prog="skill-dashboard")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    args = ap.parse_args()
    output = render_dashboard(output_format=args.format)
    if args.format == "json":
        print(json.dumps(output, indent=2))
    else:
        print(output)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())