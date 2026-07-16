"""Failure escalation (per v4.0.0 sub-task 3/3).

Per 你 vision 2026-07-08 '我希望这个项目之后可以自己独立运行':
- True autonomous, but with visibility
- Per LITERATURE Signal-to-Fix: failures must surface, not silently fail

Per 自上而下/分治 (user meta-principle):
- Big: SA v4.0.0 cron execution
- Sub-task 1 (b350609): cron logic + CLI
- Sub-task 2 (c7998fa): OS cron integration
- Sub-task 3 (THIS COMMIT): failure escalation (LAST sub-task)
  — **v4.0.0 MVP COMPLETE (3/3 sub-tasks)**

Per LITERATURE Nate Berkopec: exponential backoff prevents cascading failures.
Per P9 (hard rule): alert/log on persistent failures.
Per P23 doc-first: spec in PROJECT_STATE.
Per P18: regression tests required.
"""
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List


def compute_backoff_seconds(failure_count, base=60, max_delay=3600):
    """Exponential backoff with cap (per Nate Berkopec).

    Per LITERATURE: backoff(n) = min(base * 2^(n-1), max_delay).
    Returns: int seconds.
    """
    if failure_count <= 0:
        return 0
    delay = base * (2 ** (failure_count - 1))
    return min(delay, max_delay)


class FailureTracker:
    """Track consecutive failures + trigger escalation (per v4.0.0).

    Per LITERATURE Signal-to-Fix: failures surface, not silent.
    Per Nate Berkopec: exponential backoff prevents cascade.
    """

    def __init__(self, state_path=None, max_consecutive=3,
                 base_backoff=60, max_backoff=3600,
                 alert_log_path=None):
        """Initialize tracker.

        Args:
            state_path: optional JSON file for persistence
            max_consecutive: alert after N consecutive failures
            base_backoff: base backoff in seconds
            max_backoff: max backoff cap in seconds
            alert_log_path: optional file to log alerts
        """
        self.state_path = Path(state_path) if state_path else None
        self.max_consecutive = max_consecutive
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff
        self.alert_log_path = Path(alert_log_path) if alert_log_path else None
        self.consecutive_failures = 0
        self.total_failures = 0
        self.last_failure_at = None
        self.last_alert_at = None
        self.history: List[Dict] = []
        self._load_state()

    def _load_state(self):
        """Load state from file (per P19 observability)."""
        if self.state_path and self.state_path.exists():
            import json
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                self.consecutive_failures = data.get("consecutive_failures", 0)
                self.total_failures = data.get("total_failures", 0)
                self.last_failure_at = data.get("last_failure_at")
                self.history = data.get("history", [])
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_state(self):
        """Save state to file (per P19 + atomic write per P9)."""
        if not self.state_path:
            return
        import json
        import os
        data = {
            "consecutive_failures": self.consecutive_failures,
            "total_failures": self.total_failures,
            "last_failure_at": self.last_failure_at,
            "history": self.history[-100:],  # keep last 100
        }
        tmp_path = self.state_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp_path, self.state_path)

    def record_failure(self, error_msg):
        """Record a failure event.

        Returns: dict with action (continue/backoff/alert).
        """
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_failure_at = datetime.now().isoformat()
        event = {
            "type": "failure",
            "consecutive": self.consecutive_failures,
            "error": error_msg,
            "timestamp": self.last_failure_at,
        }
        self.history.append(event)
        self._save_state()
        backoff = compute_backoff_seconds(
            self.consecutive_failures,
            self.base_backoff, self.max_backoff)
        action = "continue"
        if self.consecutive_failures >= self.max_consecutive:
            action = "alert"
            self._alert(error_msg, backoff)
        elif self.consecutive_failures > 1:
            action = "backoff"
        return {
            "consecutive_failures": self.consecutive_failures,
            "backoff_seconds": backoff,
            "action": action,
        }

    def record_success(self):
        """Record a success event (resets consecutive counter)."""
        if self.consecutive_failures > 0:
            event = {
                "type": "recovery",
                "previous_consecutive": self.consecutive_failures,
                "timestamp": datetime.now().isoformat(),
            }
            self.history.append(event)
        self.consecutive_failures = 0
        self._save_state()

    def _alert(self, error_msg, backoff):
        """Trigger alert (per LITERATURE Signal-to-Fix: visibility)."""
        alert = {
            "type": "alert",
            "consecutive_failures": self.consecutive_failures,
            "error": error_msg,
            "backoff_seconds": backoff,
            "timestamp": datetime.now().isoformat(),
        }
        self.history.append(alert)
        self.last_alert_at = alert["timestamp"]
        # Log to file if configured
        if self.alert_log_path:
            import json
            with open(self.alert_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(alert) + "\n")
        # Also print (per P9 visibility)
        print(f"[ALERT] {self.consecutive_failures} consecutive failures")
        print(f"  Error: {error_msg}")
        print(f"  Backoff: {backoff}s")

    def get_status(self):
        """Get current failure tracker status."""
        return {
            "consecutive_failures": self.consecutive_failures,
            "total_failures": self.total_failures,
            "last_failure_at": self.last_failure_at,
            "last_alert_at": self.last_alert_at,
            "history_count": len(self.history),
        }


def main():
    """CLI: show failure tracker demo."""
    print("=== SA v4.0.0 Failure Escalation ===")
    print(f"Per 你 vision 2026-07-08 '希望这个项目之后可以自己独立运行'")
    print()
    print("Per LITERATURE Signal-to-Fix: failures must surface.")
    print("Per Nate Berkopec: exponential backoff prevents cascading failures.")
    print()
    tracker = FailureTracker(max_consecutive=3)
    print("Demo: simulate 4 failures then 1 success")
    for i in range(1, 5):
        result = tracker.record_failure(f"error {i}")
        print(f"  Failure {i}: action={result['action']} "
              f"backoff={result['backoff_seconds']}s")
    tracker.record_success()
    print(f"  Success: consecutive={tracker.consecutive_failures}")
    print()
    print(f"Final status: {tracker.get_status()}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())