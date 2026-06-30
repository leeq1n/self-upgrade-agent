"""Dynamic keyword expansion — extract trending terms from discovered papers.

[FROZEN v1.1.0] — stable n-gram extraction, tested, do not modify.

Automatically identifies emerging AI/ML methods and trends from paper
titles and abstracts, reducing reliance on manually maintained keywords.
"""
import json
import logging
import os
from collections import Counter
from typing import List

logger = logging.getLogger(__name__)

_TRENDING_CACHE = os.path.join(
    os.path.dirname(__file__), "..", "upgrades", "trending_keywords.json"
)

# Known noise terms to filter out
_NOISE_TERMS = {
    "we", "propose", "introduce", "present", "show", "demonstrate", "paper",
    "method", "approach", "model", "result", "experiment", "performance",
    "state", "art", "novel", "new", "using", "based", "improved", "better",
    "achieve", "outperform", "without", "within", "across", "through",
    "also", "can", "may", "one", "two", "first", "also",
}


def extract_ngrams(text: str, n: int = 2, top_k: int = 20) -> List[str]:
    """Extract top-k n-grams from text, filtering noise.

    Handles both space-separated and hyphenated terms.
    """
    # Normalize and tokenize
    words = text.lower().replace("-", " ").replace(":", " ").split()
    # Filter noise and short words
    words = [w.strip(",.()[]{}\"'") for w in words if len(w) > 2 and w not in _NOISE_TERMS]

    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = " ".join(words[i : i + n])
        if all(w not in _NOISE_TERMS for w in ngram.split()):
            ngrams.append(ngram)

    counter = Counter(ngrams)
    return [term for term, _ in counter.most_common(top_k)]


def extract_trending_keywords(
    titles: List[str],
    abstracts: List[str],
    llm_call=None,
    top_n: int = 10,
) -> List[str]:
    """Extract trending research keywords from paper titles and abstracts.

    Uses n-gram frequency (fast) + optional LLM filtering (accurate).
    """
    # Combine all text
    all_text = " ".join(titles + [a[:500] for a in abstracts])

    # Extract 2-grams and 3-grams
    bigrams = extract_ngrams(all_text, n=2, top_k=top_n * 3)
    trigrams = extract_ngrams(all_text, n=3, top_k=top_n * 2)

    # Merge and deduplicate
    candidates = list(dict.fromkeys(bigrams + trigrams))

    if llm_call and candidates:
        # Use LLM to filter — keep only "method names" and "research trends"
        candidate_list = "\n".join(f"- {c}" for c in candidates[:top_n * 2])
        prompt = (
            f"From the following phrases extracted from AI research papers, "
            f"identify which are actual method names or research trends "
            f"(e.g., 'chain of thought', 'reinforcement learning', 'tool use'). "
            f"Exclude generic descriptions.\n\n"
            f"Phrases:\n{candidate_list}\n\n"
            f"Return ONLY a JSON list of the {top_n} most relevant method/trend names:"
        )
        try:
            response = llm_call(prompt)
            # Try to parse JSON list from response
            import re as _re
            json_match = _re.search(r'\[.*?\]', response or "", _re.DOTALL)
            if json_match:
                filtered = json.loads(json_match.group())
                if isinstance(filtered, list) and filtered:
                    return filtered[:top_n]
        except Exception as e:
            logger.debug(f"LLM keyword filtering failed, using n-gram only: {e}")

    # Fallback: return top n-grams
    return candidates[:top_n]


def merge_keywords(
    existing: List[str],
    new: List[str],
    max_total: int = 15,
) -> List[str]:
    """Merge new keywords into existing list, keeping most frequent at top.

    New keywords are prepended (they represent latest trends).
    Duplicates are removed. Total is capped at max_total.
    """
    # Normalize
    existing_lower = [k.lower() for k in existing]
    merged = list(new)  # Newest first

    for kw in existing:
        if kw.lower() not in [m.lower() for m in merged]:
            merged.append(kw)

    return merged[:max_total]


def update_trending_keywords(papers, existing_keywords: List[str] = None) -> List[str]:
    """Extract keywords from a list of papers and merge with existing.

    Saves the updated keyword list to upgrades/trending_keywords.json.

    Args:
        papers: List of Paper objects (must have title and abstract).
        existing_keywords: Current keyword list. Loads from config if None.

    Returns:
        Updated keyword list (newest first).
    """
    titles = [p.title for p in papers if hasattr(p, 'title')]
    abstracts = [p.abstract for p in papers if hasattr(p, 'abstract')]

    if not titles:
        return existing_keywords or []

    new_kw = extract_trending_keywords(titles, abstracts)

    if existing_keywords is None:
        existing_keywords = []

    merged = merge_keywords(existing_keywords, new_kw)

    # Persist
    try:
        os.makedirs(os.path.dirname(_TRENDING_CACHE), exist_ok=True)
        with open(_TRENDING_CACHE, "w", encoding="utf-8") as f:
            json.dump({"keywords": merged, "extracted_from": len(titles)}, f, indent=2)
    except Exception:
        pass

    logger.info(f"Keywords updated: {len(new_kw)} new from {len(titles)} papers "
                f"→ {len(merged)} total")
    return merged


def load_trending_keywords() -> List[str]:
    """Load previously saved trending keywords."""
    if os.path.exists(_TRENDING_CACHE):
        try:
            with open(_TRENDING_CACHE, encoding="utf-8") as f:
                return json.load(f).get("keywords", [])
        except Exception:
            pass
    return []
