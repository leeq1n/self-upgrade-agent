"""Research module: search arXiv for latest papers on agent-related topics.

[FROZEN v1.1.0] — stable API, tested, do not modify.
"""
import urllib.request
import urllib.parse
import urllib.error
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Dict

logger = __import__("logging").getLogger(__name__)

NS = {'a': 'http://www.w3.org/2005/Atom'}


@dataclass
class Paper:
    """Standardized paper data structure used across all modules."""
    arxiv_id: str
    title: str
    authors: str
    published: str
    abstract: str
    categories: str
    citation_count: int = 0


def _arxiv_keyword(kw: str) -> str:
    """Convert a keyword phrase to arXiv query syntax (spaces become +)."""
    return kw.strip().replace(' ', '+')


def build_query_string(config) -> str:
    """Build arXiv API query from a ResearchConfig.

    arXiv query syntax uses + for space and +OR+ / +AND+ for operators.
    This is NOT standard URL encoding — arXiv has its own query DSL.
    Example: all:transformer+attention+AND+cat:cs.AI
    """
    if not config.keywords:
        return ""

    kw_parts = [f"all:{_arxiv_keyword(kw)}" for kw in config.keywords]
    cat_parts = [f"cat:{c}" for c in config.categories]

    kw_clause = "+OR+".join(kw_parts)
    cat_clause = "+OR+".join(cat_parts)

    return f"({kw_clause})+AND+({cat_clause})"


def _parse_arxiv_entry(entry) -> Paper:
    """Parse a single Atom entry from arXiv API into a Paper."""
    title_el = entry.find('a:title', NS)
    title = title_el.text.strip().replace('\n', ' ') if title_el is not None else "Untitled"

    raw_id = entry.find('a:id', NS).text.strip() if entry.find('a:id', NS) is not None else ""
    full_id = raw_id.split('/abs/')[-1] if '/abs/' in raw_id else raw_id
    arxiv_id = full_id.split('v')[0]

    published_el = entry.find('a:published', NS)
    published = published_el.text[:10] if published_el is not None else "unknown"

    authors = ', '.join(
        a.find('a:name', NS).text
        for a in entry.findall('a:author', NS)
        if a.find('a:name', NS) is not None
    )

    summary_el = entry.find('a:summary', NS)
    summary = summary_el.text.strip().replace('\n', ' ') if summary_el is not None else ""

    cats = ', '.join(
        c.get('term', 'unknown')
        for c in entry.findall('a:category', NS)
    )

    return Paper(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        published=published,
        abstract=summary,
        categories=cats,
    )


def _is_withdrawn(entry) -> bool:
    """Check if a paper entry has been withdrawn."""
    summary_el = entry.find('a:summary', NS)
    if summary_el is None:
        return False
    summary = summary_el.text.strip().lower()
    return "withdrawn" in summary or "retracted" in summary


import hashlib, os, pickle, time as _time
_CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'upgrades', 'arxiv_cache')
os.makedirs(_CACHE_DIR, exist_ok=True)

def _cached_fetch(url, cache_seconds=3600):
    """Fetch URL with local file cache to avoid repeated API calls."""
    key = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(_CACHE_DIR, key + '.pkl')
    if os.path.exists(cache_file):
        age = _time.time() - os.path.getmtime(cache_file)
        if age < cache_seconds:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    req = urllib.request.Request(url, headers={'User-Agent': 'SelfUpgradeAgent/1.0'})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                wait = 2 ** attempt
                _time.sleep(wait)
                continue
            raise
    raise RuntimeError('arXiv API exhausted after 5 retries')

