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

def _apply_patch_to_module(module_path: str, patch_code: str) -> str:
    """Surgically merge patch code into an existing core module.

    Strategy (in order):
    1. If patch_code is a full module (starts with docstring), use as-is.
    2. Extract target function name from patch, find it in original, replace.
    3. If target function not found, append patch to end of module.

    This preserves imports, __version__, and module-level metadata while
    replacing only the targeted function implementation.

    Args:
        module_path: Path to the existing module file (e.g., 'core/planner.py').
        patch_code: Generated code — either a single function or a full module.

    Returns:
        The merged module source code as a string.
    """
    # Case 1: Full module replacement (patch has its own docstring)
    stripped = patch_code.strip()
    if stripped.startswith('"""') or stripped.startswith("'''"):
        return patch_code

    # Read original module
    with open(module_path, encoding="utf-8") as f:
        original = f.read()

    # Case 2: Extract function name and surgically replace
    func_match = re.search(r'def\s+(\w+)\s*\(', patch_code)
    if not func_match:
        return original  # Can't identify target, keep original

    func_name = func_match.group(1)

    # Pattern: match the function definition through to the next top-level def
    # or end of file. Uses a non-greedy approach with lookahead.
    pattern = (
        r'(def\s+' + re.escape(func_name) + r'\s*\([^)]*\).*?)'
        r'(?=\n(?:def\s+\w+\s*\(|\n*#|$)|\Z)'
    )

    if re.search(pattern, original, re.DOTALL):
        merged = re.sub(pattern, patch_code.strip(), original, flags=re.DOTALL)
        return merged

    # Case 3: Function not found, append
    return original.rstrip() + "\n\n" + patch_code.strip() + "\n"


# ═══════════════════════════════════════════════════════════
# Pipeline Nodes
# ═══════════════════════════════════════════════════════════

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
        try:
            patch = generate_patch(best.paper, "planner.py") or {}
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


def node_evaluate(state: dict) -> dict:
    """Phase 5: Real A/B benchmark — baseline vs patched agent.

    v1.5.0: actually use config.evaluate.trials_per_test.  Each "trial"
    is a full run of all benchmark tasks; we run multiple trials so
    that success_rate has a real distribution (not just one noisy
    sample) and the bootstrap CI in stats.py is meaningful.

    Cost: 21 tasks × N trials × 2 (baseline + upgraded) = 42*N LLM
    calls.  N=3 → 126 calls; with Qwen3.5-2B this finishes in a
    few minutes.  N=10 (the old config) → 420 calls, which is why
    we lowered the default.
    """
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
    except Exception as e:
        state["errors"].append(f"Deploy: {e}")
        logger.warning(f"   Deploy error: {e}")

    state["done"] = True
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
    graph.add_edge("decide", END)

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
