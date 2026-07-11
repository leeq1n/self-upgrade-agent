"""Cron-based daily-loop scheduler (per SA v4.0.0).

Per 你 vision 2026-07-08 '我希望这个项目之后可以自己独立运行':
- True autonomous deployment
- Cron-style scheduling
- Per LITERATURE Signal-to-Fix: autonomous with safety nets

Per 自上而下/分治 (user 2026-07-11 meta-principle):
- Big: SA v4.0.0 cron execution
- Sub-task 1 (this commit): cron logic + CLI
- Sub-task 2 (future): real cron integration (Windows Task Scheduler / launchd / crontab)
- Sub-task 3 (future): failure escalation

Per P23 doc-first: spec exists (PROJECT_STATE + LITERATURE).
Per P18: regression tests required.
"""
import time
import datetime
from typing import Optional, Callable, Dict, List


def parse_cron(expr):
    """Parse simple cron expression: 'H H * * *' (hour minute).

    Per LITERATURE: minimal cron parser, supports 'hour:minute daily'.
    Returns dict {hour, minute} or None if invalid.
    """
    if not expr or not isinstance(expr, str):
        return None
    parts = expr.strip().split()
    if len(parts) < 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None
        return {"hour": hour, "minute": minute}
    except ValueError:
        return None


def seconds_until_next(hour, minute, now=None):
    """Calculate seconds until next occurrence of hour:minute.

    Per LITERATURE: deterministic time math.
    Returns: int (seconds), 0 if now matches.
    """
    if now is None:
        now = datetime.datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        # Next day
        target += datetime.timedelta(days=1)
    return int((target - now).total_seconds())


def should_run_now(expr, now=None):
    """Check if cron expression matches current time (within 60s window).

    Per LITERATURE: time-based trigger check.
    Returns: bool.
    """
    parsed = parse_cron(expr)
    if parsed is None:
        return False
    if now is None:
        now = datetime.datetime.now()
    return (now.hour == parsed["hour"]
            and now.minute == parsed["minute"])


def schedule_loop(do_round, cron_expr="2 0", max_iterations=None,
                  state_path=None, log_fn=None):
    """Run daily-loop on cron schedule (per v4.0.0 MVP).

    Per 你 vision 终极目标: 真 autonomous deployment.
    Per LITERATURE: minimal, 奥卡姆.

    Args:
        do_round: callable(round_index) -> dict
        cron_expr: 'H M' format (default '2 0' = 00:02 daily)
        max_iterations: stop after N runs (None = forever)
        state_path: optional state.json path for persistence
        log_fn: optional logging callback (default print)

    Returns: dict {runs_completed, last_run_at}
    """
    from src.daily_loop_integration import (
        init_daily_loop, daily_loop_persisted,
    )
    from src.state_persistence import load_state
    if log_fn is None:
        log_fn = print
    parsed = parse_cron(cron_expr)
    if parsed is None:
        raise ValueError(f"Invalid cron expression: {cron_expr}")
    log_fn(f"[cron] Schedule: {cron_expr} (hour={parsed['hour']} "
           f"minute={parsed['minute']})")
    init_daily_loop(state_path=state_path)
    runs_completed = 0
    last_run_at = None
    iterations = 0
    try:
        while max_iterations is None or iterations < max_iterations:
            iterations += 1
            wait = seconds_until_next(parsed["hour"], parsed["minute"])
            log_fn(f"[cron] Next run in {wait}s "
                   f"(at {parsed['hour']:02d}:{parsed['minute']:02d})")
            if wait > 0:
                time.sleep(wait)
            # Time to run
            log_fn(f"[cron] Running iteration {iterations}...")
            result = daily_loop_persisted(do_round, max_rounds=1,
                                           interval=0, state_path=state_path)
            runs_completed += 1
            last_run_at = datetime.datetime.now().isoformat()
            log_fn(f"[cron] Run done: kept={result.get('kept_count', 0)} "
                   f"failed={result.get('failures_count', 0)}")
    except KeyboardInterrupt:
        log_fn("[cron] Stopped by user (Ctrl-C)")
    return {
        "runs_completed": runs_completed,
        "last_run_at": last_run_at,
    }


def main():
    """CLI: show cron schedule + manual test run."""
    print("=== SA v4.0.0 Cron Scheduler ===")
    print("Per 你 vision 2026-07-08 '希望这个项目之后可以自己独立运行'")
    print()
    # Demo: parse '2 0' (00:02 daily)
    parsed = parse_cron("2 0")
    print(f"Default cron '2 0': hour={parsed['hour']} minute={parsed['minute']}")
    secs = seconds_until_next(parsed["hour"], parsed["minute"])
    print(f"Seconds until next 00:02: {secs}s")
    print()
    print("Per LITERATURE Seed: minimal, 奥卡姆.")
    print("Sub-task 1 done: cron logic + CLI")
    print("Sub-task 2 pending: real OS cron integration")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())