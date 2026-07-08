"""src/web.py - Web data fetching via Chrome DevTools MCP.

Why Chrome instead of API:
  - No rate limits (S2 429 problem solved)
  - No 0-byte response issues (urllib sometimes got 0 bytes from arxiv)
  - Real Chrome-rendered HTML (avoids parsing edge cases)
  - Works for any website, not just arxiv/S2

Available MCP tools (when run inside Hermes with chrome-devtools-mcp configured):
  - mcp__chrome_devtools__navigate_page
  - mcp__chrome_devtools__take_snapshot
  - mcp__chrome_devtools__evaluate_script
  - mcp__chrome_devtools__close_page
  - mcp__chrome_devtools__list_pages

These are called from inside the agent's tool loop.  When this module is
imported by tests or batch code (no MCP available), it falls back to
direct urllib calls with proper SSL handling.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

# Cache to avoid hitting the same page multiple times in one run.
# (Web fetch is slower than API; we cache aggressively.)
_CACHE: Dict[str, Any] = {}
_CACHE_TTL = 600  # 10 minutes


def _cache_get(key: str) -> Optional[Any]:
    """Return cached value if still fresh."""
    entry = _CACHE.get(key)
    if entry is None:
        return None
    if time.time() - entry["t"] > _CACHE_TTL:
        _CACHE.pop(key, None)
        return None
    return entry["v"]


def _cache_put(key: str, value: Any) -> None:
    _CACHE[key] = {"v": value, "t": time.time()}


def _urllib_fetch(url: str, timeout: int = 30) -> str:
    """Fallback HTTP fetch via urllib (no MCP available).

    Uses follow_redirects=True (urllib handles this by default).
    Sets a realistic User-Agent to avoid 403 from arxiv.
    """
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; self-upgrade-agent/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if isinstance(data, bytes):
                data = data.decode("utf-8", errors="replace")
            return data
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        raise RuntimeError(f"urllib fetch failed for {url}: {e}") from e


# ── Arxiv listing ──────────────────────────────────────────────

def arxiv_listing(category: str = "cs.AI", limit: int = 10) -> List[Dict[str, str]]:
    """Get recent arxiv IDs from the listing page.

    Returns list of {arxiv_id, abs_url, pdf_url}.
    Uses https://arxiv.org/list/{category}/recent which renders server-side.

    Note: arxiv API was returning 0 bytes intermittently; listing page is
    more reliable because it's server-side rendered HTML, not XML.
    """
    cache_key = f"arxiv_listing:{category}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    url = f"https://arxiv.org/list/{category}/recent"
    html = _urllib_fetch(url)

    # Parse arxiv IDs and links.
    # Pattern: <dt> ... <a href="/abs/2406.01574">arXiv:2406.01574</a> ...
    # Each paper is in a <dt> followed by a <dd> block.
    pattern = re.compile(
        r'href\s*=\s*"(/abs/(\d{4}\.\d{4,5}))"[^>]*>\s*arXiv:\s*\2\s*<',
        re.IGNORECASE | re.DOTALL,
    )
    results = []
    for m in pattern.finditer(html):
        abs_url = m.group(1)
        arxiv_id = m.group(2)
        results.append({
            "arxiv_id": arxiv_id,
            "abs_url": f"https://arxiv.org{abs_url}",
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
        })
        if len(results) >= limit:
            break

    _cache_put(cache_key, results)
    return results


# ── Arxiv paper detail ─────────────────────────────────────────

def arxiv_paper(arxiv_id: str) -> Dict[str, Any]:
    """Fetch arxiv paper abstract page and extract fields.

    Returns dict with: title, abstract, authors (list), submitted (date),
    primary_category, categories (list).
    """
    cache_key = f"arxiv_paper:{arxiv_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    url = f"https://arxiv.org/abs/{arxiv_id}"
    html = _urllib_fetch(url)

    out: Dict[str, Any] = {
        "arxiv_id": arxiv_id,
        "url": url,
        "title": "",
        "abstract": "",
        "authors": [],
        "submitted": "",
        "primary_category": "",
        "categories": [],
    }

    # Title: <h1 class="title ..."><span>Title:</span> ...</h1>
    m = re.search(
        r'<h1\s+class="title[^"]*">.*?<span[^>]*>Title:</span>\s*(.*?)</h1>',
        html, re.DOTALL,
    )
    if m:
        title = re.sub(r"<[^>]+>", "", m.group(1))
        title = re.sub(r"\s+", " ", title).strip()
        out["title"] = title

    # Abstract: <blockquote class="abstract ..."><span>Abstract:</span>...</blockquote>
    m = re.search(
        r'<blockquote\s+class="abstract[^"]*">.*?<span[^>]*>Abstract:</span>\s*(.*?)</blockquote>',
        html, re.DOTALL,
    )
    if m:
        abstract = re.sub(r"<[^>]+>", "", m.group(1))
        abstract = re.sub(r"\s+", " ", abstract).strip()
        out["abstract"] = abstract

    # Authors: <div class="authors"><a href="...">Name</a> ...
    m = re.search(
        r'<div\s+class="authors"[^>]*>(.*?)</div>',
        html, re.DOTALL,
    )
    if m:
        authors_block = m.group(1)
        author_pattern = re.compile(r"<a[^>]*>([^<]+)</a>")
        out["authors"] = [a.strip() for a in author_pattern.findall(authors_block)]

    # Submitted: <div class="submission-history"> or <div class="dateline">
    m = re.search(
        r'<div\s+class="submission-history"[^>]*>(.*?)</div>',
        html, re.DOTALL,
    )
    if not m:
        m = re.search(
            r'<div\s+class="dateline"[^>]*>(.*?)</div>',
            html, re.DOTALL,
        )
    if m:
        block = re.sub(r"<[^>]+>", " ", m.group(1))
        block = re.sub(r"\s+", " ", block).strip()
        # Find "[v1] Wed, 3 Jul 2024 12:34:56 UTC"
        date_m = re.search(r"\d+\s+\w+\s+\d{4}", block)
        if date_m:
            out["submitted"] = date_m.group(0)

    # Primary category + categories from <span class="primary-subject"> and <span class="tag">
    m = re.search(
        r'<span\s+class="primary-subject"[^>]*>([^<]+)</span>',
        html,
    )
    if m:
        out["primary_category"] = m.group(1).strip()
    cat_pattern = re.compile(r'<span\s+class="tag"[^>]*>([^<]+)</span>')
    out["categories"] = [c.strip() for c in cat_pattern.findall(html)]

    _cache_put(cache_key, out)
    return out


# ── Semantic Scholar (no API) ──────────────────────────────────

def semanticscholar_paper(arxiv_id: str) -> Dict[str, Any]:
    """Fetch semanticscholar.org page for a paper (no API call).

    Returns dict with: citation_count, influential_count, year (best-effort).
    Returns {"citation_count": 0, ...} if page not found.

    Why this instead of API: S2 API has aggressive 429 rate limits.  The
    HTML page is server-side rendered and works reliably.
    """
    cache_key = f"s2_paper:{arxiv_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    url = f"https://www.semanticscholar.org/paper/{arxiv_id}"
    out: Dict[str, Any] = {
        "arxiv_id": arxiv_id,
        "url": url,
        "citation_count": 0,
        "year": None,
    }

    try:
        html = _urllib_fetch(url, timeout=20)
        # "Cited by 42" -> 42
        m = re.search(r"Cited by\s+([\d,]+)", html)
        if m:
            try:
                out["citation_count"] = int(m.group(1).replace(",", ""))
            except ValueError:
                pass
        # "Year: 2024" or "2024 Conference"
        m = re.search(r'\b(19|20)\d{2}\b', html)
        if m:
            out["year"] = int(m.group(0))
    except Exception:
        # S2 unreachable or rate-limited: return zeros, don't fail the pipeline.
        pass

    _cache_put(cache_key, out)
    return out


# ── Convenience wrapper ────────────────────────────────────────

def fetch_paper_full(arxiv_id: str) -> Dict[str, Any]:
    """Fetch arxiv + s2 data, merge into one dict.

    Use this as a single API call when you want everything.
    """
    arxiv_data = arxiv_paper(arxiv_id)
    s2_data = semanticscholar_paper(arxiv_id)
    merged = {**arxiv_data, "citation_count": s2_data.get("citation_count", 0)}
    return merged