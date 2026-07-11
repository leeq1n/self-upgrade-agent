"""Daily-loop state persistence (per P19 + 你 vision of autonomous agent).

Per P19 (Data flow observability):
- Persist intermediate results for cross-round observability
- Daily-loop needs state across rounds + restarts

Per 你 vision (2026-07-10 '我希望这个项目之后可以自己独立运行'):
- Cross-process state (between daily-loop runs)
- Failure recovery: re-start from last persisted state
- Audit trail: which rounds ran, what happened

Per 自上而下/分治 (user 2026-07-11 meta-principle):
- Big task: v3.1.2 daily-loop persistence
- Sub-task 1 (this): state.json persistence (cross-round state)
- Sub-task 2 (future): failure recovery on top of state.json
- Sub-task 3 (future): integration with daily-loop

Per P18 (failure -> regression test): must have tests.

Per Signal-to-Fix (LITERATURE): persist at end of round (atomic write).
Per P9 (hard rule): atomic write (tmp + os.replace, per ISS-003 lesson).
"""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


STATE_DIR = Path(__file__).parent.parent / "upgrades"
STATE_FILE = STATE_DIR / "state.json"


def _now_iso():
    """Current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def _now_ts():
    """Current UTC timestamp (float)."""
    return time.time()


def atomic_write_json(path, data, indent=2):
    """Atomic JSON write (per ISS-003 lesson: tmp + os.replace).

    Per P9 hard rule + LITERATURE: atomic write prevents torn reads.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    os.replace(tmp, path)


def load_state(state_path=None):
    """Load state.json (returns empty dict if missing)."""
    path = Path(state_path) if state_path else STATE_FILE
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return json.loads(f.read())
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state, state_path=None):
    """Save state.json atomically."""
    path = Path(state_path) if state_path else STATE_FILE
    atomic_write_json(path, state)


def update_round(round_index, round_data, state_path=None):
    """Update state.json with new round data.

    Per P19: persist at end of round.
    Per LITERATURE Signal-to-Fix: atomic write at end.

    Returns: updated state dict.
    """
    state = load_state(state_path)
    if "rounds" not in state:
        state["rounds"] = {}
    state["rounds"][str(round_index)] = {
        **round_data,
        "persisted_at": _now_iso(),
    }
    state["last_updated"] = _now_iso()
    state["last_round_index"] = round_index
    save_state(state, state_path)
    return state


def get_last_round(state_path=None):
    """Get last round index from state.json (or None)."""
    state = load_state(state_path)
    return state.get("last_round_index")


def get_round(round_index, state_path=None):
    """Get specific round data from state.json (or None)."""
    state = load_state(state_path)
    return state.get("rounds", {}).get(str(round_index))


def get_all_rounds(state_path=None):
    """Get all rounds from state.json (sorted by index)."""
    state = load_state(state_path)
    rounds = state.get("rounds", {})
    if not rounds:
        return []
    indexed = [(int(k), v) for k, v in rounds.items()]
    indexed.sort()
    return [v for _, v in indexed]


def init_state(meta=None, state_path=None):
    """Initialize state.json with metadata.

    Per P14 docs stay current: include schema_version + created_at.
    """
    state = {
        "schema_version": "1.0",
        "created_at": _now_iso(),
        "last_updated": _now_iso(),
        "last_round_index": None,
        "rounds": {},
        "meta": meta or {},
    }
    save_state(state, state_path)
    return state


def main():
    """CLI: show state.json summary."""
    state = load_state()
    if not state:
        print("No state.json (empty)")
        return 0
    print(f"state.json summary:")
    print(f"  schema_version: {state.get('schema_version')}")
    print(f"  created_at: {state.get('created_at')}")
    print(f"  last_updated: {state.get('last_updated')}")
    print(f"  last_round_index: {state.get('last_round_index')}")
    rounds = state.get("rounds", {})
    print(f"  rounds: {len(rounds)}")
    if rounds:
        for k in sorted(rounds.keys(), key=int)[-3:]:
            r = rounds[k]
            print(f"    [{k}] decision={r.get('decision', 'N/A')} "
                  f"target={r.get('target', 'N/A')}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())