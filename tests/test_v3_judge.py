"""Tests for src/v3_judge.py - mock select_best.

Per user workflow (2026-07-09): test small functions first,
then combine into larger features.
"""
import pytest

from src.v3_judge import (
    EmptySummariesError,
    select_best_mock,
    select_best,
    is_mock,
    _build_judge_prompt,
    _parse_llm_response,
)
from src.v3_multipaper import PaperSummary


def _make(id_: str, plan: str = "plan", idea: str = "idea",
          viewpoint: str = "vp") -> PaperSummary:
    return PaperSummary(
        paper_arxiv_id=id_,
        title=f"Title {id_}",
        idea=idea,
        viewpoint=viewpoint,
        plan=plan,
    )


class TestEmptySummaries:
    def test_empty_raises(self):
        with pytest.raises(EmptySummariesError):
            select_best_mock([])


class TestSingleSummary:
    def test_returns_the_only_one(self):
        s = _make("a")
        assert select_best_mock([s]) is s

    def test_with_custom_ranking_returns_it(self):
        s = _make("a")
        assert select_best_mock([s], ranking_fn=lambda x: 0) is s


class TestMultipleSummaries:
    def test_default_ranking_picks_longest_plan(self):
        s1 = _make("a", plan="short")
        s2 = _make("b", plan="a longer plan with more detail")
        s3 = _make("c", plan="medium plan here")
        winner = select_best_mock([s1, s2, s3])
        # s2 has longest plan * 2 = highest rank
        assert winner.paper_arxiv_id == "b"

    def test_custom_ranking_fn(self):
        s1 = _make("a", plan="long plan here")
        s2 = _make("b", plan="short")
        # rank by idea length instead of plan
        winner = select_best_mock(
            [s1, s2],
            ranking_fn=lambda s: len(s.idea),
        )
        # Both have same idea length, stable sort picks first
        assert winner.paper_arxiv_id == "a"

    def test_custom_ranking_picks_highest(self):
        s1 = _make("a")
        s2 = _make("b")
        s3 = _make("c")
        # rank c highest
        ranks = {"a": 1.0, "b": 2.0, "c": 10.0}
        winner = select_best_mock(
            [s1, s2, s3],
            ranking_fn=lambda s: ranks[s.paper_arxiv_id],
        )
        assert winner.paper_arxiv_id == "c"

    def test_ties_use_input_order(self):
        """When ranks are equal, stable sort preserves input order."""
        s1 = _make("a")
        s2 = _make("b")
        s3 = _make("c")
        # All ranks equal
        winner = select_best_mock([s1, s2, s3], ranking_fn=lambda s: 1.0)
        # Stable sort: first one wins
        assert winner.paper_arxiv_id == "a"

    def test_default_ranking_weights_plan_more(self):
        """Plan is weighted 2x vs idea + viewpoint in default rank."""
        # Make plan dominate
        s_long_plan = _make("lp", plan="x" * 100, idea="", viewpoint="")
        s_long_vp = _make("vp", plan="", idea="", viewpoint="x" * 100)
        winner = select_best_mock([s_long_plan, s_long_vp])
        # long plan: 100 * 2 = 200
        # long viewpoint: 100 * 1 = 100
        assert winner.paper_arxiv_id == "lp"


class TestIsMock:
    def test_is_mock_returns_true(self):
        assert is_mock() is True


class TestMockIntegrationWithMultiPaper:
    """Joint test: read_papers() + select_best_mock() together."""

    def test_pick_from_real_catalog(self):
        from src.v3_multipaper import read_papers
        papers = read_papers()
        assert len(papers) >= 5, "catalog should have >= 5 papers"
        winner = select_best_mock(papers)
        # Winner must be one of the papers
        assert winner in papers

    def test_pick_subset(self):
        from src.v3_multipaper import read_papers
        papers = read_papers()
        # Take first 3
        subset = papers[:3]
        winner = select_best_mock(subset)
        assert winner in subset

    def test_custom_rank_on_real_catalog(self):
        from src.v3_multipaper import read_papers
        papers = read_papers()
        # Pick the one with the shortest title (just to verify
        # the ranking_fn is applied correctly)
        winner = select_best_mock(
            papers,
            ranking_fn=lambda s: -len(s.title),  # negative = shortest first
        )
        assert winner in papers


# ── Step 1.2: Real LLM judge tests ──────────────────────────────

class TestBuildJudgePrompt:
    """The prompt should list all summaries clearly so the LLM
    can reason about them."""

    def test_includes_all_summaries(self):
        summaries = [
            PaperSummary("a", "Title A", "idea A", "vp A", "plan A"),
            PaperSummary("b", "Title B", "idea B", "vp B", "plan B"),
        ]
        prompt = _build_judge_prompt(summaries)
        assert "arxiv_id=a" in prompt
        assert "arxiv_id=b" in prompt
        assert "Title A" in prompt
        assert "plan B" in prompt

    def test_requests_json(self):
        summaries = [PaperSummary("a", "A", "i", "v", "p")]
        prompt = _build_judge_prompt(summaries)
        assert "best_arxiv_id" in prompt
        assert "JSON" in prompt


