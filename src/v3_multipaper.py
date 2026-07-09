"""src/v3_multipaper.py - multi-paper reader.

Per user feedback 2026-07-08: 'multi-paper reading,
generate ideas/views/plans then let LLM judge'.

This module reads N papers and produces structured summaries.
Each summary contains:
  - paper_arxiv_id
  - title
  - idea (1-line innovation)
  - viewpoint (1-line perspective on our design)
  - plan (1-line action item)

The summarization is currently **deterministic** (extracts from a
structured catalog in LITERATURE_DETAIL.md).  In v3.0.2, this
will call an LLM-as-judge to *select* the best plan from the N
summaries.

Why start deterministic?
  - v3.0 must work *without* a working LLM round-trip (per P17
    honest reporting: don't claim green when yellow).
  - The catalog in LITERATURE_DETAIL.md is hand-curated; an LLM
    would just rephrase it.
  - The next commit (v3.0.2) adds LLM-as-judge on top.

Public API:
  read_papers() -> List[PaperSummary]
  read_papers(ids=[...]) -> List[PaperSummary]
  parse_literature_catalog(path) -> List[PaperSummary]
"""
import os
import re
from dataclasses import dataclass, asdict
from typing import List, Optional


# Default catalog location (per P11: project knowledge, not memory)
DEFAULT_CATALOG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "LITERATURE_DETAIL.md",
)


@dataclass
class PaperSummary:
    """Structured summary of one paper from the catalog."""
    paper_arxiv_id: str
    title: str
    idea: str           # 1-line innovation (the paper's main contribution)
    viewpoint: str      # 1-line perspective (how we use / don't use it)
    plan: str           # 1-line action item (concrete next step for v3)
    section: str = ""   # original markdown section heading

    def to_dict(self):
        return asdict(self)


@dataclass
class CatalogParseError(Exception):
    """Raised when the catalog cannot be parsed."""
    path: str
    reason: str


# ── Parsing ──────────────────────────────────────────────────────

_RE_SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_RE_TLDR = re.compile(r"\*\*TL;DR\*\*\s*:\s*(.+?)(?=\n\*\*|\n##|\Z)",
                      re.DOTALL)
# Why field: matches "Why we use it", "Why we DON'T use it",
# "Why we DON'T use it directly", etc.
# Note: [^*]* between the keyword and the closing ** lets us
# match text like "Why we DON'T use it directly**".
# Without this, non-greedy .*? finds the FIRST 'use' (which
# isn't followed by **) and gives up instead of expanding.
_RE_USE = re.compile(
    r"\*\*(Why.*?(?:use|don[\u0027\u2019]t use)|Use it for)[^*]*\*\*"
    r"\s*:?\s*(.+?)(?=\n\*\*|\n##|\Z)",
    re.DOTALL,
)


def parse_literature_catalog(path: str = DEFAULT_CATALOG) -> List[PaperSummary]:
    """Parse the LITERATURE_DETAIL.md catalog into PaperSummary list.

    Each ## heading becomes one PaperSummary.  arxiv_id is inferred
    from the title line or set to a placeholder if no DOI/arxiv is
    present.

    Raises CatalogParseError if the file is missing or unreadable.
    """
    if not os.path.isfile(path):
        raise CatalogParseError(path, "file not found")
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise CatalogParseError(path, f"read failed: {e}")

    summaries: List[PaperSummary] = []
    # Split by ## headings
    sections = _RE_SECTION.split(content)
    # _RE_SECTION.split alternates: text, heading, text, heading, ...
    # sections[0] is content before the first heading (skipped).
    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        body = sections[i + 1] if i + 1 < len(sections) else ""

        # Extract TL;DR
        tldr_match = _RE_TLDR.search(body)
        if not tldr_match:
            # Skip sections without a TL;DR (probably meta sections)
            continue
        tldr = " ".join(tldr_match.group(1).split())

        # Extract "Why we use / don't use" + "Use it for"
        viewpoint = ""
        plan = ""
        for m in _RE_USE.finditer(body):
            key, value = m.group(1), m.group(2)
            value = " ".join(value.split())
            if key.startswith("Why"):
                viewpoint = value
            elif key.startswith("Use"):
                plan = value

        # Infer arxiv_id from heading
        arxiv_id = _infer_arxiv_id(heading)

        # Use first sentence of TL;DR as the 'idea'
        idea = tldr.split(".")[0] + "."

        summaries.append(PaperSummary(
            paper_arxiv_id=arxiv_id,
            title=heading,
            idea=idea,
            viewpoint=viewpoint,
            plan=plan,
            section=heading,
        ))

    return summaries


def _infer_arxiv_id(heading: str) -> str:
    """Infer an arxiv_id from a section heading.  Falls back to
    a slug of the title.
    """
    # Remove everything after first '(' or '—' or ','
    base = re.split(r"[(\u2014,]", heading, 1)[0].strip()
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    return slug or "unknown"


# ── Public API ───────────────────────────────────────────────────

def read_papers(
    ids: Optional[List[str]] = None,
    catalog_path: str = DEFAULT_CATALOG,
) -> List[PaperSummary]:
    """Read N papers from the catalog and return structured summaries.

    Args:
      ids: optional list of arxiv_ids to filter.  If None, returns
        all papers in the catalog.
      catalog_path: path to LITERATURE_DETAIL.md (default: project docs).

    Returns:
      List[PaperSummary], one per matching paper.

    Raises:
      CatalogParseError if the catalog is missing or unreadable.
    """
    all_summaries = parse_literature_catalog(catalog_path)
    if ids is None:
        return all_summaries
    id_set = set(ids)
    return [s for s in all_summaries if s.paper_arxiv_id in id_set]


def paper_count(catalog_path: str = DEFAULT_CATALOG) -> int:
    """Return the number of papers in the catalog."""
    return len(read_papers(catalog_path=catalog_path))