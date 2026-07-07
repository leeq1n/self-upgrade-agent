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
    """LLM-based scoring — tailored to this project's actual upgrade targets.

    v1.5.0: rewrote the prompt to be specific to the self-upgrade agent
    pipeline.  Earlier versions asked "is this paper useful for any
    agent?" which surfaced too many papers that improve some other kind
    of agent but don't help *this* system.  The new prompt asks the
    LLM to evaluate applicability against the 5 concrete pain points
    of this codebase (paper search, code generation, sandbox,
    A/B evaluation, bootloader), so high scores correlate with
    actually useful upgrades.
    """
    prompt = (
        "You are selecting which research papers this self-upgrade agent\n"
        "should try to turn into code patches.  Score the paper on 3 axes (1-10):\n\n"
        "  applicability_to_agent_pipeline: how well the paper's method\n"
        "    could improve one of these 5 specific pain points in this\n"
        "    project: (a) multi-source paper search & filtering, (b) LLM\n"
        "    code-patch generation, (c) sandbox validation of generated\n"
        "    code, (d) A/B benchmark evaluation of a candidate patch\n"
        "    against the current code, (e) bootloader / atomic rollout\n"
        "    of the new module.  A paper that improves *any* of those is\n"
        "    high applicability; a paper about, say, RL for game-playing\n"
        "    is low.\n\n"
        "  novelty: how novel / state-of-the-art is the method?  1 is a\n"
        "    textbook re-statement, 10 is a fresh paradigm.\n\n"
        "  abstract_quality: how well-written and reproducible is the\n"
        "    paper?  1 is unclear, 10 has code + numbers.\n\n"
        f"Paper title: {paper.title}\n"
        f"Paper abstract: {paper.abstract[:800]}\n\n"
        "Reply with ONLY raw JSON, no markdown fences:\n"
        '{"applicability_to_agent_pipeline": 1-10, "novelty": 1-10, "abstract_quality": 1-10}'
    )
    system = (
        "You are a strict research evaluator.  High applicability scores "
        "should be reserved for papers whose method can be turned into a "
        "concrete code improvement for this self-upgrade agent pipeline. "
        "Do not give high scores just because the paper is famous."
    )

    # v1.8.1: filter is keyword-based scoring; no deep reasoning needed.
    # Disable thinking for speed.
    content = chat_simple(prompt, system=system, config=llm_config,
                          enable_thinking=False)
    data = _parse_llm_json(content)
    if not data:
        logger.warning(f"LLM returned invalid JSON: {str(content)[:100]}")

    def _safe(s, default=5.0):
        try: return max(0.0, min(10.0, float(s)))
        except: return default
    return ScoredPaper(
        paper=paper,
        # The old field names (abstract_score, applicability_score,
        # novelty_score) are kept for backward compatibility with
        # ScoredPaper and decide.py.  We re-map the new dimensions
        # onto the existing slots.
        abstract_score=_safe(data.get("abstract_quality", 5)),
        applicability_score=_safe(data.get("applicability_to_agent_pipeline", 3)),
        novelty_score=_safe(data.get("novelty", 3)),
    )


def score_paper(
    paper: Paper,
    config: FilterConfig,
    use_llm: bool = False,
    llm_config: Optional[LLMConfig] = None,
) -> ScoredPaper:
    """Score a single paper.

    If ``use_llm`` is True and the LLM is configured AND has at least
    one alive (not quota-dead) key, use LLM scoring.  Otherwise fall
    back to keyword scoring.  The "alive key" check matters because
    LLM scoring against all-dead keys burns timeouts (5-15s per
    paper) without any chance of success.
    """
    if use_llm and llm_config is not None and llm_config.ready:
        # Quick check: are there alive keys?  Avoid burning 15s per paper
        # if all keys are quota-dead.  v1.8.1: if no API keys (local
        # llama-server), skip the quota check and use LLM directly.
        if llm_config.api_keys:
            try:
                from src.llm import QuotaState
                quota = QuotaState()
                alive_keys = [k for k in llm_config.api_keys if not quota.is_dead(k)]
                if not alive_keys:
                    logger.debug(f"All keys quota-dead, falling back to keyword for {paper.arxiv_id}")
                    return _keyword_score_paper(paper)
            except Exception:
                pass
        try:
            return _llm_score_paper(paper, llm_config)
        except Exception as e:
            logger.warning(f"LLM scoring failed, falling back to keyword: {e}")
    return _keyword_score_paper(paper)


# Deterministic boost for self-upgrade-specific keywords.  LLM scoring
# alone is unstable (same paper may rank 1st or 4th on different runs);
# these patterns match the exact pain points the agent is trying to
# improve, so a hit here is meaningful.  Each hit adds +1 to
# applicability_score, capped at +3.
_SELF_UPGRADE_BOOST_PATTERNS = (
    "self-improv", "self-evolv", "world model",
    "agent planning", "task planning", "agent prompt",
    "code generation", "code patch", "sandbox",
    "a/b test", "benchmark evaluat", "bootloader",
    "hot reload", "atomic deploy", "llm agent",
    "tool use", "tool-use", "agent tool",
    "multi-agent", "agent coordin", "agent memory",
    "agent reflection", "agent reasoning",
)


def _self_upgrade_boost(paper: Paper) -> float:
    """Return a [0, 3] deterministic score based on keyword matches.

    v1.5.0: addresses ISS-001 — LLM scoring is unstable, so we add
    a small deterministic boost to break ties in favor of papers
    that are clearly about self-upgrade / agent planning.  This
    doesn't replace LLM scoring — it only nudges the ranking.
    """
    text = ((paper.title or "") + " " + (paper.abstract or "")).lower()
    hits = sum(1 for p in _SELF_UPGRADE_BOOST_PATTERNS if p in text)
    return min(3.0, float(hits))


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

    v1.5.0: each paper's ``applicability_score`` is bumped by
    ``_self_upgrade_boost(paper)`` (capped at +3) so papers about
    agent planning / self-improvement rank reliably above music
    generation / image segmentation noise.
    """
    scored = []

    for p in papers:
        sp = score_paper(p, config, use_llm=use_llm, llm_config=llm_config)

        # Deterministic boost (ISS-001).  Applied after LLM scoring so
        # it acts as a tie-breaker, not a replacement.
        boost = _self_upgrade_boost(p)
        if boost > 0:
            sp.applicability_score = min(10.0, sp.applicability_score + boost)
            logger.debug(
                f"filter: +{boost:.0f} self-upgrade boost for {p.arxiv_id}"
            )

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
