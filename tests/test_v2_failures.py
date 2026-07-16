"""Tests for src/failures.py — failure log + replay.

Layered tests (per P3: 单元→联合→集成):
  - Unit: log_failure / read_failures / unique_failure_modes / replay_one
  - Joint: run_one_round() actually calls log_failure on each branch
"""
import os
import sys
import json
import tempfile
import pytest
from unittest.mock import MagicMock

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)


# ─────────────────────────────────────────────────────────────
# Unit tests
# ─────────────────────────────────────────────────────────────

class TestFailureSignature:
    def test_round_1970s_signature_has_all_fields(self):
        from src.failures import FailureSignature
        sig = FailureSignature(
            paper_arxiv_id="2310.02170",
            target_module="core/planner.py",
            decision="NO_PATCH",
            error_first_line="LLM did not produce valid Patch",
            timestamp=1234567890.0,
        )
        assert sig.key() == ("2310.02170", "core/planner.py", "NO_PATCH")

    def test_to_jsonl_line_round_trip(self):
        from src.failures import FailureSignature
        sig = FailureSignature(
            paper_arxiv_id="x", target_module="y", decision="REVERTED",
            error_first_line="err", timestamp=1.0,
        )
        line = sig.to_jsonl_line()
        d = json.loads(line)
        assert d["paper_arxiv_id"] == "x"
        assert d["decision"] == "REVERTED"


class TestLogFailure:
    def test_log_failure_appends(self, tmp_path):
        """log_failure should append a JSONL line to the log."""
        from src.failures import log_failure, read_failures
        log_path = str(tmp_path / "failures.jsonl")

        # Build a minimal RoundResult-like
        result = MagicMock()
        result.paper.arxiv_id = "2310.02170"
        result.target_module = "core/planner.py"
        result.decision = "NO_PATCH"
        result.error = "improve returned None"

        sig = log_failure(result, log_path=log_path)
        assert sig is not None
        assert sig.decision == "NO_PATCH"

        # Verify the file was written
        sigs = read_failures(log_path=log_path)
        assert len(sigs) == 1
        assert sigs[0].paper_arxiv_id == "2310.02170"

    def test_log_failure_creates_parent_dir(self, tmp_path):
        """log_failure should mkdir parent if missing."""
        from src.failures import log_failure
        log_path = str(tmp_path / "deep" / "nested" / "failures.jsonl")

        result = MagicMock()
        result.paper.arxiv_id = "x"
        result.target_module = "y"
        result.decision = "REVERTED"
        result.error = "err"

        sig = log_failure(result, log_path=log_path)
        assert sig is not None
        assert os.path.exists(log_path)

    def test_log_failure_never_raises(self, tmp_path):
        """Per principle: log_failure must NEVER raise — even on
        permission errors etc, return None."""
        from src.failures import log_failure
        # Path on Windows that we can't write to (a directory)
        bad_path = str(tmp_path)  # is a dir, not a file
        result = MagicMock()
        result.paper.arxiv_id = "x"
        result.target_module = "y"
        result.decision = "REVERTED"
        result.error = "err"

        sig = log_failure(result, log_path=bad_path)
        # Returns None instead of raising
        assert sig is None


class TestReadFailures:
    def test_read_missing_returns_empty(self, tmp_path):
        from src.failures import read_failures
        result = read_failures(log_path=str(tmp_path / "nonexistent.jsonl"))
        assert result == []

    def test_read_skips_malformed_lines(self, tmp_path):
        from src.failures import read_failures
        log = tmp_path / "failures.jsonl"
        with open(log, "w") as f:
            f.write('{"paper_arxiv_id":"x","target_module":"y","decision":"NO_PATCH","error_first_line":"","timestamp":1.0}\n')
            f.write('this is not json\n')
            f.write('{"incomplete":true}\n')
            f.write('{"paper_arxiv_id":"a","target_module":"b","decision":"REVERTED","error_first_line":"","timestamp":2.0}\n')

        sigs = read_failures(log_path=str(log))
        assert len(sigs) == 2
        assert sigs[0].paper_arxiv_id == "x"
        assert sigs[1].paper_arxiv_id == "a"


class TestUniqueFailureModes:
    def test_dedup_by_key(self, tmp_path):
        from src.failures import log_failure, unique_failure_modes
        log = str(tmp_path / "failures.jsonl")
        result = MagicMock()
        result.paper.arxiv_id = "x"
        result.target_module = "y"
        result.decision = "NO_PATCH"
        result.error = "first attempt"
        log_failure(result, log_path=log)
        result.error = "second attempt"  # different error message
        log_failure(result, log_path=log)
        result.error = "third attempt"
        log_failure(result, log_path=log)

        modes = unique_failure_modes(log_path=log)
        assert len(modes) == 1  # all collapse to same key


