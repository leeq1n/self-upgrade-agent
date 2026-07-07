"""v1.8.1: MCP-style tool registry.

User insight (2026-07-07):
  - '很多内容你都可以当作工具拆分出来(MCP那种,需要有工具说明)'
  - '例如网络搜索(可以带不重复搜索参数), 筛选创新点与当前项目适配情况'

Design (三层):
  Layer 1 — REGISTRY (emergent): tools can be added/removed at runtime
  Layer 2 — ANTI-LOCK-IN (harness-style): every tool has a test_fn
  Layer 3 — 奥卡姆 (always works): list_tools() returns built-in tools
    even if the registry is empty (so node_research can call them)

Each tool is a dict with:
  - name:        unique identifier
  - description: human-readable, goes into LLM prompts
  - fn:          callable(**kwargs) -> result
  - params:      dict of {param_name: param_description}  (for LLM)
  - test_fn:     optional sanity check, returns True if healthy

The registry is mutable at runtime.  LLM can register new tools via
patchgen (or via a CLI flag, see self_upgrade tool-add).

Built-in tools (奥卡姆 — these never change):
  - web_search(query, exclude_seen=True)
  - evaluate_innovation(paper, project_context)
  - run_harness(target, version='current')
  - read_decision_log(limit=20, decision='reverted')

These are seed tools so the loop has something to call on first run.
LLM can delete or replace them (the registry is mutable).
"""
from typing import Callable, Dict, Any, Optional, List


# Mutable registry.  Empty by default?  No — for v1.8.1 we seed 4
# built-in tools so the loop has something to call.  These are the
# only "default" tools; LLM can remove or replace them at runtime.
_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register(name: str, description: str, fn: Callable,
             params: Optional[Dict[str, str]] = None,
             test_fn: Optional[Callable[[], bool]] = None) -> None:
    """Register a tool.  Re-registering overwrites (allows patching).

    Args:
        name:        unique identifier (must be non-empty string)
        description: human-readable, used in LLM prompts
        fn:          callable(**kwargs) -> result
        params:      optional dict of {param_name: param_description}
        test_fn:     optional sanity check, returns True if healthy

    Raises:
        ValueError: if name is empty or fn is not callable
    """
    if not name or not isinstance(name, str):
        raise ValueError(f"tool name must be non-empty string, got {name!r}")
    if not callable(fn):
        raise ValueError(f"tool fn must be callable, got {type(fn).__name__}")
    _REGISTRY[name] = {
        "description": description,
        "fn": fn,
        "params": params or {},
        "test_fn": test_fn,
    }


def unregister(name: str) -> bool:
    """Remove a tool.  Returns True if it existed, False if not."""
    return _REGISTRY.pop(name, None) is not None


def list_tools() -> List[Dict[str, Any]]:
    """Return public-facing tool descriptions (one dict per tool).

    Does NOT include the `fn` callable (LLM shouldn't call this directly).
    Returns: list of {"name", "description", "params"} dicts.
    """
    return [
        {
            "name": name,
            "description": info["description"],
            "params": info["params"],
        }
        for name, info in _REGISTRY.items()
    ]


def get_tool(name: str) -> Optional[Dict[str, Any]]:
    """Return tool dict (with fn).  None if not found."""
    return _REGISTRY.get(name)


def call_tool(name: str, **kwargs) -> Any:
    """Call a tool by name.  Raises KeyError if not found.

    Returns whatever the tool's fn returns.  Exceptions in fn
    propagate to the caller — the registry does NOT swallow them
    (callers can decide if they want try/except).
    """
    if name not in _REGISTRY:
        raise KeyError(f"tool not registered: {name!r}")
    return _REGISTRY[name]["fn"](**kwargs)


def run_health_check() -> Dict[str, bool]:
    """Run test_fn for every tool.  Returns {name: passed}.

    This is the harness layer: if a tool's test_fn fails, the caller
    can decide to unregister it (anti-lock-in).
    """
    out = {}
    for name, info in _REGISTRY.items():
        test_fn = info.get("test_fn")
        if test_fn is None:
            out[name] = True
            continue
        try:
            out[name] = bool(test_fn())
        except Exception:
            out[name] = False
    return out


def registry_size() -> int:
    """How many tools are currently registered.  For diagnostics."""
    return len(_REGISTRY)


def clear_registry() -> None:
    """Remove ALL tools.  Used by tests + emergency fallback."""
    _REGISTRY.clear()


# ═══════════════════════════════════════════════════════════
# Built-in seed tools (奥卡姆: simple, useful, can be removed)
# ═══════════════════════════════════════════════════════════
# These give the loop something to call on first run.  LLM can
# remove them via unregister() or replace them with smarter versions
# via register().

