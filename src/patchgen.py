"""
Code patch generation from research papers.

v1.5.0 — aligned with _apply_patch_to_module (surgical merge):

  * Reads the *current* target module and includes it in the prompt, so
    the LLM knows what already exists and can extend rather than rewrite
    from scratch.
  * Requires the patch to (a) keep the existing public functions
    (so callers like core/agent.run keep working) and (b) keep imports
    and __version__ intact.
  * Drops response_format={"type": "json_object"} because ModelScope and
    several other OpenAI-compatible gateways ignore or mangle it.  The
    downstream _parse_llm_json in src/filter.py is more tolerant than
    json.loads; we use that here too.

Outputs a dict shaped like ``{"function": str, "test": str, "module": str}``
suitable for direct use by ``_apply_patch_to_module``.
"""
import json
import logging
import os
import re
from typing import Optional

from src.llm import chat, LLMConfig
from src.research import Paper

logger = logging.getLogger(__name__)


# Target modules in core/ that the agent is allowed to patch.  Mirrors
# src/switcher.py:CORE_MODULES.  We import lazily to avoid a circular dep.
def _core_module_targets() -> dict:
    from src.switcher import CORE_MODULES
    return CORE_MODULES


# Hard-reject papers that are obviously not about AI agents / ML systems.
# This is a coarse safety net on top of filter.py's LLM scoring, because
# LLM scoring can give a high applicability score to a paper that merely
# *mentions* "agent" or "hierarchical" without being about LLM agents.
_REJECT_TITLE_PATTERNS = [
    "song generation", "music generation", "audio synthesis",
    "speech recognition", "speech synthesis", "tts", "asr",
    "image segmentation", "object detection", "image classification",
    "video generation", "video synthesis", "3d reconstruction",
    "protein folding", "drug discovery", "genomic",
    "weather", "climate", "ocean",
    "robot", "robotic grasping", "manipulation", "locomotion",
    "translation", "machine translation",
    "recommender", "advertising", "click prediction",
]
_REJECT_CATEGORY_PATTERNS = [
    "q-bio", "stat.AP", "eess.AS", "cs.SD", "cs.CV", "physics.",
]


def _paper_is_obviously_unrelated(paper: Paper) -> bool:
    """Quick reject: paper is clearly not about AI / ML agents.

    Returns True if the paper should be skipped entirely.  This is
    deliberately conservative — better to skip a borderline case than
    to waste an LLM call on a paper about music generation.
    """
    title_lower = (paper.title or "").lower()
    abstract_lower = (paper.abstract or "").lower()
    for pat in _REJECT_TITLE_PATTERNS:
        if pat in title_lower:
            return True
    cats = (paper.categories or "").lower()
    for pat in _REJECT_CATEGORY_PATTERNS:
        if pat in cats:
            return True
    # Negative signal: paper is clearly not in CS (e.g. heavily
    # biology / physics jargon).  This is best-effort, not a guarantee.
    if "agent" not in title_lower and "agent" not in abstract_lower and \
       "llm" not in title_lower and "llm" not in abstract_lower and \
       "language model" not in abstract_lower and \
       "reinforcement" not in abstract_lower and \
       "prompt" not in abstract_lower and \
       "tool" not in abstract_lower and \
       "planner" not in abstract_lower and \
       "plan" not in abstract_lower:
        # No agent/LLM/RL/prompt content at all — probably not relevant.
        return True
    return False


def _read_target_module(target_module: str) -> str:
    """Return the *current* source of core/<target_module>, or '' if missing.

    We feed this to the LLM so it can write a patch that builds on
    existing code instead of starting from scratch (which would lose
    imports, __version__, and existing public functions).
    """
    try:
        targets = _core_module_targets()
        path = targets.get(target_module)
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.debug(f"could not read {target_module}: {e}")
    return ""


def _extract_public_functions(source: str) -> list:
    """Return a list of top-level def names declared in ``source``."""
    return re.findall(r"^def\s+(\w+)\s*\(", source, flags=re.MULTILINE)


# Generic markdown-fence strip — we use this because response_format
# is unreliable on OpenAI-compatible gateways.  The same logic lives in
# src/filter.py:_parse_llm_json, but we re-implement lightly to keep
# this module self-contained.
_FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE | re.MULTILINE)


