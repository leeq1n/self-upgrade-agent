"""Tests for src/keyword_expander.py.

Covers the trending-keyword cache used by the daily self-upgrade loop.
"""
import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import keyword_expander
from src.keyword_expander import (
    extract_ngrams,
    extract_trending_keywords,
    load_trending_keywords,
    merge_keywords,
    update_trending_keywords,
)


class TestExtractNgrams:
    def test_basic_bigrams(self):
        # Use distinct words so we don't get self-pairs (e.g. "agent agent").
        text = "the agent learns to plan the planning the reasoning"
        ngrams = extract_ngrams(text, n=2, top_k=5)
        # "agent learns" and "the planning" should both appear.
        joined = " ".join(ngrams)
        assert "agent learns" in joined
        assert "the planning" in joined

    def test_empty(self):
        assert extract_ngrams("") == []

    def test_top_k_limits(self):
        text = " ".join(f"word{i}" for i in range(50))
        result = extract_ngrams(text, n=1, top_k=3)
        assert len(result) <= 3


class TestMergeKeywords:
    def test_dedupes_case_insensitive(self):
        merged = merge_keywords(
            existing=["Agent", "Planning"],
            new=["agent", "REASONING", "tool"],
        )
        # "Agent" and "agent" should collapse into one entry.
        lowered = [k.lower() for k in merged]
        assert lowered.count("agent") == 1
        assert "reasoning" in lowered
        assert "tool" in lowered

    def test_new_take_precedence(self):
        # By design, merge_keywords puts NEW keywords first (they represent
        # latest trends); existing keywords are appended.
        merged = merge_keywords(["A", "B"], ["B", "C"])
        # C is new → should be near the front.
        assert merged.index("C") < merged.index("A")
        # B (in both) appears once and stays in the list.
        assert merged.count("B") == 1


class TestLoadTrendingKeywords:
    def test_returns_empty_when_no_cache(self, monkeypatch):
        # Point the module at a non-existent path.
        monkeypatch.setattr(keyword_expander, "_TRENDING_CACHE", "/nonexistent/_x.json")
        assert load_trending_keywords() == []

    def test_loads_from_cache(self, monkeypatch, tmp_path):
        cache_path = str(tmp_path / "trending.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"keywords": ["alpha", "beta"]}, f)
        monkeypatch.setattr(keyword_expander, "_TRENDING_CACHE", cache_path)
        result = load_trending_keywords()
        assert result == ["alpha", "beta"]

    def test_handles_corrupt_cache(self, monkeypatch, tmp_path):
        cache_path = str(tmp_path / "trending.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        monkeypatch.setattr(keyword_expander, "_TRENDING_CACHE", cache_path)
        # Should not raise; should return [].
        assert load_trending_keywords() == []


class TestNodeResearchConsumesTrending:
    """The pipeline's node_research should append trending keywords to the
    search query.  This is what makes the 'loop' close: yesterday's findings
    influence tomorrow's searches.
    """

    def test_appends_unique_trending(self, monkeypatch, tmp_path):
        from src.pipeline_lg import node_research
        from src.config import Config
        from src import pipeline_lg as plg

        # Set up a trending cache with one keyword NOT in the base config.
        cache_path = str(tmp_path / "trending.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"keywords": ["agentic-workflow", "toolformer"]}, f)
        monkeypatch.setattr(keyword_expander, "_TRENDING_CACHE", cache_path)

        # Stub the actual search.  patch pipeline_lg.search_arxiv because
        # that's the binding used inside node_research (import-time binding).
        called_keywords = []
        monkeypatch.setattr(
            plg, "search_arxiv",
            lambda cfg: (called_keywords.append(list(cfg.keywords)) or []),
        )

        cfg = Config()
        cfg.research.keywords = ["transformer", "agent"]
        state = {"config": cfg}
        node_research(state)

        # Trending keywords should be appended.
        assert called_keywords, "search_arxiv was not called"
        used = called_keywords[0]
        assert "transformer" in used  # base
        assert "agent" in used        # base
        assert "agentic-workflow" in used  # from trending
        assert "toolformer" in used

    def test_does_not_duplicate_base_keywords(self, monkeypatch, tmp_path):
        from src.pipeline_lg import node_research
        from src.config import Config
        from src import pipeline_lg as plg

        cache_path = str(tmp_path / "trending.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"keywords": ["transformer", "totally-new-term"]}, f)
        monkeypatch.setattr(keyword_expander, "_TRENDING_CACHE", cache_path)

        called_keywords = []
        monkeypatch.setattr(
            plg, "search_arxiv",
            lambda cfg: (called_keywords.append(list(cfg.keywords)) or []),
        )

        cfg = Config()
        cfg.research.keywords = ["transformer", "agent"]
        node_research({"config": cfg})

        used = called_keywords[0]
        # "transformer" must not be duplicated.
        assert used.count("transformer") == 1
        # "totally-new-term" should be added.
        assert "totally-new-term" in used
