"""Filter papers by scoring their applicability to agent skill upgrades.

Supports two modes:
- Keyword scoring (fast, deterministic, no API cost) — default
- LLM scoring (more accurate, uses ModelScope/Qwen) — configurable
"""
import json
import logging
import re
from dataclasses import dataclass
from typing import List, Optional
from src.research import Paper
from src.config import FilterConfig
from src.llm import chat_simple, LLMConfig

logger = logging.getLogger(__name__)

# LLM JSON responses are frequently wrapped in markdown fences (```json ... ```)
# or have leading prose ("Here is the JSON: {...}").  We try a sequence of
# increasingly tolerant parse strategies.
def _parse_llm_json(content: str) -> dict:
    """Robustly extract a JSON object from an LLM response.

    Tries, in order:
      1. Direct json.loads on the whole string.
      2. Strip ```json / ``` fences, parse the inside.
      3. Find the first {...} block, parse it.

    Returns {} on any failure.
    """
    if not content:
        return {}
    content = content.strip()

    # 1) Direct parse.
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # 2) Strip ```json / ``` fences (possibly with leading "json" hint).
    fenced = re.sub(
        r"^\s*```(?:json)?\s*|\s*```\s*$",
        "",
        content,
        flags=re.IGNORECASE | re.MULTILINE,
    ).strip()
    if fenced and fenced != content:
        try:
            return json.loads(fenced)
        except json.JSONDecodeError:
            pass

    # 3) First balanced {...} block.  We don't do full brace-matching — that
    #    is overkill for a 3-field response.  A non-greedy regex covers 99%
    #    of LLM outputs.
    m = re.search(r"\{[^{}]*\}", content, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    return {}


# Keyword dictionaries for fallback scoring
_ABSTRACT_QUALITY = [
    "state-of-the-art", "sota", "improves", "outperforms",
    "benchmark", "evaluation", "experiment", "ablation", "significant",
]
_APPLICABILITY = [
    "agent", "framework", "skill", "prompt", "tool use",
    "coordination", "reasoning", "planning", "self-improve",
    "multi-agent", "delegation", "orchestration", "memory", "context",
]
_NOVELTY = [
    "first", "novel", "new method", "innovative", "unprecedented",
    "pioneering", "breakthrough", "for the first time",
]


@dataclass
class ScoredPaper:
    paper: Paper
    abstract_score: float
    applicability_score: float
    novelty_score: float
    citation_score: float = 0.0

    @property
    def total_score(self) -> float:
        return round(
            self.applicability_score * 0.40 +
            self.novelty_score * 0.25 +
            self.abstract_score * 0.15 +
            self.citation_score * 0.20,
            2,
        )

    def meets_thresholds(self, config: FilterConfig) -> bool:
        return (self.abstract_score >= config.min_abstract_score and
                self.applicability_score >= config.min_applicability_score and
                self.novelty_score >= config.min_novelty_score)


def _keyword_score(text: str, terms: List[str]) -> float:
    """Score text (0-10) by keyword term density."""
    text_lower = text.lower()
    matches = sum(1 for term in terms if term in text_lower)
    if not terms:
        return 0.0
    return min(10.0, (matches / len(terms)) * 20.0)


def _keyword_score_paper(paper: Paper) -> ScoredPaper:
    """Keyword-only scoring (fallback)."""
    text = paper.title + " " + paper.abstract
    words = len(text.split())
    length_bonus = min(8.0, (words / 200) * 8.0) if words > 0 else 0.0
    kw = _keyword_score(text, _ABSTRACT_QUALITY)
    abstract_score = min(10.0, kw * 0.4 + length_bonus * 0.6)
    return ScoredPaper(
        paper=paper,
        abstract_score=round(abstract_score, 2),
        applicability_score=round(_keyword_score(text, _APPLICABILITY), 2),
        novelty_score=round(_keyword_score(text, _NOVELTY), 2),
    )


def _llm_score_paper(paper: Paper, llm_config: Optional[LLMConfig] = None) -> ScoredPaper:
    """LLM-based scoring — more accurate for method/trend detection."""
    prompt = (
        f"Rate this AI/ML paper on three dimensions (1-10).\n\n"
        f"TITLE: {paper.title}\n"
        f"ABSTRACT: {paper.abstract[:800]}\n\n"
        'Respond ONLY with valid JSON, no other text:\n'
        '{"abstract_quality": 1-10, "applicability_to_agents": 1-10, "novelty": 1-10}'
    )
    system = (
        "You are an AI research evaluator. A paper with high 'applicability_to_agents' "
        "presents methods directly useful for improving LLM-based agent systems "
        "(prompting, tool use, planning, memory, reasoning, etc.). Be strict in scoring."
    )

    content = chat_simple(prompt, system=system, config=llm_config)
    data = _parse_llm_json(content)
    if not data:
        logger.warning(f"LLM returned invalid JSON: {str(content)[:100]}")

    def _safe(s, default=5.0):
        try: return max(0.0, min(10.0, float(s)))
        except: return default
    return ScoredPaper(
        paper=paper,
        abstract_score=_safe(data.get("abstract_quality", 5)),
        applicability_score=_safe(data.get("applicability_to_agents", 3)),
        novelty_score=_safe(data.get("novelty", 3)),
    )


def score_paper(
    paper: Paper,
    config: FilterConfig,
    use_llm: bool = False,
    llm_config: Optional[LLMConfig] = None,
) -> ScoredPaper:
    """Score a single paper. Falls back to keyword scoring if LLM fails."""
    if use_llm:
        try:
            return _llm_score_paper(paper, llm_config)
        except Exception as e:
            logger.warning(f"LLM scoring failed, falling back to keyword: {e}")
    return _keyword_score_paper(paper)


def filter_papers(
    papers: List[Paper],
    config: FilterConfig,
    use_llm: bool = False,
    llm_config: Optional[LLMConfig] = None,
    enrich_citations: bool = True,
) -> List[ScoredPaper]:
    """Score all papers, enrich with citation data, filter by thresholds.

    When enrich_citations=True, calls Semantic Scholar to get real citation
    counts (adds ~1-2s per paper due to API calls).
    """
    scored = []

    for p in papers:
        sp = score_paper(p, config, use_llm=use_llm, llm_config=llm_config)

        # Enrich with real citation data from Semantic Scholar
        if enrich_citations and sp.meets_thresholds(config):
            try:
                from src.research_s2 import enrich_paper, citation_score
                s2_data = enrich_paper(p.arxiv_id)
                sp.citation_score = citation_score(s2_data.get("citation_count", 0))
                p.citation_count = s2_data.get("citation_count", 0)
            except Exception:
                pass  # S2 unavailable — keep citation_score=0

        scored.append(sp)

    qualified = [s for s in scored if s.meets_thresholds(config)]
    qualified.sort(key=lambda s: s.total_score, reverse=True)
    return qualified[:config.max_papers_to_consider]
