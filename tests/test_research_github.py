"""Tests for GitHub trending search integration."""
import pytest
from unittest.mock import patch, MagicMock
import json

from src.research_github import (
    _parse_trending_html,
    _parse_repo_search_json,
)


class TestParseGitHub:
    """Test HTML/JSON parsing without live network calls."""

    def test_parse_trending_extracts_repos(self):
        """Parse GitHub trending page HTML."""
        html = """
        <html><body>
        <article class="Box-row">
            <h2 class="h3 lh-condensed">
                <a href="/owner/awesome-project">owner / <span>awesome-project</span></a>
            </h2>
            <p class="col-9 color-fg-muted my-1 pr-4">
                An awesome AI agent framework for reasoning.
            </p>
            <span class="d-inline-block float-sm-right">1,234 stars today</span>
            <span itemprop="programmingLanguage">Python</span>
        </article>
        <article class="Box-row">
            <h2 class="h3 lh-condensed">
                <a href="/dev/cool-tool">dev / <span>cool-tool</span></a>
            </h2>
            <p class="col-9 color-fg-muted my-1 pr-4">
                Cool tool for LLM evaluation.
            </p>
            <span class="d-inline-block float-sm-right">567 stars today</span>
            <span itemprop="programmingLanguage">TypeScript</span>
        </article>
        </body></html>
        """
        repos = _parse_trending_html(html)
        assert len(repos) == 2
        assert repos[0]["name"] == "owner/awesome-project"
        assert repos[0]["description"] == "An awesome AI agent framework for reasoning."
        assert repos[0]["language"] == "Python"
        assert repos[0]["stars_today"] == "1,234 stars today"
        assert repos[1]["name"] == "dev/cool-tool"

    def test_parse_trending_empty(self):
        """Empty HTML returns empty list."""
        assert _parse_trending_html("") == []
        assert _parse_trending_html("<html></html>") == []

    def test_parse_repo_search_json(self):
        """Parse GitHub search API JSON response."""
        response = {
            "total_count": 2,
            "items": [
                {
                    "full_name": "langchain-ai/langchain",
                    "description": "Building applications with LLMs",
                    "stargazers_count": 95000,
                    "language": "Python",
                    "html_url": "https://github.com/langchain-ai/langchain",
                    "topics": ["llm", "agents"],
                },
                {
                    "full_name": "microsoft/autogen",
                    "description": "Multi-agent conversation framework",
                    "stargazers_count": 35000,
                    "language": "Python",
                    "html_url": "https://github.com/microsoft/autogen",
                    "topics": ["multi-agent", "conversation"],
                },
            ],
        }
        repos = _parse_repo_search_json(response)
        assert len(repos) == 2
        assert repos[0]["name"] == "langchain-ai/langchain"
        assert repos[0]["stars"] == 95000
        assert repos[0]["topics"] == ["llm", "agents"]
        assert repos[1]["name"] == "microsoft/autogen"

    def test_parse_repo_search_empty(self):
        """Empty search results."""
        assert _parse_repo_search_json({"items": []}) == []
        assert _parse_repo_search_json({}) == []


class TestNoNetworkCalls:
    """Verify graceful degradation on network errors."""

    def test_search_github_repos_handles_error(self):
        """search_github_repos should return [] on error, not crash."""
        from src.research_github import search_github_repos
        with patch("src.research_github._cached_fetch", side_effect=Exception("timeout")):
            result = search_github_repos("test", max_results=5)
            assert result == []

    def test_search_trending_weekly_handles_error(self):
        """search_trending_weekly should return [] on error."""
        from src.research_github import search_trending_weekly
        with patch("src.research_github._cached_fetch", side_effect=Exception("timeout")):
            result = search_trending_weekly()
            assert result == []