class TestReplayOne:
    def test_now_passes(self):
        from src.failures import FailureSignature, replay_one
        sig = FailureSignature(
            paper_arxiv_id="x", target_module="y", decision="NO_PATCH",
            error_first_line="err", timestamp=1.0,
        )
        # play_fn returns a RoundResult with KEPT decision
        ok_result = MagicMock()
        ok_result.decision = "KEPT"
        verdict, detail = replay_one(sig, lambda _: ok_result)
        assert verdict == "now_passes"
        assert detail == "KEPT"

    def test_still_fails(self):
        from src.failures import FailureSignature, replay_one
        sig = FailureSignature(
            paper_arxiv_id="x", target_module="y", decision="REVERTED",
            error_first_line="err", timestamp=1.0,
        )
        fail_result = MagicMock()
        fail_result.decision = "REVERTED"
        verdict, detail = replay_one(sig, lambda _: fail_result)
        assert verdict == "still_fails"

    def test_play_fn_raises(self):
        from src.failures import FailureSignature, replay_one
        sig = FailureSignature(
            paper_arxiv_id="x", target_module="y", decision="NO_PATCH",
            error_first_line="err", timestamp=1.0,
        )
        verdict, detail = replay_one(sig, lambda _: 1/0)
        assert verdict == "not_replayed"
        assert "raised" in detail

    def test_play_fn_returns_none(self):
        from src.failures import FailureSignature, replay_one
        sig = FailureSignature(
            paper_arxiv_id="x", target_module="y", decision="NO_PATCH",
            error_first_line="err", timestamp=1.0,
        )
        verdict, detail = replay_one(sig, lambda _: None)
        assert verdict == "not_replayed"


# ─────────────────────────────────────────────────────────────
# Joint tests: run_one_round wires log_failure
# ─────────────────────────────────────────────────────────────

class TestRunOneRoundLogsFailures:
    """Joint test: run_one_round should call log_failure on each
    failure path (NO_PATCH, APPLY_FAILED, REVERTED) but NOT on KEPT."""

    def test_no_patch_path_logs(self, tmp_path, monkeypatch):
        """NO_PATCH path calls log_failure with the right decision."""
        from src.v2_round import run_one_round
        from src.v2_agent import Paper
        from src.failures import log_failure as real_log, DEFAULT_LOG
        from src import failures

        log_calls = []
        def fake_log(result, log_path=DEFAULT_LOG):
            log_calls.append(getattr(result, "decision", None))
            return None

        # Mock _chat to return garbage so improve() returns None.
        # Note: log_failure is imported in src.v2_round as a NAME,
        # so monkeypatching src.failures.log_failure doesn't reach
        # it.  Use sys.modules trick: patch the bound reference.
        import src.v2_round as v2r
        monkeypatch.setattr(v2r, "log_failure", fake_log)
        import src.v2_agent as v2a
        monkeypatch.setattr(v2a, "_chat", lambda **kwargs: MagicMock(
            content="garbage no json", error=None,
        ))

        result = run_one_round(
            paper=Paper(arxiv_id="x", title="x", abstract="x"),
            target_module=str(tmp_path / "planner.py"),
            project_root=str(tmp_path),
        )
        assert result.decision == "NO_PATCH"
        assert "NO_PATCH" in log_calls

    def test_kept_path_does_not_log(self, tmp_path, monkeypatch):
        """KEPT path should NOT log_failure (successes don't become
        regression tests)."""
        from src.v2_round import run_one_round
        from src.v2_agent import Paper
        from src import failures

        log_calls = []
        def fake_log(result, log_path=None):
            log_calls.append(getattr(result, "decision", None))
            return None

        # log_failure in src.v2_round is a bound name, not the module attr.
        # Patch the bound reference directly.
        import src.v2_round as v2r
        monkeypatch.setattr(v2r, "log_failure", fake_log)

        # Use a hand-rolled compatible patch — apply succeeds, tests pass
        target = tmp_path / "planner.py"
        target.write_text("def plan_task(task):\n    return [task]\n")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_basic.py").write_text(
            "def test_existing():\n"
            "    from planner import plan_task\n"
            "    assert plan_task('hi') == ['hi']\n"
        )

        import src.v2_agent as v2a
        # Patch that preserves behavior
        new_fn = (
            "def plan_task(task):\n"
            "    # v2.3 test patch — same behavior\n"
            "    return [task]\n"
        )
        target_escaped = str(target).replace("\\", "\\\\")
        patch_payload = (
            '{"function": "' + new_fn.replace('"', '\\"').replace("\n", "\\n") + '", '
            '"test": "def test_x(): pass", '
            '"module": "' + target_escaped + '"}'
        )
        monkeypatch.setattr(v2a, "_chat", lambda **kwargs: MagicMock(
            content=patch_payload, error=None,
        ))

        result = run_one_round(
            paper=Paper(arxiv_id="x", title="x", abstract="x"),
            target_module=str(target),
            project_root=str(tmp_path),
            test_path="tests/test_basic.py",
        )
        # KEPT expected
        assert result.decision == "KEPT"
        # log_failure should NOT have been called (no failures)
        assert "NO_PATCH" not in log_calls
        assert "APPLY_FAILED" not in log_calls
        assert "REVERTED" not in log_calls


