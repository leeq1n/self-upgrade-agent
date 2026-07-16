"""src/v3_persist.py - persist multi-paper intermediate results.

Per user insight 2026-07-09: '如果有几个功能是顺序执行,
你可以先把前面的输出存下来, 作为下一个功能的输入'.

This module handles persistence between read_papers() and
select_best() so that:
  - Intermediate summaries are observable (cat the file)
  - Judgments can be replayed against the same input
  - Debugging is easy (which input led to which decision)
  - Future steps (v3.0.2+) can chain without re-parsing

File format: JSONL (append-only).  One PaperSummary per line.
Storage: upgrades/judge_summaries.jsonl + upgrades/judge_decisions.jsonl

Public API:
  save_summaries(summaries, path=...)     -> str  (returns path)
  read_summaries(path=...)                -> List[PaperSummary]
  save_decision(winner, summaries, ...)   -> str  (returns path)
  read_decisions(path=...)                -> List[DecisionRecord]
"""
import json
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Optional

from src.v3_multipaper import PaperSummary


# Default storage locations.  Per .gitignore, upgrades/* is
# runtime state and not tracked.
DEFAULT_SUMMARIES_PATH = os.path.join(
    "upgrades", "judge_summaries.jsonl"
)
DEFAULT_DECISIONS_PATH = os.path.join(
    "upgrades", "judge_decisions.jsonl"
)


@dataclass
class DecisionRecord:
    """One judgment event: which paper was chosen, with what input."""
    timestamp: float
    winner_arxiv_id: str
    winner_title: str
    num_input_summaries: int
    input_arxiv_ids: List[str]
    source: str  # "mock" | "llm" | "fallback"

    def to_dict(self):
        return asdict(self)


# ── Summaries persistence ───────────────────────────────────────

def save_summaries(
    summaries: List[PaperSummary],
    path: str = DEFAULT_SUMMARIES_PATH,
) -> str:
    """Persist a list of PaperSummary to a JSONL file.

    Each call OVERWRITES the file (single canonical snapshot).
    Returns the absolute path to the saved file.
    """
    abs_path = os.path.abspath(path)
    parent = os.path.dirname(abs_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        for s in summaries:
            f.write(json.dumps(s.to_dict(), ensure_ascii=False))
            f.write("\n")
    return abs_path


def read_summaries(
    path: str = DEFAULT_SUMMARIES_PATH,
) -> List[PaperSummary]:
    """Read PaperSummary objects back from a JSONL file.

    Skips malformed lines (with no exception) so a partial
    corruption doesn't crash the pipeline.  Returns an empty
    list if the file doesn't exist.
    """
    if not os.path.exists(path):
        return []
    out: List[PaperSummary] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                out.append(PaperSummary(
                    paper_arxiv_id=data.get("paper_arxiv_id", "unknown"),
                    title=data.get("title", ""),
                    idea=data.get("idea", ""),
                    viewpoint=data.get("viewpoint", ""),
                    plan=data.get("plan", ""),
                    section=data.get("section", ""),
                ))
            except (json.JSONDecodeError, KeyError, TypeError):
                # Skip malformed lines silently
                continue
    return out


# ── Decisions persistence ───────────────────────────────────────

def save_decision(
    winner: PaperSummary,
    input_summaries: List[PaperSummary],
    source: str = "unknown",
    path: str = DEFAULT_DECISIONS_PATH,
) -> str:
    """Append a DecisionRecord to the decisions JSONL file.

    Returns the absolute path to the file.
    """
    abs_path = os.path.abspath(path)
    parent = os.path.dirname(abs_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    record = DecisionRecord(
        timestamp=time.time(),
        winner_arxiv_id=winner.paper_arxiv_id,
        winner_title=winner.title,
        num_input_summaries=len(input_summaries),
        input_arxiv_ids=[s.paper_arxiv_id for s in input_summaries],
        source=source,
    )
    with open(abs_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record.to_dict(), ensure_ascii=False))
        f.write("\n")
    return abs_path


def read_decisions(
    path: str = DEFAULT_DECISIONS_PATH,
) -> List[DecisionRecord]:
    """Read all DecisionRecord objects from a JSONL file.

    Skips malformed lines.  Returns empty list if file missing.
    """
    if not os.path.exists(path):
        return []
    out: List[DecisionRecord] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                out.append(DecisionRecord(
                    timestamp=data["timestamp"],
                    winner_arxiv_id=data["winner_arxiv_id"],
                    winner_title=data["winner_title"],
                    num_input_summaries=data["num_input_summaries"],
                    input_arxiv_ids=data["input_arxiv_ids"],
                    source=data["source"],
                ))
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
    return out