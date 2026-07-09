"""scripts/_self_check_run_replay.py - dry-run verification (no LLM).

Tests that scripts/run_replay.py works without needing a real LLM
call.  Monkey-patches replay_all_failures to return a fixed report.

Usage:
    python scripts/_self_check_run_replay.py
"""
import sys
import os
from unittest.mock import patch, MagicMock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))


def main():
    fake_report = MagicMock()
    fake_report.to_dict.return_value = {
        "total_unique": 3,
        "now_passes": 1,
        "still_fails": 2,
        "not_replayed": 0,
        "details": [
            {"paper_arxiv_id": "x", "target_module": "y",
             "decision": "NO_PATCH", "verdict": "now_passes",
             "detail": "KEPT"},
        ],
    }
    with patch("src.v2_round.replay_all_failures",
               return_value=fake_report):
        # Run the actual script's main()
        from scripts.run_replay import main as run_main
        run_main()


if __name__ == "__main__":
    main()