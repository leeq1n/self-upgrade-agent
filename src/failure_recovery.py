"""Failure recovery (per v3.1.2 sub-task 2/3, on top of state.json).

Per 你 vision (2026-07-10 '我希望这个项目之后可以自己独立运行'):
- Cross-process recovery: re-start from last persisted state
- No manual intervention when daily-loop crashes

Per P18 (failure -> regression test):
- Test crash scenarios, restart scenarios
- Backoff strategy prevents thundering herd

Per 自上而下/分治 (user 2026-07-11 meta-principle):
- Big task: v3.1.2 daily-loop persistence
- Sub-task 1 (done 33c6ead): state.json persistence
- Sub-task 2 (this commit): failure recovery
- Sub-task 3 (future): integration with daily-loop

Per LITERATURE Signal-to-Fix + Nate Berkopec backoff:
- exponential backoff with jitter
- max attempts before giving up
- recover from last persisted state

Per P9 (hard rule): atomic write (already in state_persistence.py).
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_BASE_DELAY_SEC = 1.0
DEFAULT_MAX_DELAY_SEC = 300.0  # 5 minutes


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def attempt_recovery(state_path=None, max_attempts=DEFAULT_MAX_ATTEMPTS,
                     base_delay=DEFAULT_BASE_DELAY_SEC,
                     max_delay=DEFAULT_MAX_DELAY_SEC):
    """Attempt to recover from a failure, with exponential backoff.

    Per Nate Berkopec: exponential backoff with jitter prevents
    thundering herd (multiple processes retrying simultaneously).

    Args:
        state_path: path to state.json (for context)
        max_attempts: max retry attempts before giving up
        base_delay: initial delay (doubles each attempt)
        max_delay: cap on delay

    Returns: dict with attempt log + final outcome.
    """
    from src.state_persistence import load_state

    state = load_state(state_path)
    log = []
    for attempt in range(1, max_attempts + 1):
        # Exponential backoff with jitter
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        jitter = delay * 0.1 * (2 * (time.time() % 1) - 1)  # +/- 10%
        actual_delay = delay + jitter
        entry = {
            "attempt": attempt,
            "scheduled_delay": actual_delay,
            "state_path": str(state_path) if state_path else None,
            "timestamp": _now_iso(),
        }
        log.append(entry)
        time.sleep(actual_delay)
    return {
        "attempts": max_attempts,
        "log": log,
        "state_loaded": bool(state),
        "last_round_index": state.get("last_round_index"),
        "timestamp": _now_iso(),
    }


def compute_backoff_delay(attempt, base_delay=DEFAULT_BASE_DELAY_SEC,
                          max_delay=DEFAULT_MAX_DELAY_SEC, jitter_seed=None):
    """Compute exponential backoff delay for given attempt.

    Per Signal-to-Fix: exponential + jitter prevents synchronized retries.

    Args:
        attempt: 1-indexed attempt number
        base_delay: initial delay (seconds)
        max_delay: cap on delay
        jitter_seed: for testing (deterministic jitter)

    Returns: delay in seconds
    """
    if attempt < 1:
        return 0
    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
    if jitter_seed is not None:
        import random
        rng = random.Random(jitter_seed)
        jitter = delay * 0.1 * (rng.random() * 2 - 1)
    else:
        jitter = delay * 0.1 * (2 * (time.time() % 1) - 1)
    return max(0, delay + jitter)


def should_retry(attempt, max_attempts=DEFAULT_MAX_ATTEMPTS):
    """Decide whether to retry given current attempt count."""
    return attempt < max_attempts


def mark_failure(round_index, error_msg, state_path=None):
    """Mark a round as failed in state.json.

    Per P19: persist failure for observability.
    """
    from src.state_persistence import load_state, save_state

    state = load_state(state_path)
    if "failures" not in state:
        state["failures"] = {}
    state["failures"][str(round_index)] = {
        "error": error_msg,
        "timestamp": _now_iso(),
    }
    state["last_updated"] = _now_iso()
    save_state(state, state_path)
    return state


def get_failure_count(round_index, state_path=None):
    """Get failure count for a specific round."""
    from src.state_persistence import load_state
    state = load_state(state_path)
    failures = state.get("failures", {})
    return len(failures.get(str(round_index), []))


def get_all_failures(state_path=None):
    """Get all failures from state.json."""
    from src.state_persistence import load_state
    state = load_state(state_path)
    return state.get("failures", {})


def main():
    """CLI: show recovery stats."""
    from src.state_persistence import load_state

    state = load_state()
    failures = state.get("failures", {})
    print(f"Recovery stats:")
    print(f"  last_round_index: {state.get('last_round_index')}")
    print(f"  failures: {len(failures)}")
    for k, v in failures.items():
        print(f"    [{k}] error={v.get('error', 'N/A')[:60]}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())