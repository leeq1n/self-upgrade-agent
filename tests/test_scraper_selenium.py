"""Tests for Selenium-based scraper functions (PwC + GitHub + health check).

These tests mock Selenium WebDriver to verify element-finding logic
without requiring a real browser.
"""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock


class TestSeleniumPwC:
    """Test Selenium-based Papers With Code scraping."""

    def make_mock_driver(self, titles=None, arxiv_links=None):
        """Build a mock Selenium driver with find_elements support."""
        driver = MagicMock()

        # Mock find_elements for paper cards
        cards = []
        if titles:
            for i, title_text in enumerate(titles):
                card = MagicMock()
                title_el = MagicMock()
                title_el.text = title_text
                card.find_element.return_value = title_el

                # Mock arxiv links
                links = []
                arxiv = arxiv_links[i] if i < len(arxiv_links) else None
                if arxiv:
                    link = MagicMock()
                    link.get_attribute.return_value = arxiv
                    links.append(link)
                card.find_elements.return_value = links
                cards.append(card)

        driver.find_elements.return_value = cards
        return driver

    def test_scrape_pwc_extracts_titles_and_arxiv_ids(self):
        """Selenium PwC scraping extracts paper titles and arXiv IDs."""
        from src.scraper import scrape_pwc_trending

        driver = self.make_mock_driver(
            titles=["Awesome Method for AI", "Better Reasoning"],
            arxiv_links=["https://arxiv.org/abs/2301.12345", "https://arxiv.org/abs/2302.67890"],
        )

        with patch("src.scraper._get_driver", return_value=driver):
            papers = scrape_pwc_trending(max_results=3)

        assert len(papers) == 2
        assert papers[0]["title"] == "Awesome Method for AI"
        assert papers[0]["arxiv_id"] == "2301.12345"
        assert papers[1]["arxiv_id"] == "2302.67890"
        driver.quit.assert_called_once()

    def test_scrape_pwc_handles_exception(self):
        """Selenium PwC scraping returns [] on error."""
        from src.scraper import scrape_pwc_trending

        with patch("src.scraper._get_driver", side_effect=Exception("no browser")):
            papers = scrape_pwc_trending(max_results=5)
            assert papers == []

    def test_scrape_pwc_keeps_cards_without_arxiv(self):
        """Cards without arXiv links are kept (still useful for discovery)."""
        from src.scraper import scrape_pwc_trending

        driver = self.make_mock_driver(
            titles=["Paper A", "Paper B"],
            arxiv_links=["https://arxiv.org/abs/2301.11111", None],
        )

        with patch("src.scraper._get_driver", return_value=driver):
            papers = scrape_pwc_trending(max_results=5)

        assert len(papers) == 2
        assert papers[0]["arxiv_id"] == "2301.11111"
        assert papers[1]["arxiv_id"] is None  # Kept, just no arXiv ID


class TestSeleniumGitHub:
    """Test Selenium-based GitHub trending scraping."""

    def make_mock_gh_driver(self, repos_data):
        """Build a mock Selenium driver for GitHub trending.

        repos_data: list of (owner/name, description, language) tuples.
        """
        driver = MagicMock()
        articles = []
        for full_name, desc, lang in repos_data:
            article = MagicMock()
            # h2 > a
            h2 = MagicMock()
            link = MagicMock()
            link.get_attribute.return_value = full_name
            link.text = full_name
            h2.find_element.return_value = link
            # description p
            desc_p = MagicMock()
            desc_p.text = desc
            # language span
            lang_span = MagicMock()
            lang_span.text = lang
            # stars span
            stars_span = MagicMock()
            stars_span.text = "100 stars today"

            # Mock find_element to return different elements based on selector
            def mock_find_element(by=None, value=None, _h2=h2, _desc=desc_p,
                                  _lang=lang_span, _stars=stars_span, **kwargs):
                selector = value or ""
                if "h2 a" in selector or "h2" in selector:
                    return _h2
                elif "itemprop" in selector:
                    return _lang
                elif "float-sm-right" in selector or "d-inline-block" in selector:
                    return _stars
                elif "p" == selector.split(",")[0].strip():
                    return _desc
                return MagicMock()

            article.find_element = mock_find_element
            articles.append(article)

        driver.find_elements.return_value = articles
        return driver

    @patch("src.scraper.time.sleep", return_value=None)
    def test_scrape_github_extracts_repos(self, mock_sleep):
        """Selenium GitHub scraping extracts repos with descriptions."""
        from src.scraper import scrape_github_trending

        driver = self.make_mock_gh_driver([
            ("owner/awesome-tool", "An awesome AI framework", "Python"),
            ("dev/cool-lib", "Cool library for LLMs", "TypeScript"),
        ])

        with patch("src.scraper._get_driver", return_value=driver):
            repos = scrape_github_trending(language="python")

        assert len(repos) == 2
        # Description comes from .text which is a direct string, not MagicMock
        descs = [r.get("description", "") for r in repos]
        assert "An awesome AI framework" in descs
        assert "Cool library for LLMs" in descs
        driver.quit.assert_called_once()

    def test_scrape_github_handles_exception(self):
        """Selenium GitHub scraping returns [] on error."""
        from src.scraper import scrape_github_trending

        with patch("src.scraper._get_driver", side_effect=Exception("no browser")):
            repos = scrape_github_trending()
            assert repos == []


class TestSeleniumHealthCheck:
    """Test Selenium availability check."""

    def test_check_selenium_available_returns_true(self):
        """When Chrome driver starts, returns True."""
        from src.scraper import check_selenium_available

        mock_driver = MagicMock()
        with patch("src.scraper._get_driver", return_value=mock_driver):
            result = check_selenium_available()
            assert result is True
            mock_driver.quit.assert_called_once()

    def test_check_selenium_available_returns_false_on_error(self):
        """When driver fails, returns False."""
        from src.scraper import check_selenium_available

        with patch("src.scraper._get_driver", side_effect=Exception("no chrome")):
            result = check_selenium_available()
            assert result is False
