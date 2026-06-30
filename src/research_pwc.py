"""Papers With Code client — trending papers and benchmark data.

[STABLE v1.2.0] — HTML parsing with caching, graceful degradation.

No official API; uses HTML scraping with BeautifulSoup.
Endpoints:
  - Trending: https://paperswithcode.com/
  - Search:   https://paperswithcode.com/search?q={query}
  - Paper:    https://paperswithcode.com/paper/{slug}
"""
import hashlib
import logging
import os
import pickle
import re
import time as _time
import urllib.error
import urllib.request
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

PWC_BASE = "https://paperswithcode.com"
_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "upgrades", "pwc_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)


def _cached_fetch(url: str, cache_seconds: int = 3600) -> Optional[bytes]:
    """Fetch URL with local file cache. Returns raw bytes or None on failure."""
    key = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(_CACHE_DIR, key + ".pkl")
    if os.path.exists(cache_file):
        age = _time.time() - os.path.getmtime(cache_file)
        if age < cache_seconds:
            with open(cache_file, "rb") as f:
                return pickle.load(f)

    req = urllib.request.Request(url, headers={"User-Agent": "SelfUpgradeAgent/1.2"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                _time.sleep(2 ** attempt)
                continue
            logger.debug(f"PwC HTTP {e.code} for {url}")
            return None
        except Exception as e:
            logger.debug(f"PwC fetch error: {e}")
            return None
    return None


def _extract_arxiv_id(text: str) -> Optional[str]:
    """Extract arXiv ID from a URL or text containing an arXiv link."""
    if not text:
        return None
    # Match arXiv ID patterns: 2301.12345 or 2301.12345v2
    match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?', text)
    if match:
        return match.group(1)
    return None


def _parse_trending_from_html(html: str) -> List[Dict]:
    """Parse Papers With Code trending page HTML.

    Extracts paper cards with title, arxiv_id, stars, and abstract snippet.

    Strategy: split on '<div class="paper-card"' tags, then process each segment
    up to the next card boundary. This handles arbitrary nesting without a full
    HTML parser.

    Args:
        html: Raw HTML string from paperswithcode.com.

    Returns:
        List of dicts with keys: title, arxiv_id, stars, url, abstract.
    """
    if not html:
        return []

    papers = []

    # Split on paper-card opening tags to isolate individual cards
    card_segments = re.split(
        r'<div[^>]*class="[^"]*paper-card[^"]*"[^>]*>',
        html,
    )

    # First segment is everything before the first paper-card, skip it
    for segment in card_segments[1:]:
        # Find the boundary: next paper-card opening tag or end of string
        next_card = re.search(
            r'<div[^>]*class="[^"]*paper-card[^"]*"[^>]*>', segment
        )
        end_idx = next_card.start() if next_card else len(segment)
        card = segment[:end_idx]

        # Title: <h1><a href="/paper/...">Title</a></h1>
        title_match = re.search(
            r'<h1[^>]*>.*?<a[^>]*href="/paper/[^"]*"[^>]*>(.*?)</a>',
            card, re.DOTALL,
        )
        title = title_match.group(1).strip() if title_match else ""
        if not title:
            continue  # Skip cards without recognizable title

        # arXiv ID: from any arxiv link in the card
        arxiv_match = re.search(
            r'https?://arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?',
            card,
        )
        arxiv_id = arxiv_match.group(1) if arxiv_match else None

        # Stars: <span class="badge-*">N stars</span>
        stars_match = re.search(
            r'<span[^>]*class="[^"]*badge[^"]*"[^>]*>(.*?)</span>',
            card,
        )
        stars = stars_match.group(1).strip() if stars_match else ""

        # Abstract/description
        abstract_match = re.search(
            r'<p[^>]*class="[^"]*(?:abstract|item-strip)[^"]*"[^>]*>(.*?)</p>',
            card, re.DOTALL,
        )
        abstract = re.sub(r'<[^>]+>', '', abstract_match.group(1).strip()) if abstract_match else ""

        url = ""
        url_match = re.search(r'<a[^>]*href="(/paper/[^"]*)"[^>]*>', card)
        if url_match:
            url = PWC_BASE + url_match.group(1)

        papers.append({
            "title": title,
            "arxiv_id": arxiv_id,
            "stars": stars,
            "url": url,
            "abstract": abstract[:200],
        })

    return papers


def _parse_search_results(html: str) -> List[Dict]:
    """Parse PwC search results page.

    Similar structure to trending page but with different wrapping.
    """
    # Reuse trending parser — the card structure is similar
    return _parse_trending_from_html(html)


def fetch_trending_papers(max_results: int = 10) -> List[Dict]:
    """Fetch trending papers from Papers With Code.

    Args:
        max_results: Maximum number of results to return.

    Returns:
        List of dicts with keys: title, arxiv_id, stars, url, abstract.
        Returns empty list on any error (graceful degradation).
    """
    # Strategy: Selenium first (robust JS rendering), regex as fallback
    try:
        # Try Selenium
        from src.scraper import scrape_pwc_trending, check_selenium_available
        if check_selenium_available():
            papers = scrape_pwc_trending(max_results)
            if papers:
                logger.info(f"PwC (Selenium): {len(papers)} papers")
                return papers
    except Exception as e:
        logger.debug(f"PwC Selenium fallback: {e}")

    # Fallback: regex HTML parsing
    try:
        data = _cached_fetch(PWC_BASE, cache_seconds=3600)
        if not data:
            logger.debug("PwC trending: no data returned")
            return []

        html = data.decode("utf-8", errors="replace")
        papers = _parse_trending_from_html(html)
        logger.info(f"PwC trending (regex): {len(papers)} papers found")
        return papers[:max_results]
    except Exception as e:
        logger.debug(f"PwC trending error: {e}")
        return []


def search_pwc(query: str, max_results: int = 10) -> List[Dict]:
    """Search Papers With Code for a query string.

    Args:
        query: Search query (e.g., "reasoning agent").
        max_results: Maximum number of results.

    Returns:
        List of paper dicts.
    """
    try:
        import urllib.parse
        encoded = urllib.parse.quote(query)
        url = f"{PWC_BASE}/search?q={encoded}"
        data = _cached_fetch(url, cache_seconds=3600)
        if not data:
            return []

        html = data.decode("utf-8", errors="replace")
        results = _parse_search_results(html)
        logger.info(f"PwC search '{query}': {len(results)} results")
        return results[:max_results]
    except Exception as e:
        logger.debug(f"PwC search error: {e}")
        return []
