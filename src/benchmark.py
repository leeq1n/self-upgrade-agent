"""Benchmark runner — evaluates agent performance on test tasks."""
import json, time, shutil, os
from typing import Dict, List
from core.agent import run as agent_run
from src.llm import chat_simple, LLMConfig
import logging

logger = logging.getLogger(__name__)


def load_tasks(path: str = "benchmarks/tasks.json") -> List[Dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_single(task: Dict, llm_config=None, verbose: bool = False,
               skill_context: str = "") -> Dict:
    """Run agent on a single benchmark task."""
    if llm_config is None:
        llm_config = LLMConfig.from_env()

    if skill_context:
        def llm_call(prompt):
            # Prepend skill context as system behavior
            sys_prompt = "You are an AI agent. " + skill_context[:500]
            return chat_simple(prompt, system=sys_prompt, config=llm_config) or ""
    else:
        def llm_call(prompt):
            return chat_simple(prompt, config=llm_config) or ""

    t0 = time.time()
    result = agent_run(task["task"], llm_call, verbose=verbose)
    result["task_id"] = task["id"]
    result["category"] = task.get("category", "")
    result["elapsed"] = round(time.time() - t0, 3)
    return result


def run_all(tasks: List[Dict] = None, llm_config=None, verbose: bool = False,
            skill_context: str = "") -> Dict:
    """Run agent on all benchmark tasks, return aggregate results."""
    if tasks is None:
        tasks = load_tasks()
    
    results = []
    for t in tasks:
        r = run_single(t, llm_config, verbose, skill_context=skill_context)
        results.append(r)
        if verbose:
            logger.info(f"  {t['id']}: steps={r['steps_planned']}, tools={r['tools_used']}, time={r['elapsed']}s")

    total = sum(1 for r in results if r.get("success", False))
    success_rate = total / len(results) if results else 0.0
    categories = {}
    for r in results:
        cat = r.get("category", "other")
        if cat not in categories:
            categories[cat] = {"total": 0, "success": 0}
        categories[cat]["total"] += 1
        if r.get("success", False):
            categories[cat]["success"] += 1

    return {
        "results": results,
        "total": len(results),
        "successes": total,
        "success_rate": success_rate,
        "categories": categories,
    }


def compare(baseline: Dict, upgraded: Dict) -> Dict:
    """Compare two benchmark runs."""
    delta = upgraded["success_rate"] - baseline["success_rate"]
    return {
        "baseline_rate": baseline["success_rate"],
        "upgraded_rate": upgraded["success_rate"],
        "success_rate_delta": delta,
        "baseline_count": baseline["total"],
        "upgraded_count": upgraded["total"],
        "improvement": delta > 0,
    }
