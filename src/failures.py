"""src/failures.py - failure log + regression test replay.

Per Substack 'The Agent Improvement Loop' (2026): production
failures must become permanent regression tests.  Every NO_PATCH /
APPLY_FAILED / REVERTED outcome is recorded as a 'failure signature'
in upgrades/failures.jsonl, and we re-run that signature at every
opportunity so the same failure never returns unnoticed.

Design choices (per user feedback 2026-07-08):
  - Append-only JSONL (one line per failure) — survives crashes
  - Failure signature = (paper_arxiv_id, target_module, decision,
    error_first_line) — enough to identify but not over-specific
  - Replay returns: ('not_replayed', reason) | ('now_passes', x)
    | ('still_fails', x) — caller decides what to do
  - Storage in upgrades/ folder (existing convention for
    runtime artifacts; see PROJECT_STATE_DETAIL §File map)
"""
import json
import os
import time
from dataclasses import dataclass, asdict
from typing import Optional, Tuple, List, Dict


DEFAULT_LOG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "upgrades", "failures.jsonl",
)


@dataclass
class FailureSignature:
    """Compact signature of a round outcome for failure tracking."""
    paper_arxiv_id: str
    target_module: str
    decision: str       # "NO_PATCH" | "APPLY_FAILED" | "REVERTED"
    error_first_line: str
    timestamp: float

    def to_jsonl_line(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: Dict) -> "FailureSignature":
        return cls(**d)

    @classmethod
    def from_round_result(cls, round_result) -> "FailureSignature":
        """Build signature from a RoundResult-like object."""
        # Defensive: RoundResult may not have all fields
        paper = getattr(round_result, "paper", None)
        arxiv = getattr(paper, "arxiv_id", "?") if paper else "?"
        err = (round_result.error or "")[:120]
        return cls(
            paper_arxiv_id=arxiv,
            target_module=getattr(round_result, "target_module", "?"),
            decision=getattr(round_result, "decision", "UNKNOWN"),
            error_first_line=err,
            timestamp=time.time(),
        )

    def key(self) -> Tuple[str, str, str]:
        """Identity used for dedup.  Excludes timestamp + error_first_line
        (the same failure mode can recur with slightly different messages)."""
        return (self.paper_arxiv_id, self.target_module, self.decision)


def _ensure_log_dir(log_path: str = DEFAULT_LOG) -> None:
    """Create the parent dir if missing.  No-op if exists."""
    parent = os.path.dirname(log_path)
    if parent and not os.path.exists(parent):
        try:
            os.makedirs(parent, exist_ok=True)
        except OSError:
            # Cannot create dir — fail later when writing
            pass


def log_failure(round_result, log_path: str = DEFAULT_LOG) -> Optional[FailureSignature]:
    """Append a FailureSignature to the JSONL log.

    Returns the signature on success, None on any error.  This
    function must NEVER raise — it is called from the decision path
    where a logging error shouldn't fail the round.
    """
    try:
        sig = FailureSignature.from_round_result(round_result)
        _ensure_log_dir(log_path)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(sig.to_jsonl_line() + "\n")
        return sig
    except Exception:
        return None


def read_failures(log_path: str = DEFAULT_LOG) -> List[FailureSignature]:
    """Read all signatures from the JSONL log.  Returns [] on missing
    or unreadable file.  Skips malformed lines (corruption tolerance)."""
    if not os.path.exists(log_path):
        return []
    out: List[FailureSignature] = []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    out.append(FailureSignature.from_dict(data))
                except (json.JSONDecodeError, TypeError, KeyError):
                    continue
    except OSError:
        return []
    return out


def unique_failure_modes(log_path: str = DEFAULT_LOG) -> List[Tuple[str, ...]]:
    """Return the unique failure-mode tuples (arxiv, target, decision),
    one per recurring failure.  Used to drive replay."""
    seen = set()
    out = []
    for sig in read_failures(log_path):
        k = sig.key()
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def replay_one(
    signature: FailureSignature,
    play_fn,
) -> Tuple[str, str]:
    """Replay a failure signature against a playback function.

    `play_fn` is a callable that takes the signature and returns
    a RoundResult-like object (with .decision).  This function
    just classifies the outcome:

      ('now_passes', decision)  - the round returned KEPT
      ('still_fails', decision) - the round returned anything else
      ('not_replayed', reason)  - play_fn raised or returned None

    Returns a (verdict, detail) tuple.
    """
    try:
        result = play_fn(signature)
    except Exception as e:
        return ("not_replayed", f"play_fn raised: {e!r}")
    if result is None:
        return ("not_replayed", "play_fn returned None")
    decision = getattr(result, "decision", "UNKNOWN")
    if decision == "KEPT":
        return ("now_passes", decision)
    return ("still_fails", decision)