class TestParseLlmResponse:
    """Extract best_arxiv_id from various LLM response formats."""

    def test_clean_json(self):
        text = '{"best_arxiv_id": "self-harness", "reason": "good"}'
        assert _parse_llm_response(text) == "self-harness"

    def test_markdown_fenced(self):
        text = '```json\n{"best_arxiv_id": "reflexion"}\n```'
        assert _parse_llm_response(text) == "reflexion"

    def test_extra_spaces(self):
        text = '{ "best_arxiv_id" :  "constitutional-ai" }'
        assert _parse_llm_response(text) == "constitutional-ai"

    def test_no_match_returns_none(self):
        assert _parse_llm_response("I think reflexion is best") is None

    def test_empty_returns_none(self):
        assert _parse_llm_response("") is None

    def test_partial_match_returns_none(self):
        # Only has reason, not best_arxiv_id
        text = '{"reason": "good"}'
        assert _parse_llm_response(text) is None


class TestSelectBestFallback:
    """When config is None or LLM fails, fall back to mock."""

    def test_no_config_uses_mock(self):
        summaries = [
            PaperSummary("a", "A", "i", "v", "short"),
            PaperSummary("b", "B", "i", "v", "much longer plan here"),
        ]
        winner = select_best(summaries, config=None)
        # Falls back to mock: longest plan wins
        assert winner.paper_arxiv_id == "b"

    def test_empty_raises(self):
        with pytest.raises(EmptySummariesError):
            select_best([], config=None)


class TestSelectBestWithMockedLlm:
    """Mock the LLM via monkeypatch to test the real path."""

    def test_llm_returns_valid_id(self, monkeypatch):
        summaries = [
            PaperSummary("alpha", "Title A", "idea A", "vp A", "plan A"),
            PaperSummary("beta", "Title B", "idea B", "vp B", "plan B"),
        ]

        # Mock the _call_llm function to return a canned response
        def fake_call_llm(prompt, config):
            return '''{"best_arxiv_id": "beta", "reason": "B is better"}'''

        monkeypatch.setattr("src.v3_judge._call_llm", fake_call_llm)

        winner = select_best(summaries, config={"fake": True})
        assert winner.paper_arxiv_id == "beta"

    def test_llm_returns_unknown_id_falls_back_to_mock(self, monkeypatch):
        summaries = [
            PaperSummary("alpha", "A", "i", "v", "short"),
            PaperSummary("beta", "B", "i", "v", "much longer plan here"),
        ]

        def fake_call_llm(prompt, config):
            return '''{"best_arxiv_id": "ghost-paper", "reason": "x"}'''

        monkeypatch.setattr("src.v3_judge._call_llm", fake_call_llm)

        winner = select_best(summaries, config={"fake": True})
        # Unknown id -> fall back to mock: longest plan wins
        assert winner.paper_arxiv_id == "beta"

    def test_llm_returns_invalid_json_falls_back_to_mock(self, monkeypatch):
        summaries = [
            PaperSummary("alpha", "A", "i", "v", "short"),
            PaperSummary("beta", "B", "i", "v", "much longer plan here"),
        ]

        def fake_call_llm(prompt, config):
            return "I think beta is best because..."  # not JSON

        monkeypatch.setattr("src.v3_judge._call_llm", fake_call_llm)

        winner = select_best(summaries, config={"fake": True})
        # Unparseable -> fall back to mock: longest plan wins
        assert winner.paper_arxiv_id == "beta"

    def test_llm_raises_falls_back_to_mock(self, monkeypatch):
        summaries = [
            PaperSummary("alpha", "A", "i", "v", "short"),
            PaperSummary("beta", "B", "i", "v", "much longer plan here"),
        ]

        def fake_call_llm(prompt, config):
            raise RuntimeError("API down")

        monkeypatch.setattr("src.v3_judge._call_llm", fake_call_llm)

        winner = select_best(summaries, config={"fake": True})
        # Exception -> fall back to mock: longest plan wins
        assert winner.paper_arxiv_id == "beta"

    def test_llm_empty_response_falls_back(self, monkeypatch):
        summaries = [
            PaperSummary("alpha", "A", "i", "v", "short"),
            PaperSummary("beta", "B", "i", "v", "much longer plan here"),
        ]

        def fake_call_llm(prompt, config):
            return ""

        monkeypatch.setattr("src.v3_judge._call_llm", fake_call_llm)

        winner = select_best(summaries, config={"fake": True})
        # Empty -> fall back to mock: longest plan wins
        assert winner.paper_arxiv_id == "beta"
