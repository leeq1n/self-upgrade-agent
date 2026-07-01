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


def run_single(task, llm_config=None, verbose: bool = False,
               skill_context: str = "") -> Dict:
    """Run agent on a single benchmark task.

    v1.6.0 (ISS-012 fix): accept either dict (legacy benchmarks/tasks.json)
    or BenchmarkTask dataclass (legacy src/evaluate.py).  The dataclass
    has ``query`` (the prompt text); dicts use key ``task``.
    """
    # Normalize dict vs dataclass into the prompt + id + category
    if hasattr(task, "query"):
        # BenchmarkTask dataclass
        prompt_text = task.query
        task_id = task.id
        category = ""
    else:
        # plain dict (benchmarks/tasks.json)
        prompt_text = task["task"]
        task_id = task["id"]
        category = task.get("category", "")

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
    result = agent_run(prompt_text, llm_call, verbose=verbose)
    result["task_id"] = task_id
    result["category"] = category
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


def score_instruction_following(task: str, output: str, llm_config=None) -> float:
    """Score how well the agent output follows the task instructions.

    Uses a lightweight LLM call to evaluate if all constraints in the task
    were satisfied by the output. Returns a score from 0.0 (completely failed)
    to 1.0 (perfectly followed).

    Args:
        task: The benchmark task description.
        output: The agent's final response.
        llm_config: LLM configuration (uses env if None).

    Returns:
        Float score 0.0-1.0, or 0.5 on evaluation failure (neutral default).
    """
    try:
        from src.llm import chat_simple, LLMConfig
        if llm_config is None:
            llm_config = LLMConfig.from_env()

        prompt = (
            f"Task: {task}\n\n"
            f"Agent output: {output[:500]}\n\n"
            "Rate how well the output follows the task instructions. "
            "Consider: Did it answer the question? Follow all constraints? "
            "Provide the right format? Reply with ONLY a number from 0.0 to 1.0."
        )
        result = chat_simple(prompt, system="You are an evaluator. Reply with a number only.",
                            config=llm_config)
        if result:
            # Extract number from response
            import re
            match = re.search(r'([01]?\.?\d+)', result)
            if match:
                score = float(match.group(1))
                return max(0.0, min(1.0, score))
    except Exception:
        pass
    return 0.5  # Neutral default
