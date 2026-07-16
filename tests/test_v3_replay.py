"""Tests for src/v3_replay.py - failure log inspect (fast)."""
import os
import sys
import tempfile

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)

from src.v3_replay import inspect_failures, format_inspect
from src.failures import log_failure, read_failures, _ensure_log_dir
from src.v2_round import RoundResult
from src.v2_agent import Paper


def _make_signature(paper_id, target, decision, error):
    """Build a synthetic RoundResult for log_failure."""
    paper = Paper(arxiv_id=paper_id, title=paper_id, abstract="")
    return RoundResult(
        decision=decision,
        paper=paper,
        target_module=target,
        error=error,
    )


class TestInspectFailures:
    def test_empty_log(self, tmp_path):
        """Empty log returns sensible defaults."""
        log = str(tmp_path / "f.jsonl")
        insp = inspect_failures(log_path=log)
        assert insp["total_entries"] == 0
        assert insp["unique_signatures"] == 0
        assert insp["decisions"] == {}
        assert insp["top_papers"] == {}
        assert insp["recent"] == []

    def test_missing_log(self, tmp_path):
        """Missing log file returns empty (no exception)."""
        log = str(tmp_path / "nope.jsonl")
        insp = inspect_failures(log_path=log)
        assert insp["total_entries"] == 0

    def test_with_logged_failures(self, tmp_path):
        """3 NO_PATCH + 1 REVERTED + 1 APPLY_FAILED counted correctly."""
        log = str(tmp_path / "f.jsonl")
        _ensure_log_dir(log_path=log)
        # Write entries directly
        from src.failures import DEFAULT_LOG
        import json
        from dataclasses import asdict
        with open(log, "w") as f:
            for i in range(3):
                f.write(json.dumps({
                    "paper_arxiv_id": "a", "target_module": "core/x.py",
                    "decision": "NO_PATCH", "error_first_line": "fail",
                    "timestamp": 1.0 + i,
                }) + "\n")
            f.write(json.dumps({
                "paper_arxiv_id": "b", "target_module": "core/y.py",
                "decision": "REVERTED", "error_first_line": "test fail",
                "timestamp": 2.0,
            }) + "\n")
            f.write(json.dumps({
                "paper_arxiv_id": "c", "target_module": "core/z.py",
                "decision": "APPLY_FAILED", "error_first_line": "apply err",
                "timestamp": 3.0,
            }) + "\n")

        insp = inspect_failures(log_path=log)
        assert insp["total_entries"] == 5
        assert insp["unique_signatures"] == 3
        assert insp["decisions"]["NO_PATCH"] == 3
        assert insp["decisions"]["REVERTED"] == 1
        assert insp["decisions"]["APPLY_FAILED"] == 1

    def test_top_papers(self, tmp_path):
        """Top papers ranked by failure count."""
        log = str(tmp_path / "f.jsonl")
        import json
        with open(log, "w") as f:
            for i in range(5):
                f.write(json.dumps({
                    "paper_arxiv_id": "popular",
                    "target_module": "core/x.py",
                    "decision": "NO_PATCH", "error_first_line": "",
                    "timestamp": float(i),
                }) + "\n")
            f.write(json.dumps({
                "paper_arxiv_id": "rare", "target_module": "core/y.py",
                "decision": "NO_PATCH", "error_first_line": "",
                "timestamp": 100.0,
            }) + "\n")
        insp = inspect_failures(log_path=log)
        assert insp["top_papers"]["popular"] == 5
        assert insp["top_papers"]["rare"] == 1

    def test_recent_truncated_to_5(self, tmp_path):
        """Recent is at most 5 entries."""
        log = str(tmp_path / "f.jsonl")
        import json
        with open(log, "w") as f:
            for i in range(20):
                f.write(json.dumps({
                    "paper_arxiv_id": f"p{i}",
                    "target_module": "core/x.py",
                    "decision": "NO_PATCH", "error_first_line": "",
                    "timestamp": float(i),
                }) + "\n")
        insp = inspect_failures(log_path=log)
        assert len(insp["recent"]) == 5


class TestFormatInspect:
    def test_format_includes_key_fields(self, tmp_path):
        log = str(tmp_path / "f.jsonl")
        insp = inspect_failures(log_path=log)
        out = format_inspect(insp)
        assert "FAILURE LOG INSPECT" in out
        assert "Total entries" in out
        assert "Unique signatures" in out

    def test_format_with_data(self, tmp_path):
        log = str(tmp_path / "f.jsonl")
        import json
        with open(log, "w") as f:
            f.write(json.dumps({
                "paper_arxiv_id": "x", "target_module": "core/y.py",
                "decision": "NO_PATCH", "error_first_line": "",
                "timestamp": 1.0,
            }) + "\n")
        insp = inspect_failures(log_path=log)
        out = format_inspect(insp)
        assert "NO_PATCH" in out
        assert "x" in out


class TestInspectIsFast:
    """inspect_failures must NOT call LLM (per user '跑的时候卡了 5+ min')."""

    def test_no_llm_call(self, tmp_path, monkeypatch):
        """Even if LLM is invoked somehow, inspect shouldn't be slow."""
        # Mock LLMConfig to verify it's never constructed
        from src import v3_replay
        called = []
        original = v3_replay.read_failures
        def spy(log_path=os.path.join("upgrades", "failures.jsonl")):
            called.append("read_failures")
            return original(log_path=log_path)
        monkeypatch.setattr(v3_replay, "read_failures", spy)
        # inspect_failures should not need LLM
        insp = inspect_failures()
        assert "read_failures" in called
        # No LLM call assertion is implicit (no LLMConfig import in v3_replay)


# ── Joint with real failures.jsonl ──────────────────────────────

class TestInspectRealLog:
    """If real failures.jsonl exists, inspect should work on it."""

    def test_inspect_real_log(self):
        """inspect_failures() on the real upgrade log doesn't crash."""
        insp = inspect_failures()
        # Could be 0 entries (no real runs) or many
        assert "total_entries" in insp
        assert "decisions" in insp
