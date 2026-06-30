"""Semantic Scholar API client — citation data and paper discovery.

[FROZEN v1.1.0] — stable API wrapper, tested, do not modify.

Free tier: 1 req/s, 100 req / 5 min without API key.
Docs: https://api.semanticscholar.org/api-docs/graph

Key endpoints:
  - Paper search: /graph/v1/paper/search?query=...&fields=...
  - Paper by arXiv ID: /graph/v1/paper/ArXiv:{id}?fields=...
  - Citations: /graph/v1/paper/{paperId}/citations?fields=...
  - References: /graph/v1/paper/{paperId}/references?fields=...
"""
import hashlib
import json
import logging
import os
import pickle
import time as _time
import urllib.error
import urllib.request
from typing import Dict, List, Optional

from src.research import Paper

logger = logging.getLogger(__name__)

S2_BASE = "https://api.semanticscholar.org/graph/v1"
_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "upgrades", "s2_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

# Fields to request by default
_DEFAULT_FIELDS = "title,authors,year,citationCount,influentialCitationCount,externalIds,abstract,url"


def _cached_fetch(url: str, cache_seconds: int = 3600) -> Optional[bytes]:
    """Fetch URL with local file cache."""
    key = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(_CACHE_DIR, key + ".pkl")
    if os.path.exists(cache_file):
        age = _time.time() - os.path.getmtime(cache_file)
        if age < cache_seconds:
            with open(cache_file, "rb") as f:
                return pickle.load(f)

    req = urllib.request.Request(url, headers={"User-Agent": "SelfUpgradeAgent/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                wait = 2 ** attempt
                logger.debug(f"S2 rate limited, waiting {wait}s...")
                _time.sleep(wait)
                continue
            if e.code == 404:
                return None
            logger.warning(f"S2 HTTP {e.code}: {url[:80]}")
            return None
        except Exception as e:
            if attempt < 4:
                _time.sleep(1)
                continue
            logger.warning(f"S2 fetch failed: {e}")
            return None
    return None


def search_papers(keywords: List[str], max_results: int = 10) -> List[dict]:
    """Search Semantic Scholar for papers matching keywords.

    Returns list of dicts with keys: paperId, title, year, citationCount,
    influentialCitationCount, externalIds (includes ArXiv), abstract, url.
    """
    query = " ".join(keywords[:5])
    if not query.strip():
        return []

    params = (
        f"query={urllib.parse.quote(query)}"
        f"&limit={max_results}"
        f"&fields={_DEFAULT_FIELDS}"
    )
    url = f"{S2_BASE}/paper/search?{params}"

    data = _cached_fetch(url)
    if not data:
        return []

    try:
        result = json.loads(data)
        return result.get("data", [])
    except json.JSONDecodeError as e:
        logger.warning(f"S2 JSON parse error: {e}")
        return []


def enrich_by_arxiv_id(arxiv_id: str) -> Optional[dict]:
    """Fetch paper metadata and citation counts by arXiv ID.

    Returns dict or None if not found.
    """
    clean_id = arxiv_id.split("v")[0].strip()
    url = f"{S2_BASE}/paper/ArXiv:{clean_id}?fields={_DEFAULT_FIELDS}"

    data = _cached_fetch(url)
    if not data:
        return None

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def enrich_paper(arxiv_id: str) -> dict:
    """Get citation data for an arXiv paper. Returns dict with keys
    citation_count, influential_citation_count, s2_paper_id, year.

    Never fails — returns zeros on error.
    """
    info = enrich_by_arxiv_id(arxiv_id)
    if not info:
        return {
            "citation_count": 0,
            "influential_citation_count": 0,
            "s2_paper_id": "",
            "year": 0,
        }

    return {
        "citation_count": info.get("citationCount", 0) or 0,
        "influential_citation_count": info.get("influentialCitationCount", 0) or 0,
        "s2_paper_id": info.get("paperId", ""),
        "year": info.get("year", 0) or 0,
    }


def get_citations(paper_id: str, limit: int = 10) -> List[dict]:
    """Get papers that cite the given paper (forward citation chain).

    Returns list of dicts with: title, citationCount, year, paperId.
    """
    url = (
        f"{S2_BASE}/paper/{paper_id}/citations"
        f"?fields=title,citationCount,year&limit={limit}"
    )
    data = _cached_fetch(url)
    if not data:
        return []

    try:
        result = json.loads(data)
        return [c.get("citingPaper", {}) for c in result.get("data", [])]
    except json.JSONDecodeError:
        return []


def get_references(paper_id: str, limit: int = 10) -> List[dict]:
    """Get papers that the given paper cites (backward citation chain).

    Returns list of dicts with: title, citationCount, year, paperId.
    """
    url = (
        f"{S2_BASE}/paper/{paper_id}/references"
        f"?fields=title,citationCount,year&limit={limit}"
    )
    data = _cached_fetch(url)
    if not data:
        return []

    try:
        result = json.loads(data)
        return [c.get("citedPaper", {}) for c in result.get("data", [])]
    except json.JSONDecodeError:
        return []


def citation_score(citation_count: int) -> float:
    """Map citation count to a 0-10 score using log scale.

    1 citation → 2.5, 10 → 5.0, 100 → 7.5, 1000 → 10.0
    """
    import math
    if citation_count <= 0:
        return 0.0
    return min(10.0, math.log10(citation_count + 1) * 3.0)
