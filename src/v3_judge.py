"""src/v3_judge.py - select the best paper from a list of summaries.

This is v3.0.1 step 1.1: deterministic mock only.  The real
LLM-as-judge (step 1.2) will use select_best() to call the LLM.

Why start with a mock?
  - Per P17 honest reporting: don't claim green when yellow.
  - Per LITERATURE: LLM judges are noisy (temperature); the
    mock gives us a reliable baseline to compare against.
  - Per user workflow (2026-07-09): '先测通小功能, 再联合成
    大功能继续测, 一步一步确认功能'.  Mock is the smallest
    piece; test it before adding LLM.

Public API:
  select_best_mock(summaries, ranking_fn=None) -> PaperSummary
  EmptySummariesError                              -> exception
"""
from typing import Callable, List, Optional

from src.v3_multipaper import PaperSummary


class EmptySummariesError(Exception):
    """Raised when select_best_mock is called with an empty list."""
    pass


def _default_rank(summary: PaperSummary) -> float:
    """Default ranking: longer plan = better.  Pure heuristic.

    Rationale: a more detailed plan suggests the paper has more
    actionable insights for our v3.x design.  This is just a
    placeholder until the LLM judge arrives in step 1.2.
    """
    # Weight: plan * 2 (actionable), idea + viewpoint (1 each)
    return len(summary.plan) * 2 + len(summary.idea) + len(summary.viewpoint)


def select_best_mock(
    summaries: List[PaperSummary],
    ranking_fn: Optional[Callable[[PaperSummary], float]] = None,
) -> PaperSummary:
    """Pick the best summary from a list, using a ranking function.

    Args:
      summaries: list of PaperSummary (must be non-empty).
      ranking_fn: optional callable.  If None, uses _default_rank
        (length-based heuristic).

    Returns:
      The PaperSummary with the highest rank.  In case of ties,
      returns the FIRST one in the input list (stable sort).

    Raises:
      EmptySummariesError if summaries is empty.
    """
    if not summaries:
        raise EmptySummariesError(
            "select_best_mock requires at least one summary"
        )

    fn = ranking_fn if ranking_fn is not None else _default_rank
    ranked = sorted(summaries, key=fn, reverse=True)
    # stable sort: tied ranks preserve input order
    return ranked[0]


def is_mock() -> bool:
    """Sanity check: returns True if this module is the mock.

    Used by callers to verify they're running the mock, not the
    real LLM judge (which doesn't exist yet in step 1.1).
    """
    return True