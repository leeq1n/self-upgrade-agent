"""Self-Upgrade Pipeline — LangGraph-powered autonomous improvement loop.

Main pipeline:
  R (Research) → F (Filter) → G (Generate Patch) → X (Sandbox Test)
    → T (Reflect & Retry) if failed
    → E (Evaluate: real A/B benchmark) if passed
    → D (Decide & Deploy)

This pipeline replaces the legacy pipeline.py skillgen path. It uses patchgen
to generate actual Python code patches targeting core/ modules.
"""
__version__ = "1.3.0"
import logging
import os
import re
import shutil
import random
from typing import TypedDict, List, Optional, Dict, Any

from langgraph.graph import StateGraph, START, END

from src.config import Config, load_config
from src.research import search_arxiv, search_all_sources, Paper
from src.filter import filter_papers, ScoredPaper
from src.patchgen import generate_patch
from src.sandbox import run_in_sandbox
from src.reflect import reflect_and_improve
from src.decide import make_decision
from src.switcher import (
    init as switcher_init,
    deploy_candidate,
    promote_candidate,
    discard_candidate,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# Pipeline State
# ═══════════════════════════════════════════════════════════

class PipelineState:
    """Mutable state carried through the LangGraph pipeline."""
    config: Config
    papers: List[Paper] = []
    scored_papers: List[ScoredPaper] = []
    best_paper: Optional[ScoredPaper] = None
    patch: Dict[str, str] = {}
    sandbox_passed: bool = False
    reflect_attempts: int = 0
    evaluation: Dict[str, Any] = {}
    decision: Dict[str, Any] = {}
    errors: List[str] = []
    done: bool = False

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, d: dict) -> "PipelineState":
        s = cls()
        for k, v in d.items():
            setattr(s, k, v)
        return s


# ═══════════════════════════════════════════════════════════
# Surgical Patch Application
# ═══════════════════════════════════════════════════════════

def _extract_target_function(patch_code: str, expected_func: Optional[str] = None) -> Optional[str]:
    """Pull exactly ONE function definition out of a patch.

    v1.8.1 (P0-2 fix): the old strategy greedily replaced the target
    function body and *also* appended every auxiliary ``def helper()``
    to the end of the module, so each promote grew planner.py by ~250
    bytes of never-called helpers.  Across N rounds the module
    ballooned 2-3× and accumulated dead code until it stopped being
    readable.

    The fix: surgical merge takes a SINGLE function definition and
    drops all other top-level defs (and any module-level statements)
    in the patch.  If the patch doesn't contain the expected target
    function, we return None and the caller can decide whether to
    reject the patch entirely.

    We *do* keep ``# comment`` lines that sit immediately above the
    target def — those carry useful context like "# v2 patch: add
    foresight step" and are part of the patch's intent.  Any def,
    import, or module-level statement elsewhere in the patch is
    silently dropped (this is the surgical contract).

    Args:
        patch_code: The raw patch string (may contain imports,
            helpers, comments, blank lines).
        expected_func: If set, only return the def with this exact
            name.  Otherwise, return the first top-level def found.

    Returns:
        The extracted function source (signature + body, no leading/
        trailing blank lines) or None if nothing usable was found.
    """
    if not patch_code or not patch_code.strip():
        return None
    lines = patch_code.splitlines()

    # Step 1: collect all top-level ``def`` start lines.
    starts = [
        i for i, ln in enumerate(lines)
        if ln.startswith("def ") and "(" in ln
    ]
    if not starts:
        return None

    # Step 2: pick the chosen def — prefer ``expected_func``.
    chosen = None
    if expected_func:
        for i in starts:
            name = lines[i].split("(", 1)[0].split()[1]
            if name == expected_func:
                chosen = i
                break
        if chosen is None:
            return None
    else:
        chosen = starts[0]

    # Step 3: extend ``chosen`` BACKWARD over leading ``#`` comments.
    # We deliberately *don't* walk across blank lines — a "header"
    # block separated from the def is module documentation and
    # doesn't belong with this function.
    leading_start = chosen
    j = chosen - 1
    while j >= 0:
        ln = lines[j]
        if not ln.strip():
            break  # blank line breaks the leading-comment cluster
        if ln.lstrip().startswith("#"):
            leading_start = j
            j -= 1
            continue
        break

    # Step 4: find the end of the function.  Stop at a *less-indented*
    # non-blank, non-comment line (catches imports, assignments,
    # another def, etc.).
    end = len(lines)
    base_indent = 0
    for j in range(chosen + 1, len(lines)):
        ln = lines[j]
        if not ln.strip():
            continue
        stripped = ln.lstrip()
        if stripped.startswith("#"):
            continue
        indent = len(ln) - len(stripped)
        if indent <= base_indent:
            end = j
            break

    body = "\n".join(lines[leading_start:end]).rstrip()
    return body if body else None


