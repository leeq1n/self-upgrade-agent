"""Tests for src/research.py"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.research import Paper, build_query_string, search_arxiv
from src.config import ResearchConfig


class TestPaperDataclass:
    def test_basic_fields(self):
        p = Paper(
            arxiv_id="2402.03300",
            title="Test Paper",
            authors="A. Author, B. Author",
            published="2024-02-03",
            abstract="This is a test abstract.",
            categories="cs.AI, cs.CL"
        )
        assert p.arxiv_id == "2402.03300"
        assert p.title == "Test Paper"
        assert p.authors == "A. Author, B. Author"
        assert p.published == "2024-02-03"
        assert p.abstract == "This is a test abstract."
        assert p.categories == "cs.AI, cs.CL"

    def test_default_citation_count(self):
        p = Paper(arxiv_id="1", title="T", authors="A", published="2024",
                  abstract="A", categories="cs.AI")
        assert p.citation_count == 0


class TestBuildQueryString:
    def test_single_keyword(self):
        config = ResearchConfig(keywords=["transformer"])
        q = build_query_string(config)
        assert "all:" in q
        assert "transformer" in q

    def test_multiple_keywords(self):
        config = ResearchConfig(keywords=["agent framework", "prompt technique"])
        q = build_query_string(config)
        # each keyword should be quoted and joined with OR
        assert "all:agent+framework" in q
        assert "all:prompt+technique" in q
        assert "OR" in q

    def test_includes_categories(self):
        config = ResearchConfig(keywords=["test"], categories=["cs.AI", "cs.LG"])
        q = build_query_string(config)
        assert "cat:cs.AI" in q
        assert "cat:cs.LG" in q


class TestSearchArxiv:
    """Integration tests that hit the real arXiv API (requires network)."""

    @pytest.mark.network
    def test_returns_papers_for_known_topic(self):
        config = ResearchConfig(keywords=["transformer"], max_papers_per_query=3,
                                arxiv_selenium_first=False)
        papers = search_arxiv(config)
        assert len(papers) > 0
        for p in papers:
            assert p.arxiv_id
            assert p.title
            assert p.abstract
            assert p.categories

    @pytest.mark.network
    def test_filters_withdrawn_papers(self):
        """Withdrawn papers should be excluded from results."""
        config = ResearchConfig(keywords=["transformer"], max_papers_per_query=3,
                                arxiv_selenium_first=False)
        papers = search_arxiv(config)
        for p in papers:
            assert "withdrawn" not in p.abstract.lower()

    def test_empty_keywords_returns_empty(self):
        config = ResearchConfig(keywords=[])
        papers = search_arxiv(config)
        assert len(papers) == 0
