"""Tests for src/v3_persist.py - summary/decision persistence.

Per user insight 2026-07-09: persist intermediate outputs of
sequential functions to disk for observability.
"""
import json
import os
import tempfile

import pytest

from src.v3_persist import (
    save_summaries,
    read_summaries,
    save_decision,
    read_decisions,
    DecisionRecord,
    DEFAULT_SUMMARIES_PATH,
    DEFAULT_DECISIONS_PATH,
)
from src.v3_multipaper import PaperSummary


def _make(id_, plan="plan", idea="idea", viewpoint="vp",
          title=None) -> PaperSummary:
    return PaperSummary(
        paper_arxiv_id=id_,
        title=title or f"Title {id_}",
        idea=idea,
        viewpoint=viewpoint,
        plan=plan,
    )


# ── save_summaries + read_summaries ──────────────────────────────

class TestSummariesRoundtrip:
    def test_roundtrip_single(self, tmp_path):
        path = str(tmp_path / "summaries.jsonl")
        s = _make("a")
        save_summaries([s], path=path)
        loaded = read_summaries(path=path)
        assert len(loaded) == 1
        assert loaded[0].paper_arxiv_id == "a"
        assert loaded[0].plan == "plan"

    def test_roundtrip_multiple(self, tmp_path):
        path = str(tmp_path / "summaries.jsonl")
        summaries = [_make("a"), _make("b"), _make("c")]
        save_summaries(summaries, path=path)
        loaded = read_summaries(path=path)
        assert len(loaded) == 3
        assert [s.paper_arxiv_id for s in loaded] == ["a", "b", "c"]

    def test_roundtrip_preserves_all_fields(self, tmp_path):
        path = str(tmp_path / "summaries.jsonl")
        s = PaperSummary(
            paper_arxiv_id="x",
            title="The Title",
            idea="A specific idea.",
            viewpoint="A viewpoint about why we use it",
            plan="A plan of action",
            section="The Section",
        )
        save_summaries([s], path=path)
        loaded = read_summaries(path=path)
        assert loaded[0] == s

    def test_overwrite_existing(self, tmp_path):
        path = str(tmp_path / "summaries.jsonl")
        save_summaries([_make("a"), _make("b")], path=path)
        # Save a different list — should overwrite, not append
        save_summaries([_make("c")], path=path)
        loaded = read_summaries(path=path)
        assert [s.paper_arxiv_id for s in loaded] == ["c"]

    def test_empty_list(self, tmp_path):
        path = str(tmp_path / "summaries.jsonl")
        save_summaries([], path=path)
        # File should exist but be empty
        assert os.path.exists(path)
        loaded = read_summaries(path=path)
        assert loaded == []

    def test_missing_file_returns_empty(self, tmp_path):
        path = str(tmp_path / "nonexistent.jsonl")
        loaded = read_summaries(path=path)
        assert loaded == []

    def test_corrupt_line_skipped(self, tmp_path):
        path = str(tmp_path / "summaries.jsonl")
        # Write valid line + garbage line + valid line
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(_make("a").to_dict()) + "\n")
            f.write("not valid json\n")
            f.write(json.dumps(_make("b").to_dict()) + "\n")
        loaded = read_summaries(path=path)
        # Valid lines survive, garbage skipped
        assert [s.paper_arxiv_id for s in loaded] == ["a", "b"]


# ── save_decision + read_decisions ──────────────────────────────