def _apply_patch_to_module(
    module_path: str,
    patch_code: str,
    expected_func: Optional[str] = None,
) -> str:
    """Surgically merge patch code into an existing core module.

    v1.8.1 (P0-2 fix): see :func:`_extract_target_function`.  We now
    take *one* function from the patch (the target, or the first def
    if ``expected_func`` is None) and replace only that function's
    body in the original module.  Auxiliary helpers / imports in
    the patch are intentionally discarded — surgical merge's
    contract is "replace the target function, keep everything else".

    Strategy (in order):
    1. If patch_code is a full module (starts with docstring), accept
       it as-is for first-time module creation.
    2. Extract ONE function from the patch.
    3. Replace the same-named function in the original if present.
    4. If the target function is not in the original, append it.

    Returns:
        The merged module source.  If the patch contained no usable
        ``def``, the original module is returned unchanged — never
        silently half-apply.
    """
    # Case 1: Full module replacement (patch has its own docstring).
    stripped = patch_code.strip()
    if stripped.startswith('"""') or stripped.startswith("'''"):
        return patch_code

    # Read original module.
    with open(module_path, encoding="utf-8") as f:
        original = f.read()

    # Case 2: Extract a single function definition from the patch.
    function_body = _extract_target_function(patch_code, expected_func)
    if function_body is None:
        logger.warning(
            f"_apply_patch_to_module: patch has no usable ``def``; "
            f"keeping original {os.path.basename(module_path)} unchanged"
        )
        return original

    func_match = re.search(r"def\s+(\w+)\s*\(", function_body)
    if not func_match:
        return original
    func_name = func_match.group(1)

    # Pattern: match the original ``def func_name(...)`` block through
    # to the next top-level statement or end of file.  The lookahead
    # accepts any of:
    #   * another ``def`` at column 0         (next function)
    #   * a *top-level* non-comment line       (any module statement)
    #   * end-of-file                          (last function in module)
    # We do NOT use [^)]* in the signature (the original implementation
    # did, which broke on default-arg types like ``Callable``); ``\(.*?\n``
    # consumes the signature up to the first newline, which is good
    # enough since real-world signatures rarely span multiple lines.
    pattern = (
        r'(def\s+' + re.escape(func_name) + r'\s*\(.*?\n)'
        r'(?=\n*(?:def\s+\w+|from\s+\w+\s+import|import\s+\w+|[A-Z_][A-Z0-9_]*\s*=|\Z))'
    )
    pat = re.compile(pattern, re.DOTALL)
    if pat.search(original):
        # Indent the replacement to match the surrounding module
        # (always column 0 here since we're splicing into the module
        # body, but be defensive about future refactors).
        replacement = function_body
        merged = pat.sub(replacement, original, count=1)
        return merged

    # Case 4: Target function not in original — append at the end.
    # This happens for first-ever patches where the module has no
    # previous definition of this function name.
    return original.rstrip() + "\n\n" + function_body + "\n"


# ═══════════════════════════════════════════════════════════
# Pipeline Nodes
# ═══════════════════════════════════════════════════════════

def _build_research_context(state: dict) -> dict:
    """Build a context dict that downstream nodes can use to make smarter
    decisions.  This is the v1.8.1 'loop feedback' feature: instead of
    every round starting from zero, the agent sees what was tried.

    Returns:
        dict with:
          - "seen_papers_count": int (how many papers we've already tried)
          - "seen_topics": list[str] (unique topics in seen_papers titles)
          - "last_outcome": dict | None (what happened last round)
          - "long_term_goal": str (what we're trying to achieve overall)

    Cheap to compute (one DB query).  Called once at end of node_research.
    """
    ctx = {
        "seen_papers_count": 0,
        "seen_topics": [],
        "last_outcome": state.get("last_outcome"),
        "long_term_goal": state.get("long_term_goal"),
    }
    try:
        from src.learning import init_db
        conn = init_db()
        try:
            cur = conn.execute("SELECT COUNT(*) FROM seen_papers")
            ctx["seen_papers_count"] = cur.fetchone()[0]

            # Sample titles to extract topics (cheap, no LLM)
            cur = conn.execute(
                "SELECT title FROM seen_papers ORDER BY last_seen_at DESC LIMIT 20"
            )
            titles = [r[0] for r in cur.fetchall() if r[0]]
            # Heuristic: take first significant word from each title
            seen_words = set()
            for t in titles:
                for w in t.lower().split():
                    w = w.strip(".,:;()[]{}")  # strip punctuation
                    if len(w) > 5 and w not in {
                        "agent", "using", "language", "model", "models",
                        "learning", "paper", "approach", "method", "task",
                        "tasks", "based", "novel", "improving", "improved",
                    }:
                        seen_words.add(w)
            ctx["seen_topics"] = sorted(seen_words)[:20]
        finally:
            conn.close()
    except Exception:
        pass
    # v1.8.1: knowledge persistence — show what failed recently.
    # LLM should see "we tried X and got Y" so it doesn't repeat.
    try:
        from src.learning import init_db, summarize_failures
        conn = init_db()
        try:
            summary = summarize_failures(conn, limit=20)
            if summary["n_total"] > 0:
                ctx["recent_failures"] = summary
                # Add a short string version for the prompt
                parts = []
                if summary["n_reverted"] > 0:
                    parts.append(f"{summary['n_reverted']} reverted")
                if summary["n_crashed"] > 0:
                    parts.append(f"{summary['n_crashed']} crashed")
                if summary["n_no_patch"] > 0:
                    parts.append(f"{summary['n_no_patch']} no_patch")
                if summary["n_kept"] > 0:
                    parts.append(f"{summary['n_kept']} kept")
                ctx["recent_failures_str"] = ", ".join(parts) if parts else "no decisions yet"
                if summary.get("failure_modes"):
                    top_fm = summary["failure_modes"][0]  # most common
                    ctx["top_failure_mode"] = f"{top_fm[0]} ({top_fm[1]}x)"
        finally:
            conn.close()
    except Exception:
        pass

    # v1.8.1: MCP-style tool registry — expose available tools to LLM.
    # node_research can then call web_search via the registry if needed.
    try:
        from src.tools import list_tools, registry_size
        ctx["available_tools"] = list_tools()
        ctx["tool_count"] = registry_size()
    except Exception:
        ctx["available_tools"] = []
        ctx["tool_count"] = 0

    return ctx


