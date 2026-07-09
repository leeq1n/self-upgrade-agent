"""scripts/run_replay.py - one-shot replay of the failure log.

Usage:
    python scripts/run_replay.py

Prints a JSON report of:
  - total_unique (count of unique failure modes)
  - now_passes (replay returned KEPT)
  - still_fails (replay returned anything else)
  - not_replayed (play_fn raised)
  - details (per-signature verdicts)

This is a one-shot script.  Run it, read the report, delete it
(if you want).  Or keep it as part of the project.
"""
import json
import sys
import os

# Make the project root importable
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from src.v2_round import replay_all_failures


def main():
    report = replay_all_failures(test_path="tests/test_pipeline.py")
    print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()