class TestDecisionsRoundtrip:
    def test_single_decision(self, tmp_path):
        path = str(tmp_path / "decisions.jsonl")
        winner = _make("b")
        inputs = [_make("a"), _make("b"), _make("c")]
        save_decision(winner, inputs, source="llm", path=path)
        loaded = read_decisions(path=path)
        assert len(loaded) == 1
        assert loaded[0].winner_arxiv_id == "b"
        assert loaded[0].num_input_summaries == 3
        assert loaded[0].source == "llm"
        assert loaded[0].input_arxiv_ids == ["a", "b", "c"]

    def test_appends_multiple_decisions(self, tmp_path):
        path = str(tmp_path / "decisions.jsonl")
        # First decision
        save_decision(_make("a"), [_make("a"), _make("b")],
                      source="mock", path=path)
        # Second decision
        save_decision(_make("b"), [_make("a"), _make("b")],
                      source="llm", path=path)
        loaded = read_decisions(path=path)
        assert len(loaded) == 2
        assert loaded[0].source == "mock"
        assert loaded[1].source == "llm"

    def test_default_source(self, tmp_path):
        path = str(tmp_path / "decisions.jsonl")
        save_decision(_make("a"), [_make("a")], path=path)
        loaded = read_decisions(path=path)
        assert loaded[0].source == "unknown"

    def test_decision_record_to_dict(self):
        rec = DecisionRecord(
            timestamp=1.0,
            winner_arxiv_id="x",
            winner_title="X",
            num_input_summaries=2,
            input_arxiv_ids=["a", "b"],
            source="mock",
        )
        d = rec.to_dict()
        assert d["timestamp"] == 1.0
        assert d["winner_arxiv_id"] == "x"
        assert d["input_arxiv_ids"] == ["a", "b"]
        assert d["source"] == "mock"

    def test_missing_decisions_returns_empty(self, tmp_path):
        path = str(tmp_path / "nonexistent.jsonl")
        loaded = read_decisions(path=path)
        assert loaded == []


# ── Joint test with real catalog ─────────────────────────────────

class TestJointWithMultiPaper:
    """End-to-end: read_papers() → save → load → select_best → save decision."""

    def test_full_pipeline(self, tmp_path, monkeypatch):
        from src.v3_multipaper import read_papers
        from src.v3_judge import select_best

        summaries_path = str(tmp_path / "summaries.jsonl")
        decisions_path = str(tmp_path / "decisions.jsonl")

        # Step 1: read papers
        summaries = read_papers()
        assert len(summaries) >= 5

        # Step 2: save summaries
        save_summaries(summaries, path=summaries_path)
        assert os.path.exists(summaries_path)

        # Step 3: load summaries (verify roundtrip)
        loaded = read_summaries(path=summaries_path)
        assert len(loaded) == len(summaries)
        assert loaded[0].paper_arxiv_id == summaries[0].paper_arxiv_id

        # Step 4: select best (mock fallback)
        winner = select_best(loaded, config=None)
        assert winner in loaded

        # Step 5: save decision
        save_decision(winner, loaded, source="mock",
                      path=decisions_path)
        assert os.path.exists(decisions_path)

        # Step 6: read decisions
        decisions = read_decisions(path=decisions_path)
        assert len(decisions) == 1
        assert decisions[0].winner_arxiv_id == winner.paper_arxiv_id
        assert decisions[0].source == "mock"

    def test_pipeline_with_mocked_llm(self, tmp_path):
        """End-to-end with a mocked LLM response."""
        from src.v3_multipaper import read_papers
        from src.v3_judge import select_best
        import unittest.mock as mock

        summaries_path = str(tmp_path / "summaries.jsonl")
        decisions_path = str(tmp_path / "decisions.jsonl")

        # Take just 3 papers for determinism
        all_papers = read_papers()
        summaries = all_papers[:3]
        save_summaries(summaries, path=summaries_path)

        # Mock LLM to pick the second paper
        with mock.patch(
            "src.v3_judge._call_llm",
            return_value=f'{{"best_arxiv_id": "{summaries[1].paper_arxiv_id}"}}',
        ):
            winner = select_best(summaries, config={"fake": True})

        assert winner.paper_arxiv_id == summaries[1].paper_arxiv_id
        save_decision(winner, summaries, source="llm",
                      path=decisions_path)
        decisions = read_decisions(path=decisions_path)
        assert decisions[0].source == "llm"


# ── Default path uses upgrades/ ─────────────────────────────────

class TestDefaultPaths:
    def test_default_summaries_path(self):
        assert DEFAULT_SUMMARIES_PATH.endswith("judge_summaries.jsonl")

    def test_default_decisions_path(self):
        assert DEFAULT_DECISIONS_PATH.endswith("judge_decisions.jsonl")