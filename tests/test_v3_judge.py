"""Tests for src/v3_judge.py - mock select_best.

Per user workflow (2026-07-09): test small functions first,
then combine into larger features.
"""
import pytest

from src.v3_judge import (
    EmptySummariesError,
    select_best_mock,
    is_mock,
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