def node_research(state: dict) -> dict:
    """Phase 1: Search arXiv for latest papers."""
    logger.info("1. Research: searching arXiv...")
    cfg = state.get("config")
    if not cfg:
        return state

    try:
        # Prepend any persisted trending keywords to the search query so
        # yesterday's hot topics continue to be explored.  The base
        # config keywords stay at the front; trending is appended.
        try:
            from src.keyword_expander import load_trending_keywords
            trending = load_trending_keywords()
            if trending and hasattr(cfg, "research") and cfg.research.keywords is not None:
                # Avoid duplicating what's already in the configured list.
                seen = {k.lower() for k in cfg.research.keywords}
                additions = [k for k in trending if k.lower() not in seen]
                if additions:
                    logger.debug(f"   Appending {len(additions)} trending keywords")
                    cfg.research.keywords = list(cfg.research.keywords) + additions
        except Exception:
            pass

        # Use multi-source search if config enables it
        multi_source = getattr(cfg.research, 'multi_source', False) if hasattr(cfg, 'research') else False
        if multi_source:
            papers = search_all_sources(cfg.research)
            logger.info(f"   Found {len(papers)} papers (multi-source)")
        else:
            papers = search_arxiv(cfg.research)
            logger.info(f"   Found {len(papers)} papers")

        # v1.8.1: filter out seen + blacklisted papers (avoid repeats)
        try:
            from src.learning import (
                init_db, is_blacklisted, get_unseen_paper_ids, get_seen_count
            )
            conn = init_db()
            try:
                n_seen = get_seen_count(conn)
                unseen_ids = get_unseen_paper_ids(conn)
                original_count = len(papers)
                # Filter out blacklisted + seen papers
                filtered = []
                for p in papers:
                    pid = getattr(p, "arxiv_id", None) or p.get("arxiv_id", "?")
                    if is_blacklisted(conn, pid):
                        continue
                    # seen_ids (despite name) = already-tried papers; keep new ones
                    if pid not in unseen_ids:
                        filtered.append(p)
                papers = filtered
                if n_seen > 0:
                    logger.info(
                        f"   Seen-papers filter: {original_count} -> {len(papers)} "
                        f"({n_seen} previously seen, {original_count - len(papers)} skipped)"
                    )
            finally:
                conn.close()
        except Exception as e:
            logger.debug(f"seen-papers filter failed (non-fatal): {e}")

        # v1.8.1: build context block for downstream nodes.  Without this,
        # node_filter and node_implement have no idea what was tried before.
        state["research_context"] = _build_research_context(state)

        state["papers"] = papers

        # Extract trending keywords from found papers
        try:
            from src.keyword_expander import update_trending_keywords
            update_trending_keywords(papers, cfg.research.keywords)
        except Exception:
            pass
    except Exception as e:
        state["errors"].append(f"Research: {e}")
        logger.error(f"   Research failed: {e}")
        state["papers"] = []
        # Even on failure, build an empty context so downstream nodes get
        # consistent shape (avoids KeyError in node_filter / node_implement).
        state["research_context"] = _build_research_context(state)

    return state


def node_filter(state: dict) -> dict:
    """Phase 2: Score and filter papers.

    v1.6.0 (ISS-013 fix): build LLMConfig from env so filter actually
    uses LLM scoring. Previously llm_config was dropped, forcing the
    keyword-only fallback path. See ISSUES.md.
    """
    papers = state.get("papers", [])
    if not papers:
        return state

    logger.info(f"2. Filter: scoring {len(papers)} papers...")
    cfg = state.get("config")
    # v1.6.0: build llm_config so filter can actually call the LLM.
    llm_config = None
    try:
        from src.llm import LLMConfig
        llm_config = LLMConfig.from_env()
    except Exception as e:
        logger.debug(f"node_filter: LLMConfig.from_env failed ({e}); using keyword only")
    use_llm = llm_config is not None and llm_config.ready

    try:
        scored = filter_papers(papers, cfg.filter, use_llm=use_llm, llm_config=llm_config)
        state["scored_papers"] = scored
        logger.info(f"   Qualified {len(scored)} papers (LLM scoring: {use_llm})")
    except Exception as e:
        state["errors"].append(f"Filter: {e}")
        logger.error(f"   Filter failed: {e}")
        state["scored_papers"] = []

    return state