# ─────────────────────────────────────────────────────────────
# Replay loop tests (v2.3.1)
# ─────────────────────────────────────────────────────────────

class TestReplayAll:
    """replay_all() should iterate unique failure modes and
    aggregate verdicts."""

    def test_replay_all_empty_log(self, tmp_path):
        from src.failures import replay_all
        log = str(tmp_path / "f.jsonl")
        report = replay_all(play_fn=lambda sig: None, log_path=log)
        assert report.total_unique == 0
        assert report.now_passes == 0
        assert report.still_fails == 0
        assert report.not_replayed == 0

    def test_replay_all_three_modes(self, tmp_path):
        """3 unique failure modes → replay reports 3 entries."""
        from src.failures import log_failure, replay_all
        log = str(tmp_path / "f.jsonl")
        for arxiv, target, dec in [
            ("2310.02170", "core/planner.py", "NO_PATCH"),
            ("2210.03629", "core/llm.py", "REVERTED"),
            ("2310.02170", "core/agent.py", "APPLY_FAILED"),
        ]:
            result = type("R", (), {
                "paper": type("P", (), {"arxiv_id": arxiv}),
                "target_module": target, "decision": dec, "error": "e",
            })()
            log_failure(result, log_path=log)

        # play_fn returns a 'now_passes' result for every signature
        ok = type("R", (), {"decision": "KEPT"})()
        report = replay_all(play_fn=lambda _: ok, log_path=log)
        assert report.total_unique == 3
        assert report.now_passes == 3
        assert report.still_fails == 0

    def test_replay_all_dedup(self, tmp_path):
        """Same failure mode logged 3 times → 1 unique → 1 replay entry."""
        from src.failures import log_failure, replay_all
        log = str(tmp_path / "f.jsonl")
        for _ in range(3):
            result = type("R", (), {
                "paper": type("P", (), {"arxiv_id": "x"}),
                "target_module": "y", "decision": "REVERTED", "error": "e",
            })()
            log_failure(result, log_path=log)
        ok = type("R", (), {"decision": "KEPT"})()
        report = replay_all(play_fn=lambda _: ok, log_path=log)
        assert report.total_unique == 1

    def test_replay_all_mixed_verdicts(self, tmp_path):
        """play_fn returns KEPT for one, REVERTED for another, raises for third."""
        from src.failures import log_failure, replay_all
        log = str(tmp_path / "f.jsonl")
        for arxiv, dec in [("a", "NO_PATCH"), ("b", "REVERTED"), ("c", "APPLY_FAILED")]:
            result = type("R", (), {
                "paper": type("P", (), {"arxiv_id": arxiv}),
                "target_module": "t", "decision": dec, "error": "e",
            })()
            log_failure(result, log_path=log)

        def play_fn(sig):
            if sig.paper_arxiv_id == "a":
                return type("R", (), {"decision": "KEPT"})()  # now_passes
            if sig.paper_arxiv_id == "b":
                return type("R", (), {"decision": "REVERTED"})()  # still_fails
            if sig.paper_arxiv_id == "c":
                raise RuntimeError("LLM unreachable")  # not_replayed

        report = replay_all(play_fn=play_fn, log_path=log)
        assert report.total_unique == 3
        assert report.now_passes == 1
        assert report.still_fails == 1
        assert report.not_replayed == 1

    def test_replay_report_to_dict(self, tmp_path):
        from src.failures import replay_all
        report = replay_all(play_fn=lambda sig: None, log_path=str(tmp_path / "f.jsonl"))
        d = report.to_dict()
        assert d["total_unique"] == 0
        assert "details" in d
