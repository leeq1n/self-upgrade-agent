"""Filter papers by scoring their applicability to agent skill upgrades.

Supports two modes:
- Keyword scoring (fast, deterministic, no API cost) — default
- LLM scoring (more accurate, uses ModelScope/Qwen) — configurable
"""
import json
import logging
from dataclasses import dataclass
from typing import List, Optional
from src.research import Paper
from src.config import FilterConfig
from src.llm import chat_simple, LLMConfig

logger = logging.getLogger(__name__)

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

    @property
    def total_score(self) -> float:
        return round(
            self.applicability_score * 0.5 +
            self.novelty_score * 0.3 +
            self.abstract_score * 0.2,
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
    try:
        data = json.loads(content) if content else {}
    except json.JSONDecodeError:
        logger.warning(f"LLM returned invalid JSON: {str(content)[:100]}")
        data = {}

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
) -> List[ScoredPaper]:
    """Score all papers, filter by thresholds, return top candidates."""
    scored = [
        score_paper(p, config, use_llm=use_llm, llm_config=llm_config)
        for p in papers
    ]
    qualified = [s for s in scored if s.meets_thresholds(config)]
    qualified.sort(key=lambda s: s.total_score, reverse=True)
    return qualified[:config.max_papers_to_consider]