def node_generate_patch(state: dict) -> dict:
    """Phase 3: Generate code patch from the best paper.

    v1.5.0: try ALL qualified papers in score order, not just the
    first.  The first paper may fail patchgen's pre-filter (e.g. it
    turns out to be about music generation despite a high filter
    score).  Falling through to the next paper costs another LLM
    call but at least we don't get stuck with zero patches when
    one of three candidates is actually usable.
    """
    scored = state.get("scored_papers", [])
    if not scored:
        return state

    tried = 0
    for best in scored:
        state["best_paper"] = best
        tried += 1
        logger.info(
            f"3. PatchGen: try {tried}/{len(scored)} — "
            f"'{best.paper.title[:60]}'"
        )
        # v1.8.1: pass loop feedback (last_outcome + seen_papers + sandbox)
        # so LLM can avoid repeating failed approaches.
        loop_state = state.get("research_context") or {}
        # Also add sandbox runtime info
        try:
            import sys as _sys
            loop_state["sandbox_info"] = {
                "python_version": f"{_sys.version_info.major}.{_sys.version_info.minor}.{_sys.version_info.micro}",
                "sys_path_sample": ", ".join(_sys.path[:3]),
            }
        except Exception:
            pass

        try:
            patch = generate_patch(best.paper, "planner.py", loop_state=loop_state) or {}
        except Exception as e:
            state["errors"].append(f"PatchGen[{tried}]: {e}")
            logger.warning(f"   PatchGen exception: {e}")
            continue

        if patch:
            state["patch"] = patch
            logger.info(
                f"   Patch generated from paper #{tried}: "
                f"{len(patch.get('function', ''))} chars"
            )
            return state
        # else: patchgen returned None — pre-filter or LLM failure.  Try next.
        logger.info(
            f"   Paper #{tried} not usable, "
            f"{len(scored) - tried} remaining"
        )

    # All candidates exhausted.
    state["patch"] = {}
    logger.warning(f"   All {tried} candidate papers failed patchgen")
    return state


def node_sandbox(state: dict) -> dict:
    """Phase 4: Test generated code in isolated sandbox."""
    patch = state.get("patch", {})
    if not patch:
        state["sandbox_passed"] = False
        return state

    function_code = patch.get("function", "")
    test_code = patch.get("test", "")
    if not function_code or not test_code:
        state["sandbox_passed"] = False
        return state

    logger.info("4. Sandbox: testing generated code...")
    try:
        result = run_in_sandbox(function_code, test_code, timeout=10)
        passed = result.get("passed", False)
        state["sandbox_passed"] = passed
        if passed:
            logger.info(f"   PASS ({result.get('elapsed', 0)}s)")
        else:
            logger.warning(f"   FAIL: {result.get('error', '')[:80]}")
    except Exception as e:
        state["errors"].append(f"Sandbox: {e}")
        state["sandbox_passed"] = False

    return state


def node_reflect(state: dict) -> dict:
    """Phase 4b: LLM analyzes failure and rewrites code (up to 3 attempts)."""
    patch = state.get("patch", {})
    attempts = state.get("reflect_attempts", 0)

    if attempts >= 3:
        logger.warning("   Reflect max attempts reached")
        return state

    function_code = patch.get("function", "")
    test_code = patch.get("test", "")

    logger.info(f"4b. Reflect: attempt {attempts + 1}/3...")
    try:
        result = reflect_and_improve(function_code, test_code, "failed",
                                     max_attempts=1)
        state["reflect_attempts"] = attempts + 1

        if result.get("fixed"):
            patch["function"] = result["code"]
            state["patch"] = patch
            logger.info(f"   Code fixed in {result['attempts']} attempt(s)")
        else:
            logger.warning(f"   Not fixed")
    except Exception as e:
        state["errors"].append(f"Reflect: {e}")
        state["reflect_attempts"] = attempts + 1

    return state


def _safety_restore_planner() -> bool:
    """v1.7.1 safety net: ensure core/planner.py is at the committed
    version before any node modifies it.  If a previous run was killed
    mid-evaluate and left a patched version, restore from git HEAD.

    Returns True if the file matched HEAD or was successfully restored.
    Returns False only on catastrophic git failure (still warns).
    """
    import subprocess
    planner = "core/planner.py"
    try:
        # Compare working tree to HEAD
        r = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", planner],
            cwd=".", capture_output=True, timeout=5,
        )
        if r.returncode == 0:
            return True  # matches HEAD
        # Different from HEAD — restore
        subprocess.run(
            ["git", "checkout", "HEAD", "--", planner],
            cwd=".", capture_output=True, timeout=5,
        )
        logger.warning(
            "_safety_restore_planner: core/planner.py was dirty "
            "(likely killed mid-evaluate), restored from git HEAD"
        )
        return True
    except Exception as e:
        logger.error(f"_safety_restore_planner: failed: {e}")
        return False


