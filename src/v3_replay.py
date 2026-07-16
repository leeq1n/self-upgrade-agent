"""src/v3_replay.py - failure-log inspection (fast) vs replay (slow).

Per user feedback 2026-07-10: '跑的时候卡了 5+ min, 因为 replay
调真 LLM'.  P18 (Failure → regression test) has two modes:

  1. INSPECT (default, fast): read failures.jsonl and report
     signatures, decisions, error counts.  No LLM call.
  2. REPLAY (--live, slow): re-run each unique failure signature
     through run_one_round to see if it now passes.  Calls LLM.

The CLI exposes both via the `replay` subcommand.
"""
import os
import json
from collections import Counter
from typing import List, Optional

from src.failures import (
    read_failures, unique_failure_modes, DEFAULT_LOG,
)


def inspect_failures(log_path: str = DEFAULT_LOG) -> dict:
    """Read the failure log and return a summary.

    Fast: no LLM call.  Just reports what we already have on disk.
    """
    all_rows = read_failures(log_path=log_path)
    unique = unique_failure_modes(log_path=log_path)

    # Count by decision
    decisions = Counter(r.decision for r in all_rows)

    # Count by paper_arxiv_id
    papers = Counter(r.paper_arxiv_id for r in all_rows)

    # Recent entries
    recent = all_rows[-5:] if all_rows else []

    return {
        "log_path": log_path,
        "total_entries": len(all_rows),
        "unique_signatures": len(unique),
        "decisions": dict(decisions),
        "top_papers": dict(papers.most_common(5)),
        "recent": recent,
    }


def format_inspect(insp: dict) -> str:
    """Format inspect_failures() result as human-readable text."""
    lines = []
    lines.append("=== FAILURE LOG INSPECT (P18) ===")
    lines.append(f"Log path:           {insp['log_path']}")
    lines.append(f"Total entries:      {insp['total_entries']}")
    lines.append(f"Unique signatures:  {insp['unique_signatures']}")
    lines.append("")
    lines.append("Decisions breakdown:")
    for d, n in sorted(insp["decisions"].items(), key=lambda x: -x[1]):
        lines.append(f"  {d:20s} {n:4d}")
    lines.append("")
    if insp["top_papers"]:
        lines.append("Top papers (by failure count):")
        for p, n in insp["top_papers"].items():
            lines.append(f"  {p:30s} {n:4d}")
    lines.append("")
    if insp["recent"]:
        lines.append(f"Recent {len(insp['recent'])} entries:")
        for r in insp["recent"]:
            err = (r.error_first_line or "")[:60]
            lines.append(
                f"  {r.decision:12s} "
                f"{r.paper_arxiv_id:25s} "
                f"{r.target_module:30s} "
                f"{err}"
            )
    return "\n".join(lines)