def _parse_json_lenient(content: str) -> Optional[dict]:
    if not content:
        return None
    s = content.strip()
    # Try direct parse first.
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    # Strip fences.
    s2 = _FENCE.sub("", s).strip()
    if s2 and s2 != s:
        try:
            return json.loads(s2)
        except json.JSONDecodeError:
            pass
    # First balanced {...} block.
    m = re.search(r"\{[^{}]*\}", s, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _format_loop_feedback(loop_state: Optional[dict]) -> str:
    """Format the loop feedback section for the patchgen prompt.

    Returns a multi-line string describing:
      - what the last round did
      - what was tried before
      - current sandbox compatibility info

    Returns "" if loop_state is None or empty (LLM gets no extra context).
    """
    if not loop_state:
        return ""

    lines = []

    last = loop_state.get("last_outcome")
    if last:
        decision = last.get("decision", "?")
        delta = last.get("delta")
        harness = last.get("harness_pass_rate")
        if delta is not None:
            lines.append(f"- Last round: decision={decision}, delta={delta:+.1%}")
        else:
            lines.append(f"- Last round: decision={decision}")
        if harness is not None:
            lines.append(f"- Last round harness: {harness:.0%}")
        errs = last.get("errors") or []
        if errs:
            err_summary = "; ".join(str(e)[:80] for e in errs[:2])
            lines.append(f"- Last round errors: {err_summary}")

    # v1.8.1: knowledge persistence from decision_log
    recent = loop_state.get("recent_failures_str")
    if recent:
        lines.append(f"- Recent outcomes (last 20): {recent}")
    top_fm = loop_state.get("top_failure_mode")
    if top_fm:
        lines.append(f"- Top failure mode: {top_fm}")

    seen_count = loop_state.get("seen_papers_count")
    if seen_count:
        lines.append(f"- We have previously attempted {seen_count} papers.")

    seen_topics = loop_state.get("seen_topics") or []
    if seen_topics:
        topic_list = ", ".join(seen_topics[:8])
        lines.append(f"- Topics already explored (avoid repeating): {topic_list}")

    sandbox = loop_state.get("sandbox_info") or {}
    if sandbox:
        py_v = sandbox.get("python_version", "?")
        path = sandbox.get("sys_path_sample", "")[:80]
        lines.append(f"- Runtime: Python {py_v}; sys.path includes {path}")

    long_goal = loop_state.get("long_term_goal")
    if long_goal:
        lines.append(f"- Long-term goal: {long_goal}")

    if not lines:
        return ""

    return "Loop feedback (v1.8.1):\n" + "\n".join(lines)


PROMPT_TEMPLATE = """\
You are modifying a small Python module in a self-improving agent system.

The CURRENT source of core/{target_module} is:

```python
{current_source}
```

Public functions currently defined here: {public_funcs}
`__version__` is currently: {current_version}

A research paper with the following method/idea was discovered:

  Title: {title}
  Abstract: {abstract}

{loop_feedback}

Your task: write a surgical PATCH that adapts an EXISTING function
(typically `{primary_func}`) to incorporate insights from the paper.

HARD CONSTRAINTS — your patch will be rejected if you violate these:

  1. Keep the existing public function signature(s).  In particular
     `def {primary_func}(...)` must still exist and accept the same
     arguments.  You may change the body, add helpers, or add new
     functions, but DO NOT rename or remove existing public functions.
  2. Keep all existing imports intact.  You may add new imports if
     the paper's method requires them.
  3. Keep `__version__` declared at module level (you may bump it to
     "{primary_func}_v2" or similar if you want, but don't delete it).
  4. The patch must be a single function (or a small set of helper
     defs) — NOT a full-file rewrite.  Our surgical-merge code
     will splice your patch into the existing module.
  5. Include a small `test_xxx` function in the same patch that
     demonstrates the improvement.

Reply with ONLY a JSON object of this exact shape (no prose, no
markdown fences — raw JSON):

{{"function": "<python source>", "test": "<python source>", "module": "{target_module}"}}
"""


def generate_patch(
    paper: Paper,
    target_module: str = "planner.py",
    llm_config: Optional[LLMConfig] = None,
    loop_state: Optional[dict] = None,
) -> Optional[dict]:
    """Generate a surgical patch.

    v1.8.1: optional `loop_state` carries last_outcome + sandbox context
    so the LLM sees what was tried before.  See _format_loop_feedback.
    """
    """Generate a surgical patch for a core agent module from a paper.

    Returns ``{"function": ..., "test": ..., "module": ...}`` on success
    or ``None`` if generation / parsing failed.
    """
    # Hard pre-filter: skip papers that are clearly not about AI/ML
    # agents (e.g. music generation, image segmentation).  This is a
    # defense against filter.py's LLM scoring occasionally promoting
    # a paper that merely *mentions* "agent" or "hierarchical" but
    # isn't actually about LLM-based agents.
    if _paper_is_obviously_unrelated(paper):
        logger.info(
            f"patchgen: skipping {paper.arxiv_id!r} ({paper.title[:60]!r}) — "
            f"obviously unrelated to AI/ML agents"
        )
        return None

    current_source = _read_target_module(target_module)
    public_funcs = _extract_public_functions(current_source) or ["plan_task"]
    primary_func = "plan_task" if "plan_task" in public_funcs else public_funcs[0]
    version_m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', current_source)
    current_version = version_m.group(1) if version_m else "1.0.0"

    # v1.8.1: inject loop feedback so LLM knows what was tried before.
    # If state not passed, this is empty (LLM gets minimal context).
    loop_feedback = _format_loop_feedback(loop_state)

    # v1.8.2: query memory for similar past patches / papers and inject
    # as context.  This is the "memory affects code change" requirement.
    memory_context = ""
    try:
        from src.mcp_client import call_tool as _call_tool
        query_text = (
            (paper.title or "") + " " +
            (paper.abstract or "")[:500] + " " +
            primary_func
        )
        relevant = _call_tool("memory_search", query=query_text, top_k=3)
        if relevant:
            lines = ["Relevant prior context (from memory MCP):"]
            for unit in relevant:
                lines.append(
                    f"  [{unit.get('kind','?')}] {unit.get('text','')[:200]}"
                )
            memory_context = "\n".join(lines)
    except Exception:
        # Memory unavailable — proceed without context (pipeline never breaks here)
        memory_context = ""

    prompt = PROMPT_TEMPLATE.format(
        target_module=target_module,
        current_source=current_source or "(file is empty — generate a sensible first version)",
        public_funcs=", ".join(public_funcs) or "(none)",
        current_version=current_version,
        title=paper.title,
        abstract=(paper.abstract or "")[:1500],
        primary_func=primary_func,
        memory_context=memory_context or "(no prior memory)",
        loop_feedback=loop_feedback,
    )

    resp = chat(
        messages=[{"role": "user", "content": prompt}],
        config=llm_config,
        # v1.8.3: thinking DISABLED.  Earlier iterations tried
        # thinking_budget=4096 (ate all max_tokens) and 1024 (still
        # left <500 tokens for code, causing empty content on minimax
        # M2 — see commit e162cd1).  Reasoning now lives in the prompt
        # itself (ReAct format), so we don't need in-model thinking.
        enable_thinking=False,
        thinking_budget=0,
        # NOTE: no response_format here — ModelScope etc. ignore it and
        # sometimes mangle the response.  _parse_json_lenient handles
        # both raw JSON and ```json ... ```-fenced output.
    )

    if not resp.content:
        logger.warning("patchgen: LLM returned empty content")
        return None

    data = _parse_json_lenient(resp.content)
    if not data:
        logger.warning(f"patchgen: could not parse JSON from LLM output: {resp.content[:200]!r}")
        return None

    fn = data.get("function", "")
    test = data.get("test", "")
    module = data.get("module", target_module)
    if not fn or len(fn) < 30:
        logger.warning(f"patchgen: 'function' missing or too short ({len(fn)} chars)")
        return None
    if not test or len(test) < 20:
        logger.warning(f"patchgen: 'test' missing or too short ({len(test)} chars)")
        return None

    # Sanity check: does the patch define the primary function?  If not,
    # surgical merge would either replace some other function or append
    # at the end — neither is what we want.
    #
    # v1.8.1: accept relaxed patterns.  M2 occasionally renames to
    # `plan_task_v2`, `plan_task_inner`, `_plan_task`, etc.  Try the
    # exact match first; fall back to a fuzzy match on the bare name.
    primary_name = re.escape(primary_func)
    if not re.search(rf"def\s+{primary_name}\s*\(", fn):
        fuzzy = re.search(rf"def\s+[\w]*?{primary_name}[\w]*?\s*\(", fn)
        if fuzzy:
            logger.info(
                f"patchgen: relaxed match — found {fuzzy.group(0).strip()} "
                f"instead of strict def {primary_func}().  Accepting."
            )
        else:
            logger.warning(
                f"patchgen: patch does not define {primary_func}() "
                f"(even fuzzy).  Surgical merge may misroute.  Returning None."
            )
            return None

    return {"function": fn, "test": test, "module": module}