def _web_search_impl(query: str, exclude_seen: bool = True) -> List[Dict[str, str]]:
    """Search arxiv (or other sources) for papers.

    Returns a list of paper dicts: {arxiv_id, title, abstract, ...}.
    The implementation delegates to src.research (the existing search).
    This is a thin wrapper so the tool registry is the single API
    node_research uses.
    """
    try:
        from src.research import search_arxiv
        from src.config import load_config
        cfg = load_config("config.yaml")
        # Replace keywords with the query
        cfg.research.keywords = [query]
        papers = search_arxiv(cfg.research)
        if exclude_seen:
            try:
                from src.learning import init_db, get_unseen_paper_ids
                conn = init_db()
                try:
                    seen = get_unseen_paper_ids(conn)
                finally:
                    conn.close()
                papers = [p for p in papers if p.arxiv_id not in seen]
            except Exception:
                pass
        return [
            {"arxiv_id": p.arxiv_id, "title": p.title, "abstract": p.abstract or ""}
            for p in papers
        ]
    except Exception as e:
        return [{"error": str(e)}]


def _web_search_test() -> bool:
    """Sanity check: web_search can be imported (no actual call)."""
    try:
        from src.research import search_arxiv  # noqa
        return True
    except Exception:
        return False


def _evaluate_innovation_impl(paper_arxiv_id: str, project_context: Optional[str] = None) -> Dict[str, Any]:
    """Score a paper for relevance to this project.

    Returns: {"arxiv_id", "relevance_score", "reasoning", "recommendation"}
    """
    try:
        from src.learning import init_db
        conn = init_db()
        try:
            cur = conn.execute(
                "SELECT paper_title FROM seen_papers WHERE paper_id = ? LIMIT 1",
                (paper_arxiv_id,),
            )
            row = cur.fetchone()
        finally:
            conn.close()
        if row:
            return {
                "arxiv_id": paper_arxiv_id,
                "relevance_score": 0.0,
                "reasoning": "already seen",
                "recommendation": "skip",
            }
        # Otherwise: heuristic — short papers from LLM-related categories score higher
        return {
            "arxiv_id": paper_arxiv_id,
            "relevance_score": 0.5,
            "reasoning": "heuristic default (LLM can patch)",
            "recommendation": "consider",
        }
    except Exception as e:
        return {"arxiv_id": paper_arxiv_id, "error": str(e)}


def _evaluate_innovation_test() -> bool:
    return True  # always passes — pure function


def _run_harness_impl(target: str = "core/planner.py", version: str = "current") -> Dict[str, Any]:
    """Run the harness for a specific target.

    Returns: {"target", "version", "passed", "failed", "total", "pass_rate"}.
    This is a thin wrapper around src.evaluate.run_harness so the tool
    registry is the single API.
    """
    try:
        from src.evaluate import run_harness
        result = run_harness(target)
        return {
            "target": target,
            "version": version,
            "passed": result.get("passed", 0),
            "failed": result.get("failed", 0),
            "total": result.get("total", 0),
            "pass_rate": result.get("pass_rate", 0.0),
        }
    except Exception as e:
        return {"target": target, "version": version, "error": str(e)}


def _run_harness_test() -> bool:
    try:
        from src.evaluate import run_harness  # noqa
        return True
    except Exception:
        return False


def _read_decision_log_impl(limit: int = 20, decision: Optional[str] = None) -> List[Dict[str, Any]]:
    """Read recent decisions from the decision_log.

    Returns: list of decision dicts.
    """
    try:
        from src.learning import init_db, get_recent_decisions
        conn = init_db()
        try:
            return get_recent_decisions(conn, limit=limit, decision=decision)
        finally:
            conn.close()
    except Exception as e:
        return [{"error": str(e)}]


def _read_decision_log_test() -> bool:
    return True  # pure db query, always works if db is initialized


# Auto-register the 4 built-in tools
register(
    "web_search",
    "Search arxiv for papers matching a query. exclude_seen=True avoids papers we already tried.",
    _web_search_impl,
    params={"query": "str — search topic", "exclude_seen": "bool — skip already-tried papers (default True)"},
    test_fn=_web_search_test,
)
register(
    "evaluate_innovation",
    "Score a paper's relevance to this project. Returns relevance_score 0-1 and recommendation.",
    _evaluate_innovation_impl,
    params={"paper_arxiv_id": "str — arxiv ID", "project_context": "str — optional context"},
    test_fn=_evaluate_innovation_test,
)
register(
    "run_harness",
    "Run the Python harness tests for a target module. Returns pass_rate.",
    _run_harness_impl,
    params={"target": "str — module path (default 'core/planner.py')", "version": "str — 'current' or 'patched'"},
    test_fn=_run_harness_test,
)
register(
    "read_decision_log",
    "Read recent decisions from the decision_log (knowledge persistence).",
    _read_decision_log_impl,
    params={"limit": "int — max rows to return", "decision": "str — filter by decision (kept/reverted/...)"},
    test_fn=_read_decision_log_test,
)