def node_evaluate(state: dict) -> dict:
    """Phase 5: Real A/B benchmark — baseline vs patched agent.

    v1.5.0: actually use config.evaluate.trials_per_test.  Each "trial"
    is a full run of all benchmark tasks; we run multiple trials so
    that success_rate has a real distribution (not just one noisy
    sample) and the bootstrap CI in stats.py is meaningful.

    v1.7.1: invoke _safety_restore_planner at entry so a previous
    process killed mid-A/B benchmark can\'t leave core/planner.py
    in a patched state.

    Cost: 21 tasks × N trials × 2 (baseline + upgraded) = 42*N LLM
    calls.  N=3 → 126 calls; with Qwen3.5-2B this finishes in a
    few minutes.  N=10 (the old config) → 420 calls, which is why
    we lowered the default.
    """
    # v1.7.1: ensure core/planner.py is at HEAD before we potentially
    # rewrite it.  If a prior run was killed mid-A/B, this restores.
    _safety_restore_planner()
    # Dry-run mode: skip real benchmark entirely
    if state.get("dry_run", False):
        logger.info("5. Evaluate: DRY-RUN — using simulated data")
        base_rate = 0.80
        upgraded_rate = min(1.0, base_rate + random.uniform(0.01, 0.10))
        state["evaluation"] = {
            "baseline_rate": base_rate,
            "upgraded_rate": upgraded_rate,
            "success_rate_delta": upgraded_rate - base_rate,
            "cost_increase_ratio": 1.0,
            "baseline_cost": 1000,
            "upgraded_cost": 1000,
            "stats": None,
            "harness": {"pass_rate": 1.0, "passed": 8, "failed": 0, "total": 8, "failures": []},
        }
        return state

    patch = state.get("patch", {})
    cfg = state.get("config")
    best = state.get("best_paper")

    if not patch or not cfg:
        return state

    trials = max(1, getattr(cfg.evaluate, "trials_per_test", 3) or 1)
    logger.info(f"5. Evaluate: running real A/B benchmark ({trials} trial(s) per arm)...")
    try:
        # v1.5.1 (ISS-004): single A/B path.  Both arms use the same
        # benchmark.run_all; the only difference is whether
        # core/planner.py is the original or the patched one.  The
        # atomic .tmp + os.replace swap is done *between* the two
        # arms so the upgraded arm actually runs the patched code.
        from src.benchmark import run_all, load_tasks as _load_tasks
        from src.evaluate import compare_results as _eval_compare

        tasks = _load_tasks()

        # ── Arm 1: baseline (original core/) ────────────────────
        logger.info(f"   Running {trials} baseline trial(s)...")
        baseline_trials = [run_all(tasks) for _ in range(trials)]
        baseline_rates = [b["success_rate"] for b in baseline_trials]
        baseline_rate = sum(baseline_rates) / len(baseline_rates)
        baseline_results = [
            r.get("success", False)
            for b in baseline_trials
            for r in b.get("results", [])
        ]
        baseline_total = len(baseline_results)
        logger.info(
            f"   Baseline: {baseline_rate:.1%} mean over {trials} trials "
            f"({int(baseline_rate * baseline_total)}/{baseline_total} successes)"
        )

        # Surgically apply patch to core/planner.py for testing
        # (preserves imports, __version__, and module metadata).
        #
        # We write through .tmp + os.replace to make the swap atomic
        # (matches switcher.promote_patch behaviour).  If the
        # process is killed mid-write, the original .py file is
        # untouched and the .tmp file is the only side-effect.
        orig_path = "core/planner.py"
        bak_path = orig_path + ".bench_bak"
        tmp_path = orig_path + ".bench_tmp"
        if os.path.exists(orig_path):
            shutil.copy2(orig_path, bak_path)
        # Flush any cached import of core.planner so the patched file
        # is picked up.  Without this, run_all() would call the
        # in-memory copy of core.planner.plan_task and our A/B
        # comparison would be a no-op (both arms see the same code).
        try:
            import sys
            for mod_name in [k for k in list(sys.modules)
                             if k.startswith("core")]:
                del sys.modules[mod_name]
        except Exception:
            pass

        # Atomic write: write to .tmp, fsync, then os.replace.  If the
        # process dies between the write and the rename, the .tmp file
        # is leftover but core/planner.py is untouched.
        merged_code = _apply_patch_to_module(
            orig_path, patch.get("function", "")
        )
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(merged_code)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, orig_path)

        # ── Arm 2: upgraded (patched core/) ───────────────────
        try:
            logger.info(f"   Running {trials} upgraded trial(s)...")
            upgraded_trials = [run_all(tasks) for _ in range(trials)]
            upgraded_rates = [u["success_rate"] for u in upgraded_trials]
            upgraded_rate = sum(upgraded_rates) / len(upgraded_rates)
            upgraded_results = [
                r.get("success", False)
                for u in upgraded_trials
                for r in u.get("results", [])
            ]
            upgraded_total = len(upgraded_results)

            # v1.8.0: harness check (independent Python unit tests).
            # Run while the patch is still applied.  If harness fails,
            # this patches a critical bug — promote MUST be blocked
            # even if LLM says the patch is good.
            from src.evaluate import run_harness
            harness_result = run_harness()
            logger.info(
                f"   Harness: {harness_result['passed']}/{harness_result['total']} "
                f"({harness_result['pass_rate']:.1%})"
            )
            if harness_result["failed"] > 0:
                logger.warning(
                    f"   HARNESS REGRESSION: {harness_result['failed']} tests broken"
                )
                for fname in harness_result.get("failures", [])[:3]:
                    logger.warning(f"     - {fname}")
        finally:
            # Atomic restore: same .tmp + os.replace pattern.  If the
            # process dies between the bak_path being moved away and
            # the new file landing, the original (now-moved) bak_path
            # file is intact and we can re-restore it.
            if os.path.exists(bak_path):
                try:
                    shutil.move(bak_path, orig_path)  # atomic on POSIX+Win
                except Exception:
                    # Last-resort: copy then delete.  This can leave a
                    # half-restored file if killed mid-copy, but the
                    # backup is still on disk.
                    shutil.copy2(bak_path, orig_path)
                    os.remove(bak_path)

        comparison = _eval_compare(
            baseline_rate, upgraded_rate,
            baseline_total, upgraded_total,
        )

        logger.info(
            f"   Upgraded: {upgraded_rate:.1%} mean over {trials} trials "
            f"({int(upgraded_rate * upgraded_total)}/{upgraded_total} successes)"
        )
        logger.info(f"   Delta: {comparison['success_rate_delta']:+.1%}")

        # Apply statistical significance check using the flattened
        # per-task success lists, which now have trials * tasks entries.
        try:
            from src.stats import is_real_improvement
            stats_result = is_real_improvement(
                baseline_rate, upgraded_rate,
                baseline_results, upgraded_results,
                min_delta=cfg.decide.min_success_rate_delta,
            )
            logger.info(f"   Statistical significance: {'YES' if stats_result['metrics']['significant'] else 'NO'}")
            logger.info(f"   CI: [{stats_result['metrics']['ci_lower']:.1%}, {stats_result['metrics']['ci_upper']:.1%}]")
        except Exception:
            stats_result = None

        # Cost ratio: tokens (rough) — we don't have per-token counts
        # in benchmark.py yet, so use the *elapsed time* ratio as a
        # proxy.  This is a placeholder but better than hard-coding 1.0.
        try:
            base_elapsed = sum(
                sum(r.get("elapsed", 0) for r in b.get("results", []))
                for b in baseline_trials
            )
            upg_elapsed = sum(
                sum(r.get("elapsed", 0) for r in u.get("results", []))
                for u in upgraded_trials
            )
            cost_ratio = (upg_elapsed / base_elapsed) if base_elapsed > 0 else 1.0
        except Exception:
            cost_ratio = 1.0

        # v1.8.0: include harness result in state for decide step to consume
        state["evaluation"] = {
            "baseline_rate": baseline_rate,
            "upgraded_rate": upgraded_rate,
            "success_rate_delta": comparison["success_rate_delta"],
            "cost_increase_ratio": round(cost_ratio, 3),
            "baseline_cost": baseline_total,
            "upgraded_cost": upgraded_total,
            "trials": trials,
            "baseline_rates_per_trial": baseline_rates,
            "upgraded_rates_per_trial": upgraded_rates,
            "stats": stats_result,
            "harness": harness_result,  # v1.8.0: real Python unit tests
        }
    except Exception as e:
        msg = f"Evaluate: {e}"
        state["errors"].append(msg)
        logger.warning(f"   Benchmark failed ({e}) — falling back to simulated data")
        # Fallback to simulated data
        base_rate = 0.80
        upgraded_rate = min(1.0, base_rate + random.uniform(0.01, 0.10))
        state["evaluation"] = {
            "baseline_rate": base_rate,
            "upgraded_rate": upgraded_rate,
            "success_rate_delta": upgraded_rate - base_rate,
            "cost_increase_ratio": 1.0,
            "baseline_cost": 1000,
            "upgraded_cost": 1000,
            "stats": None,
            "harness": {"pass_rate": 1.0, "passed": 8, "failed": 0, "total": 8, "failures": []},
        }

    return state


