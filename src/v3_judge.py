"""src/v3_judge.py - select the best paper from a list of summaries.

v3.0.1 step 1.1: deterministic mock (`select_best_mock`).
v3.0.1 step 1.2: real LLM judge (`select_best`) with mock fallback.

Why start with a mock, then add LLM?
  - Per P17 honest reporting: don't claim green when yellow.
  - Per LITERATURE: LLM judges are noisy (temperature); the
    mock gives us a reliable baseline.
  - Per user workflow (2026-07-09): '先测通小功能, 再联合成
    大功能继续测, 一步一步确认功能'.

Fallback strategy (per fail-OPEN principle):
  - LLM returns non-JSON      -> fall back to mock
  - LLM returns unknown id    -> fall back to mock
  - LLM call raises exception -> fall back to mock
  - LLM returns empty string  -> fall back to mock
  - config is None            -> fall back to mock (no LLM)

Public API:
  select_best_mock(summaries, ranking_fn=None) -> PaperSummary
  select_best(summaries, config=None)          -> PaperSummary
  EmptySummariesError                          -> exception
"""
import json
import re
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


# ── Step 1.2: Real LLM judge with mock fallback ────────────────

# Pattern for the JSON we want the LLM to return:
#   {"best_arxiv_id": "self-harness", "reason": "..."}
# We use a regex (not full JSON parse) to be tolerant of slight
# variations like markdown code fences or trailing commas.
_LLM_JSON_PATTERN = re.compile(
    r'"best_arxiv_id"\s*:\s*"([^"]+)"',
)


def _build_judge_prompt(summaries: List[PaperSummary]) -> str:
    """Build the prompt that asks the LLM to pick the best paper.

    Format: a JSON object with `best_arxiv_id` and optional `reason`.
    """
    lines = [
        "You are selecting the most useful paper for a self-improving",
        "code agent.  Read the summaries below and reply with JSON:",
        '  {"best_arxiv_id": "<id>", "reason": "<one line>"}',
        "",
        "Summaries:",
        "",
    ]
    for i, s in enumerate(summaries, 1):
        lines.append(f"{i}. arxiv_id={s.paper_arxiv_id}")
        lines.append(f"   title: {s.title}")
        lines.append(f"   idea: {s.idea}")
        lines.append(f"   plan: {s.plan}")
        lines.append("")
    lines.append("Pick the most actionable plan.")
    return "\n".join(lines)


def _parse_llm_response(response_text: str) -> Optional[str]:
    """Extract best_arxiv_id from the LLM response.  Returns None
    if it can't be parsed (caller falls back to mock)."""
    if not response_text:
        return None
    m = _LLM_JSON_PATTERN.search(response_text)
    return m.group(1) if m else None


def _call_llm(prompt: str, config) -> str:
    """Call the LLM.  Returns response text.  Raises on failure.

    Lazy import: src.v2_agent is heavy (loads LLMConfig + reads
    .env).  Importing it eagerly would slow down the judge mock.
    """
    from src.v2_agent import _chat
    messages = [{"role": "user", "content": prompt}]
    response = _chat(messages=messages, config=config)
    return response.content


def select_best(
    summaries: List[PaperSummary],
    config=None,
) -> PaperSummary:
    """Pick the best summary from a list, using an LLM.

    Args:
      summaries: list of PaperSummary (must be non-empty).
      config: optional LLMConfig-like object.  If None, falls
        back to select_best_mock (no LLM call).

    Returns:
      The PaperSummary whose arxiv_id matches the LLM's choice.
      If the LLM response is unparseable or returns an unknown
      id, falls back to select_best_mock().

    Raises:
      EmptySummariesError if summaries is empty (consistent
      with select_best_mock).
    """
    if not summaries:
        raise EmptySummariesError(
            "select_best requires at least one summary"
        )
    # No config -> no LLM -> fall back to mock
    if config is None:
        return select_best_mock(summaries)

    # Build prompt and call LLM
    prompt = _build_judge_prompt(summaries)
    try:
        response_text = _call_llm(prompt, config)
    except Exception:
        # LLM call failed -> fall back to mock
        return select_best_mock(summaries)

    # Parse response
    chosen_id = _parse_llm_response(response_text)
    if chosen_id is None:
        return select_best_mock(summaries)

    # Find the chosen summary
    for s in summaries:
        if s.paper_arxiv_id == chosen_id:
            return s

    # LLM returned an unknown id -> fall back to mock
    return select_best_mock(summaries)