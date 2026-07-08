"""Tests for src/web.py - arxiv/s2 fetcher without API."""
import os, sys
sys.path.insert(0, r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent")

import pytest

from src.web import arxiv_listing, arxiv_paper, semanticscholar_paper, fetch_paper_full


def test_arxiv_listing_returns_real_ids():
    """arxiv_listing returns real arxiv IDs from arxiv.org listing page."""
    papers = arxiv_listing("cs.AI", limit=3)
    assert len(papers) >= 1, "should find at least 1 paper"
    for p in papers:
        # Real arxiv ID format: NNNN.NNNNN (e.g. 2406.01574)
        arxiv_id = p["arxiv_id"]
        parts = arxiv_id.split(".")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert parts[1].isdigit()
        assert p["abs_url"].startswith("https://arxiv.org/abs/")
        assert p["pdf_url"].startswith("https://arxiv.org/pdf/")


def test_arxiv_listing_caches_results():
    """Second call within TTL returns cached result (no second HTTP call)."""
    papers1 = arxiv_listing("cs.CL", limit=2)
    papers2 = arxiv_listing("cs.CL", limit=2)
    assert papers1 == papers2


def test_arxiv_paper_extracts_title():
    """arxiv_paper returns non-empty title for known paper."""
    p = arxiv_paper("2310.02170")
    assert p["title"], "title should not be empty"
    # Real title for 2310.02170 is "A Dynamic LLM-Powered Agent Network..."
    assert "Agent" in p["title"] or "agent" in p["title"].lower()


def test_arxiv_paper_extracts_abstract():
    """arxiv_paper returns non-empty abstract."""
    p = arxiv_paper("2310.02170")
    assert p["abstract"], "abstract should not be empty"
    assert len(p["abstract"]) > 100, "abstract should be substantial"


def test_arxiv_paper_extracts_authors():
    """arxiv_paper returns authors list."""
    p = arxiv_paper("2310.02170")
    assert len(p["authors"]) > 0
    # Known authors for 2310.02170
    assert any("Liu" in a for a in p["authors"])


def test_arxiv_paper_extracts_category():
    """arxiv_paper returns primary_category."""
    p = arxiv_paper("2310.02170")
    assert p["primary_category"], "primary_category should be set"
    assert "cs" in p["primary_category"].lower()


def test_semanticscholar_paper_graceful():
    """S2 fetch must not raise (graceful on network failure)."""
    # Should not raise even if S2 is unreachable
    out = semanticscholar_paper("2310.02170")
    assert "citation_count" in out
    assert isinstance(out["citation_count"], int)


def test_fetch_paper_full_merges():
    """fetch_paper_full combines arxiv + s2 data."""
    out = fetch_paper_full("2310.02170")
    assert "title" in out
    assert "abstract" in out
    assert "citation_count" in out


def test_cache_prevents_repeat_fetch():
    """Verify cache: arxiv_paper for same id returns same object quickly."""
    import time
    t0 = time.time()
    p1 = arxiv_paper("2406.01574")
    elapsed1 = time.time() - t0
    t0 = time.time()
    p2 = arxiv_paper("2406.01574")
    elapsed2 = time.time() - t0
    # Second call should be much faster (cache hit)
    assert elapsed2 < elapsed1, f"cache should make 2nd call faster: {elapsed1:.2f}s vs {elapsed2:.2f}s"
    assert p1 == p2