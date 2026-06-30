"""GitHub trending and search — discover repositories with related code.

[STABLE v1.2.0] — GitHub API + trending page scraping with caching.

Endpoints:
  - Search: https://api.github.com/search/repositories?q=...&sort=stars
  - Trending: https://github.com/trending/python?since=weekly

Optional: Set GITHUB_TOKEN env var to increase API rate limit (60→5000 req/h).
"""
import hashlib
import json
import logging
import os
import pickle
import re
import time as _time
import urllib.error
import urllib.request
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

GH_API = "https://api.github.com"
GH_TRENDING = "https://github.com/trending"
_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "upgrades", "gh_cache")
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

    headers = {"User-Agent": "SelfUpgradeAgent/1.2",
               "Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
            return data
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 2:
                wait = 2 ** attempt
                logger.debug(f"GitHub rate limited, waiting {wait}s...")
                _time.sleep(wait)
                continue
            logger.debug(f"GitHub HTTP {e.code} for {url}")
            return None
        except Exception as e:
            logger.debug(f"GitHub fetch error: {e}")
            return None
    return None


def _parse_trending_html(html: str) -> List[Dict]:
    """Parse GitHub trending page HTML.

    Extracts repo cards with name, description, language, stars_today.

    Args:
        html: Raw HTML from github.com/trending.

    Returns:
        List of dicts with: name, description, language, stars_today, url.
    """
    if not html:
        return []

    repos = []

    # Each repo is in an <article class="Box-row">
    articles = re.split(r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>', html)

    for article in articles[1:]:  # Skip content before first article
        # Name: <a href="/owner/repo">owner / <span>repo</span></a>
        name_match = re.search(
            r'<a[^>]*href="/([^"]+)"[^>]*>\s*([^<]+)\s*/\s*<span[^>]*>([^<]+)</span>',
            article, re.DOTALL,
        )
        if not name_match:
            continue
        full_name = name_match.group(1).strip()

        # Description: <p class="col-9 color-fg-muted ...">
        desc_match = re.search(
            r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>\s*(.*?)\s*</p>',
            article, re.DOTALL,
        )
        description = desc_match.group(1).strip() if desc_match else ""

        # Language
        lang_match = re.search(
            r'itemprop="programmingLanguage"[^>]*>\s*([^<]+)\s*<',
            article,
        )
        language = lang_match.group(1).strip() if lang_match else ""

        # Stars today
        stars_match = re.search(
            r'float-sm-right[^>]*>\s*(.*?)\s*</span>',
            article,
        )
        stars_today = stars_match.group(1).strip() if stars_match else ""

        repos.append({
            "name": full_name,
            "description": description,
            "language": language,
            "stars_today": stars_today,
            "url": f"https://github.com/{full_name}",
        })

    return repos


def _parse_repo_search_json(data: dict) -> List[Dict]:
    """Parse GitHub search API JSON response.

    Args:
        data: Decoded JSON from /search/repositories.

    Returns:
        List of dicts with: name, description, stars, language, url, topics.
    """
    items = data.get("items", [])
    repos = []
    for item in items:
        repos.append({
            "name": item.get("full_name", ""),
            "description": item.get("description", ""),
            "stars": item.get("stargazers_count", 0),
            "language": item.get("language", ""),
            "url": item.get("html_url", ""),
            "topics": item.get("topics", []),
        })
    return repos


def search_github_repos(query: str = "agent LLM reasoning",
                        max_results: int = 10) -> List[Dict]:
    """Search GitHub repositories by keyword.

    Uses the GitHub Search API (60 req/h without token, 5000 with token).

    Args:
        query: Search query string.
        max_results: Maximum number of results.

    Returns:
        List of repo dicts. Empty list on failure (graceful degradation).
    """
    try:
        import urllib.parse
        encoded = urllib.parse.quote(query)
        url = f"{GH_API}/search/repositories?q={encoded}&sort=stars&per_page={min(max_results, 30)}"
        data = _cached_fetch(url, cache_seconds=3600)
        if not data:
            return []

        result = json.loads(data.decode("utf-8"))
        repos = _parse_repo_search_json(result)
        logger.info(f"GitHub search '{query}': {len(repos)} repos")
        return repos[:max_results]
    except Exception as e:
        logger.debug(f"GitHub search error: {e}")
        return []


def search_trending_weekly(language: str = "python") -> List[Dict]:
    """Fetch GitHub weekly trending repositories.

    Args:
        language: Programming language filter (default: python).

    Returns:
        List of repo dicts. Empty list on failure.
    """
    try:
        url = f"{GH_TRENDING}/{language}?since=weekly"
        data = _cached_fetch(url, cache_seconds=3600)
        if not data:
            return []

        html = data.decode("utf-8", errors="replace")
        repos = _parse_trending_html(html)
        logger.info(f"GitHub trending ({language}): {len(repos)} repos")
        return repos
    except Exception as e:
        logger.debug(f"GitHub trending error: {e}")
        return []
