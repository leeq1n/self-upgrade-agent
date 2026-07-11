"""Daily-loop integration (per v3.1.2 sub-task 3/3).

Per 你 vision (autonomous agent):
- Persist round state at end of each round (per P19)
- Auto-mark failures (per failure_recovery)
- Recover from last persisted state on startup

Per 自上而下/分治 (user meta-principle):
- Big task: v3.1.2 daily-loop persistence
- Sub-task 1 (done 33c6ead): state.json persistence
- Sub-task 2 (done 1ac92fc): failure recovery
- Sub-task 3 (this commit): integration with daily-loop

Per P19 (data flow observability):
- Persist intermediate results for cross-round observability
- Persist at end of round (atomic write)

Per P18: integration tests required.
Per LITERATURE Signal-to-Fix: fail-fast at integration layer (test separately).
"""
import sys
from pathlib import Path


def record_round(round_index, round_data, state_path=None):
    """Record round result in state.json (per P19)."""
    from src.state_persistence import update_round
    return update_round(round_index, round_data, state_path)


def record_failure(round_index, error_msg, state_path=None):
    """Record failure in state.json (per failure_recovery)."""
    from src.failure_recovery import mark_failure
    return mark_failure(round_index, error_msg, state_path)


def get_resume_state(state_path=None):
    """Get state to resume from (per failure_recovery).

    Returns dict with:
    - last_round_index: last completed round (or None)
    - failures: dict of past failures
    - can_resume: bool
    """
    from src.state_persistence import load_state
    state = load_state(state_path)
    return {
        "last_round_index": state.get("last_round_index"),
        "failures": state.get("failures", {}),
        "can_resume": state.get("last_round_index") is not None,
        "schema_version": state.get("schema_version"),
    }


def init_daily_loop(meta=None, state_path=None):
    """Initialize state.json for daily-loop (idempotent).

    Per LITERATURE Signal-to-Fix: idempotent init preserves data
    if state already exists (don't clobber).
    """
    from src.state_persistence import load_state, save_state
    state = load_state(state_path)
    if state and "rounds" in state:
        # Already initialized; preserve
        return state
    # First-time init
    from src.state_persistence import init_state
    return init_state(meta, state_path)


def daily_loop_persisted(do_round, max_rounds=None, interval=0,
                          state_path=None, target=None):
    """Run daily-loop with state.json persistence (per v3.1.2 sub-task 3/3).

    Per 你 vision: cross-process autonomous agent with persistence.

    Args:
        do_round: callable(round_index) -> RoundResult-like dict
        max_rounds: max rounds to run (None = forever)
        interval: seconds between rounds
        state_path: optional state.json path override

    Returns: dict with rounds_run, kept_count, failures_count
    """
    from src.state_persistence import load_state
    init_daily_loop(meta={"target": target} if target else None, state_path=state_path)
    # Resume from last_round_index (per failure_recovery spec)
    state = load_state(state_path)
    start_idx = (state.get("last_round_index") or 0) + 1
    rounds = 0
    kept = 0
    failures = 0
    try:
        while max_rounds is None or rounds < max_rounds:
            round_idx = start_idx + rounds
            rounds += 1
            try:
                r = do_round(round_idx)
            except Exception as e:
                record_failure(round_idx, str(e), state_path)
                failures += 1
                continue
            # Persist round result
            record_round(round_idx, r, state_path)
            if r.get("decision") == "KEPT":
                kept += 1
    except KeyboardInterrupt:
        pass
    return {
        "rounds_run": rounds,
        "kept_count": kept,
        "failures_count": failures,
    }


def main():
    """CLI: show daily-loop state."""
    from src.state_persistence import load_state

    state = load_state()
    if not state:
        print("No state.json (empty)")
        return 0
    print(f"Daily-loop state:")
    resume = get_resume_state()
    print(f"  last_round_index: {resume['last_round_index']}")
    print(f"  can_resume: {resume['can_resume']}")
    print(f"  failures: {len(resume['failures'])}")
    rounds = state.get("rounds", {})
    print(f"  rounds persisted: {len(rounds)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())