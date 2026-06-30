"""Tests for src/filter.py"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.filter import score_paper, filter_papers
from src.research import Paper
from src.config import FilterConfig


class TestKeywordFilter:
    """Pure keyword scoring (fallback when no LLM)."""

    def test_score_paper_returns_valid_ranges(self):
        p = Paper(arxiv_id="1", title="Improving Agent Performance",
                  authors="A", published="2024",
                  abstract="We propose a novel method that outperforms baselines "
                           "on agent planning and tool use benchmarks.",
                  categories="cs.AI")
        scored = score_paper(p, FilterConfig(), use_llm=False)
        assert 0 <= scored.abstract_score <= 10
        assert 0 <= scored.applicability_score <= 10
        assert 0 <= scored.novelty_score <= 10
        assert scored.total_score >= 0

    def test_filter_ranks_by_total_score(self):
        papers = [
            Paper(arxiv_id="1", title="Revolutionary Agent AI",
                  authors="A", published="2024",
                  abstract="A groundbreaking multi-agent coordination framework.",
                  categories="cs.AI"),
            Paper(arxiv_id="2", title="Chemistry Paper",
                  authors="B", published="2024",
                  abstract="A study of chemical bonds.",
                  categories="cs.CE"),
        ]
        config = FilterConfig(min_abstract_score=0, min_applicability_score=0,
                              min_novelty_score=0, max_papers_to_consider=2)
        # enrich_citations=False avoids hitting Semantic Scholar (network call).
        results = filter_papers(papers, config, use_llm=False, enrich_citations=False)
        assert len(results) == 2
        assert results[0].total_score >= results[1].total_score

    def test_filter_removes_low_scores(self):
        papers = [Paper(arxiv_id="1", title="AI Paper", authors="A",
                        published="2024",
                        abstract="A method for agent self-improvement.",
                        categories="cs.AI")]
        config = FilterConfig(min_abstract_score=99, min_applicability_score=99,
                              min_novelty_score=99)
        results = filter_papers(papers, config, use_llm=False, enrich_citations=False)
        assert len(results) == 0


@pytest.mark.llm
class TestLLMFilter:
    """LLM-enhanced scoring (requires .env)."""

    def test_llm_score_paper_returns_valid_ranges(self):
        p = Paper(arxiv_id="1", title="Multi-Agent Coordination with RL",
                  authors="A", published="2024",
                  abstract="We propose a novel multi-agent framework using "
                           "reinforcement learning for task delegation.",
                  categories="cs.AI")
        scored = score_paper(p, FilterConfig(), use_llm=True)
        assert 0 <= scored.abstract_score <= 10
        assert 0 <= scored.applicability_score <= 10
        assert 0 <= scored.novelty_score <= 10

    def test_llm_returns_json_scores(self):
        papers = [Paper(arxiv_id="1", title="Irrelevant Biology Paper",
                        authors="B", published="2024",
                        abstract="A study of cell division mechanisms in yeast.",
                        categories="q-bio.SC")]
        results = filter_papers(papers, FilterConfig(), use_llm=True)
        assert len(results) <= 1
        if results:
            assert results[0].applicability_score < 5  # biology != agent