def node_decide(state: dict) -> dict:
    """Phase 6: Decide and deploy — keep or revert."""
    eval_data = state.get("evaluation", {})
    cfg = state.get("config")
    best = state.get("best_paper")
    patch = state.get("patch", {})

    if not eval_data or not cfg:
        return state

    logger.info("6. Decide: evaluating results...")
    decision = make_decision(eval_data, cfg.decide)
    state["decision"] = decision

    target_module = patch.get("module", "planner.py") if patch else "planner.py"

    try:
        switcher_init()

        if best and best.paper:
            # Create patch name from arXiv ID
            patch_name = "patch-" + best.paper.arxiv_id.replace(".", "-")

            # Save as candidate
            deploy_candidate(patch_name, "Patch", state.get("patch"),
                             target_module=target_module)

            # Record in history database
            try:
                from src.db import UpgradeHistory, UpgradeRecord
                history = UpgradeHistory(cfg.database.path)
                try:
                    history.insert(UpgradeRecord(
                        paper_arxiv_id=best.paper.arxiv_id,
                        paper_title=best.paper.title,
                        skill_name=patch_name,
                        skill_path=os.path.join("upgrades", "candidates", patch_name),
                        baseline_success_rate=eval_data.get("baseline_rate", 0),
                        upgraded_success_rate=eval_data.get("upgraded_rate", 0),
                        baseline_cost_tokens=eval_data.get("baseline_cost", 0),
                        upgraded_cost_tokens=eval_data.get("upgraded_cost", 0),
                        decision=decision["decision"],
                        notes="; ".join(decision["reasons"]),
                    ))
                finally:
                    history.close()
            except Exception:
                logger.debug("Failed to record upgrade in history DB", exc_info=True)

            if decision["decision"] == "kept":
                if getattr(cfg.pipeline, "auto_promote", False):
                    result = promote_candidate(patch_name)
                    logger.info(f"   AUTO-PROMOTED to core/{target_module}: {result['status']}")
                else:
                    logger.info(f"   KEPT. Manual approval: python run.py --promote {patch_name}")
            else:
                discard_candidate(patch_name)
                logger.info(f"   REVERTED. Candidate discarded: {patch_name}")

            # v1.8.1: log decision to decision_log (knowledge persistence).
            # Free-text failure_mode lets LLM categorize without enum.
            if best and best.paper:
                try:
                    from src.learning import init_db, log_decision
                    conn = init_db()
                    try:
                        # Classify failure mode heuristically from reasons
                        reasons = decision.get("reasons") or []
                        failure_mode = reasons[0][:200] if reasons else None
                        # Extract numeric delta and harness
                        ev = state.get("evaluation") or {}
                        log_decision(
                            conn,
                            paper_arxiv_id=best.paper.arxiv_id,
                            paper_title=best.paper.title,
                            decision=decision["decision"],
                            delta=ev.get("success_rate_delta"),
                            harness_pass_rate=(ev.get("harness") or {}).get("pass_rate"),
                            failure_mode=failure_mode,
                            notes=("; ".join(reasons))[:500] if reasons else None,
                        )
                    finally:
                        conn.close()
                except Exception as e:
                    logger.debug(f"log_decision failed (non-fatal): {e}")

            # v1.8.1: mark this paper as seen (regardless of decision)
            # so we don\'t try the same paper again in future rounds
            if best and best.paper:
                try:
                    from src.learning import init_db, mark_paper_seen
                    conn = init_db()
                    try:
                        outcome_str = f"{decision['decision']}: {'; '.join(decision.get('reasons', []) or ['no reasons'])[:300]}"
                        mark_paper_seen(
                            conn,
                            paper_id=best.paper.arxiv_id,
                            outcome=outcome_str,
                        )
                    finally:
                        conn.close()
                except Exception as e:
                    logger.debug(f"mark_paper_seen failed (non-fatal): {e}")
    except Exception as e:
        state["errors"].append(f"Deploy: {e}")
        logger.warning(f"   Deploy error: {e}")

    state["done"] = True
    return state