def search_arxiv(config) -> List[Paper]:
    """Search arXiv for papers matching configured keywords and categories.

    Strategy (v1.8.1): src/web.py (HTML scrape, no API, no rate limits).
    Old strategy was Selenium -> arxiv API, but API was unreliable
    (0-byte responses) and Selenium needed Chrome setup.

    Uses src/web.py.arxiv_listing for the recent-paper index and
    src/web.py.arxiv_paper for full abstract + authors.
    """
    from src.web import arxiv_listing, arxiv_paper, _cache_get

    # Support both: full Config (config.research.X) and flat ResearchConfig (config.X)
    cfg_obj = getattr(config, "research", config)
    keywords = [k.lower() for k in (cfg_obj.keywords or [])]
    # Empty keywords means "no search intent" — preserve old behavior (return []).
    if not keywords:
        return []
    categories = cfg_obj.categories or ["cs.AI", "cs.CL"]
    max_papers = cfg_obj.max_papers_per_query

    # Pull recent papers from each configured category (default cs.AI).
    listings: List[Dict] = []
    for cat in categories:
        try:
            cat_listings = arxiv_listing(cat, limit=max_papers)
            listings.extend(cat_listings)
        except Exception as e:
            logger.debug(f"arxiv_listing({cat}) failed: {e}")

    if not listings:
        return []

    # Dedupe arxiv_ids (different categories may overlap).
    seen_ids: set = set()
    unique: List[Dict] = []
    for entry in listings:
        if entry["arxiv_id"] in seen_ids:
            continue
        seen_ids.add(entry["arxiv_id"])
        unique.append(entry)
    listings = unique[:max_papers]

    # Filter by keywords if specified.
    if keywords:
        def matches(paper_meta: Dict) -> bool:
            aid = paper_meta["arxiv_id"]
            try:
                full = arxiv_paper(aid)
            except Exception as e:
                logger.debug(f"arxiv_paper({aid}) failed: {e}")
                return False
            text = (full.get("title", "") + " " + full.get("abstract", "")).lower()
            return any(kw in text for kw in keywords)

        listings = [p for p in listings if matches(p)]

    # Fetch full details and convert to Paper dataclass.
    papers: List[Paper] = []
    for entry in listings:
        try:
            full = arxiv_paper(entry["arxiv_id"])
        except Exception as e:
            logger.debug(f"arxiv_paper({entry['arxiv_id']}) failed: {e}")
            continue
        cats = full.get("categories") or []
        primary = full.get("primary_category", "cs.AI")
        # Strip the human-readable part "Computation and Language (cs.CL)" -> "cs.CL"
        primary_code = primary.split("(")[-1].rstrip(")").strip() if "(" in primary else primary
        papers.append(Paper(
            arxiv_id=full.get("arxiv_id", entry["arxiv_id"]),
            title=full.get("title", ""),
            authors=", ".join(full.get("authors", [])),
            published=full.get("submitted", ""),
            abstract=full.get("abstract", ""),
            categories=primary_code or "cs.AI",
        ))

    return papers


def search_all_sources(config) -> List[Paper]:
    """Search all available sources and aggregate results with deduplication.

    Sources: arXiv (primary), Semantic Scholar (citation data), Papers With Code
    (trending), GitHub (trending repos with related code).

    All sources fail gracefully — if one is unavailable, the rest still contribute.

    Args:
        config: ResearchConfig with keywords and categories.

    Returns:
        Deduplicated list of Paper objects from all available sources.
    """
    papers = []

    # ── Source 1: arXiv (primary) ──
    try:
        arxiv_papers = search_arxiv(config)
        papers.extend(arxiv_papers)
        logger.info(f"arXiv: {len(arxiv_papers)} papers")
    except Exception as e:
        logger.warning(f"arXiv search failed: {e}")

    # ── Source 2: Semantic Scholar enrichment ──
    try:
        from src.research_s2 import enrich_papers
        enrich_papers(papers)
    except Exception as e:
        logger.debug(f"S2 enrichment skipped: {e}")

    # ── Source 3: Papers With Code trending ──
    try:
        from src.research_pwc import fetch_trending_papers
        pwc_papers = fetch_trending_papers(max_results=5)
        for p in pwc_papers:
            if p.get("arxiv_id") and p.get("title"):
                # Avoid duplicates by arXiv ID
                if not any(pp.arxiv_id == p["arxiv_id"] for pp in papers):
                    papers.append(Paper(
                        arxiv_id=p["arxiv_id"],
                        title=p["title"],
                        authors="",
                        published="",
                        abstract=p.get("abstract", ""),
                        categories="",
                    ))
        logger.info(f"PwC: {len(pwc_papers)} trending papers")
    except Exception as e:
        logger.debug(f"PwC trending skipped: {e}")

    # ── Source 4: GitHub trending ──
    try:
        from src.research_github import search_trending_weekly
        gh_repos = search_trending_weekly(language="python")
        gh_count = 0
        for repo in gh_repos:
            desc = repo.get("description", "")
            name = repo.get("name", "")
            if desc and len(desc) > 20:
                # Convert GitHub repos to Paper-like entries with a synthetic ID
                import hashlib
                gh_id = "gh-" + hashlib.md5(name.encode()).hexdigest()[:8]
                if not any(pp.arxiv_id == gh_id for pp in papers):
                    papers.append(Paper(
                        arxiv_id=gh_id,
                        title=f"[GitHub] {name}: {desc[:80]}",
                        authors="",
                        published="",
                        abstract=desc,
                        categories="",
                    ))
                    gh_count += 1
        logger.info(f"GitHub trending: {gh_count} relevant repos")
    except Exception as e:
        logger.debug(f"GitHub trending skipped: {e}")

    return papers
