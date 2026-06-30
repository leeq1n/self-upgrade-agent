"""Tests for Papers With Code integration."""
import os
import pytest
from unittest.mock import patch, MagicMock

# We test the module's parsing logic without live network calls
from src.research_pwc import (
    _parse_trending_from_html,
    _parse_search_results,
    _extract_arxiv_id,
)


class TestParseTrending:
    """Test HTML parsing of Papers With Code trending page."""

    def test_extract_arxiv_id_from_url(self):
        """Extract arXiv ID from various URL formats."""
        assert _extract_arxiv_id("https://arxiv.org/abs/2301.12345") == "2301.12345"
        assert _extract_arxiv_id("https://arxiv.org/abs/2301.12345v2") == "2301.12345"
        assert _extract_arxiv_id("https://arxiv.org/pdf/2301.12345.pdf") == "2301.12345"
        assert _extract_arxiv_id("no-arxiv-link") is None
        assert _extract_arxiv_id("") is None

    def test_parse_trending_extracts_papers(self):
        """Parse trending page HTML and extract paper data."""
        html = """
        <html><body>
        <div class="paper-card">
            <h1><a href="/paper/awesome-method">Awesome Method for AI</a></h1>
            <div class="paper-abstract">We propose a novel method for reasoning.</div>
            <a href="https://arxiv.org/abs/2305.67890">arXiv</a>
            <span class="badge-secondary">123 stars</span>
        </div>
        <div class="paper-card">
            <h1><a href="/paper/better-reasoning">Better Reasoning with Trees</a></h1>
            <div class="paper-abstract">Tree-based reasoning improves accuracy.</div>
            <a href="https://arxiv.org/pdf/2306.11111.pdf">arXiv</a>
            <span class="badge-secondary">89 stars</span>
        </div>
        </body></html>
        """
        papers = _parse_trending_from_html(html)
        assert len(papers) == 2
        assert papers[0]["title"] == "Awesome Method for AI"
        assert papers[0]["arxiv_id"] == "2305.67890"
        assert papers[0]["stars"] == "123 stars"
        assert papers[1]["arxiv_id"] == "2306.11111"

    def test_parse_trending_empty(self):
        """Empty HTML returns empty list."""
        assert _parse_trending_from_html("") == []
        assert _parse_trending_from_html("<html></html>") == []

    def test_parse_search_results(self):
        """Parse search results page."""
        html = """
        <html><body>
        <div class="paper-card">
            <h1><a href="/paper/great-paper">Great Paper Title</a></h1>
            <p class="item-strip">Published in NeurIPS 2024</p>
            <a href="https://arxiv.org/abs/2401.99999">arXiv</a>
        </div>
        </body></html>
        """
        results = _parse_search_results(html)
        assert len(results) == 1
        assert results[0]["title"] == "Great Paper Title"
        assert results[0]["arxiv_id"] == "2401.99999"


class TestNoNetworkCalls:
    """Verify that module functions accept mock responses gracefully."""

    def test_fetch_trending_papers_handles_network_error(self):
        """fetch_trending_papers should return [] on all paths failing."""
        from src.research_pwc import fetch_trending_papers
        # Mock both Selenium and regex paths (import is local in function)
        with patch("src.scraper.check_selenium_available", return_value=False), \
             patch("src.research_pwc._cached_fetch", side_effect=Exception("timeout")):
            result = fetch_trending_papers(max_results=5)
            assert result == []