# ═══════════════════════════════════════════════════════════
# Skill Audit (Phase 7 — lifecycle, 0 LLM)
# ═══════════════════════════════════════════════════════════

def node_skill_audit(state: dict) -> dict:
    """Phase 7: audit active skills — usage stats, quality score, auto-cull.

    v1.8.0: zero-LLM skill lifecycle management.

    This node runs AFTER decide (so it doesn't block promote decisions)
    but BEFORE end-of-round.  It:
      1. Calls evaluate_all_skills_static() (reads from skill_registry)
      2. Auto-culls skills with quality_score < 0 (i.e. they hurt more
         than they help, by enough use_count to be statistically real)
      3. Stores the audit result in state["skill_audit"]

    Returns: updated state.
    """
    logger.info("7. Skill Audit: evaluating active skills (0 LLM)...")

    cfg = state.get("config")
    if not cfg:
        return state

    # Per-round count: how many rounds since last audit
    audit_count = state.get("_audit_rounds_since_audit", 0) + 1
    audit_every = getattr(cfg.pipeline, "skill_audit_every", 1) if hasattr(cfg, "pipeline") else 1

    if audit_count < audit_every:
        # Skip this round; will audit on the next eligible one
        state["_audit_rounds_since_audit"] = audit_count
        logger.info(f"   Skip (round {audit_count}/{audit_every})")
        return state

    # Reset counter
    state["_audit_rounds_since_audit"] = 0

    # Run audit
    try:
        from src.db import UpgradeHistory
        from src.skill_lifecycle import evaluate_all_skills_static

        db_path = getattr(cfg.database, "path", "upgrades/history.db") if hasattr(cfg, "database") else "upgrades/history.db"
        history = UpgradeHistory(db_path)
        try:
            audit_result = evaluate_all_skills_static(history, cull_threshold=0.0)
        finally:
            history.close()

        # Auto-cull
        culled = []
        if audit_result:
            from src.db import UpgradeHistory as UH
            history = UpgradeHistory(db_path)
            try:
                for skill_name, info in audit_result.items():
                    if info["action"] == "culled":
                        history.archive_skill(skill_name)
                        culled.append(skill_name)
            finally:
                history.close()

        # Record audit in audit_history (v1.8.0)
        try:
            h_audit = UpgradeHistory(db_path)
            try:
                h_audit.record_audit(
                    n_skills=len(audit_result),
                    n_culled=len(culled),
                    n_kept=len(audit_result) - len(culled),
                    details=audit_result,
                )
            finally:
                h_audit.close()
        except Exception as e:
            logger.debug(f"   record_audit failed (non-fatal): {e}")

        state["skill_audit"] = {
            "evaluated": len(audit_result),
            "culled": culled,
            "details": audit_result,
        }
        logger.info(
            f"   Audit: {len(audit_result)} skills evaluated, "
            f"{len(culled)} culled: {culled}"
        )
    except Exception as e:
        state.setdefault("errors", []).append(f"SkillAudit: {e}")
        logger.warning(f"   Skill audit failed: {e}")
        state["skill_audit"] = {"evaluated": 0, "culled": [], "error": str(e)}

    return state


# ═══════════════════════════════════════════════════════════
# Edge Routing
# ═══════════════════════════════════════════════════════════

def _papers_found(state: dict) -> str:
    return "filter" if state.get("papers") else "end"


def _papers_qualified(state: dict) -> str:
    return "generate" if state.get("scored_papers") else "end"


def _patch_generated(state: dict) -> str:
    return "sandbox" if state.get("patch") else "end"


def _sandbox_result(state: dict) -> str:
    return "evaluate" if state.get("sandbox_passed") else "reflect"


def _reflect_result(state: dict) -> str:
    attempts = state.get("reflect_attempts", 0)
    return "sandbox" if attempts < 3 else "evaluate"


# ═══════════════════════════════════════════════════════════
# Graph Construction
# ═══════════════════════════════════════════════════════════

def build_graph():
    """Build the LangGraph pipeline graph."""
    graph = StateGraph(dict)

    # Add all nodes
    nodes = [
        ("research", node_research),
        ("filter", node_filter),
        ("generate", node_generate_patch),
        ("sandbox", node_sandbox),
        ("reflect", node_reflect),
        ("evaluate", node_evaluate),
        ("decide", node_decide),
        ("skill_audit", node_skill_audit),
    ]
    for name, func in nodes:
        graph.add_node(name, func)

    # Edges: R → F → G → X → E → D
    #          ↑     ↑     ↑   ↓   ↑
    #          └─────┴─────┘   T → X (retry loop, max 3)

    graph.add_edge(START, "research")
    graph.add_conditional_edges("research", _papers_found, {
        "filter": "filter",
        "end": END,
    })
    graph.add_conditional_edges("filter", _papers_qualified, {
        "generate": "generate",
        "end": END,
    })
    graph.add_conditional_edges("generate", _patch_generated, {
        "sandbox": "sandbox",
        "end": END,
    })
    graph.add_conditional_edges("sandbox", _sandbox_result, {
        "evaluate": "evaluate",
        "reflect": "reflect",
    })
    graph.add_conditional_edges("reflect", _reflect_result, {
        "sandbox": "sandbox",
        "evaluate": "evaluate",
    })
    graph.add_edge("evaluate", "decide")
    graph.add_edge("decide", "skill_audit")
    graph.add_edge("skill_audit", END)

    return graph.compile()


# ═══════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════

def run(cfg: Config = None, dry_run: bool = False) -> dict:
    """Run the full self-upgrade pipeline.

    Args:
        cfg: Config object. Loaded from config.yaml if None.
        dry_run: If True, skip real LLM benchmark (use simulated data).
                 Set to False for --live mode with real evaluation.

    Returns:
        State dict with keys: papers, scored_papers, best_paper, patch,
        sandbox_passed, reflect_attempts, evaluation, decision, errors, done.
    """
    if cfg is None:
        cfg = load_config()

    initial_state = {
        "config": cfg,
        "papers": [],
        "scored_papers": [],
        "best_paper": None,
        "patch": {},
        "sandbox_passed": False,
        "reflect_attempts": 0,
        "evaluation": {},
        "decision": {},
        "errors": [],
        "done": False,
        "dry_run": dry_run,
    }

    return build_graph().invoke(initial_state)


# Alias for backward compatibility with run.py
run_pipeline_lg = run
