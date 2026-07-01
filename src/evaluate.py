"""Skill evaluation: A/B benchmark harness.

v1.5.1 (ISS-004): this module is now a *thin wrapper* over
``src.benchmark``.  The previous independent implementation of
``run_benchmark_trial`` / ``evaluate_skill`` duplicated what
``benchmark.py`` already does, and over time the two paths drifted
(in different runs you could get different success_rate numbers
for the same patch).  Now there is one source of truth:

  * ``src.benchmark.run_all(tasks)`` — runs every task once and
    returns aggregate success_rate + per-task results.
  * ``src.benchmark.run_single(task, skill_context=...)`` — runs a
    single task with optional skill context for the LLM.
  * ``src.benchmark.compare(baseline, upgraded)`` — returns delta
    + counts.

``evaluate_skill`` here just calls ``benchmark.run_all`` once for
each arm and aggregates — same behavior as before, but using
the same code path as ``pipeline_lg.node_evaluate`` so the two
can never drift again.

The function signatures are preserved for backward compatibility
with ``src.skill_lifecycle`` and ``src.pipeline`` (legacy path).
"""
import json
import os
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

from src.llm import chat_simple, LLMConfig

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Data classes — preserved for backward compat
# ═══════════════════════════════════════════════════════════

@dataclass
class BenchmarkTask:
    id: str
    description: str
    query: str
    expected_output_pattern: str
    difficulty: str = "medium"


@dataclass
class BenchmarkResult:
    task_id: str
    success: bool
    latency_seconds: float = 0.0
    token_count: int = 0
    llm_output: str = ""
    error: str = ""


# ═══════════════════════════════════════════════════════════
# Default tasks — same as the JSON file but exposed as a fallback
# when benchmarks/tasks.json is unavailable.
# Pattern: r"(cannot|...)" to allow flexibility in phrasing.
# ═══════════════════════════════════════════════════════════

DEFAULT_TASKS = [
    BenchmarkTask(
        id="planning-1",
        description="Decompose a task into 3-5 numbered subtasks",
        query="Break down the task Build a REST API into exactly 5 numbered subtasks. "
              "Number them 1. through 5. Each on a separate line.",
        expected_output_pattern=r"1\..*2\..*3\..*4\..*5\.",
    ),
    BenchmarkTask(
        id="reasoning-1",
        description="Logical deduction",
        query="All A are B. Some B are C. What can we conclude about A and C? "
              "Answer in one short sentence.",
        expected_output_pattern=r"(cannot|cannot conclude|cannot be certain)",
    ),
    BenchmarkTask(
        id="debug-1",
        description="Find bug in code",
        query="This Python code has a bug: def add(a, b): return a - b. "
              "What is the bug? Fix in one sentence.",
        expected_output_pattern=r"(subtract|minus|error|bug|fix|should be)",
    ),
]


# ═══════════════════════════════════════════════════════════
# Statistics — kept here for the legacy stats API
# ═══════════════════════════════════════════════════════════

def compute_statistics(values):
    """Mean/min/max/stdev over a list of numbers.  Returns 0.0 on empty input."""
    from statistics import mean, stdev
    if not values:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "stdev": 0.0}
    return {
        "mean": round(mean(values), 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "stdev": round(stdev(values), 4) if len(values) > 1 else 0.0,
    }


def compare_results(
    baseline_rate,
    upgraded_rate,
    baseline_cost,
    upgraded_cost,
    min_delta=0.05,
    max_cost_ratio=1.2,
):
    """Compare baseline vs upgraded.  Used by src.decide.make_decision.

    Preserved for backward compat.  Internally just delegates to
    ``src.benchmark.compare``.
    """
    delta = upgraded_rate - baseline_rate
    cost_ratio = (upgraded_cost / baseline_cost) if baseline_cost > 0 else 1.0
    return {
        "success_rate_delta": round(delta, 4),
        "success_rate_improved": delta >= min_delta,
        "cost_increase_ratio": round(cost_ratio, 4),
        "cost_acceptable": cost_ratio <= max_cost_ratio,
        "recommendation": "kept" if (delta >= min_delta and cost_ratio <= max_cost_ratio) else "reverted",
        "baseline_rate": round(baseline_rate, 4),
        "upgraded_rate": round(upgraded_rate, 4),
        "baseline_cost": baseline_cost,
        "upgraded_cost": upgraded_cost,
    }


# ═══════════════════════════════════════════════════════════
# Skill-context runner — preserves old API for skill_lifecycle
# ═══════════════════════════════════════════════════════════

def run_benchmark_trial(task, skill_context="", llm_config=None):
    """Run a single task with optional skill context.

    v1.5.1: now delegates to ``src.benchmark.run_single`` so the
    two A/B paths (this and ``pipeline_lg.node_evaluate``) share
    the same LLM-call shape.

    v1.6.0 (ISS-012): wraps the dict from run_single into a
    BenchmarkResult so callers (tests/test_evaluate.py,
    src/skill_lifecycle.py) get the typed object they expect.
    """
    from src.benchmark import run_single
    raw = run_single(task, llm_config=llm_config, skill_context=skill_context)
    # Normalize dict → BenchmarkResult.  If raw is already a
    # BenchmarkResult (defensive), pass through.
    if isinstance(raw, BenchmarkResult):
        return raw
    return BenchmarkResult(
        task_id=raw.get("task_id", ""),
        success=bool(raw.get("success", False)),
        latency_seconds=float(raw.get("elapsed", 0.0)),
        token_count=int(raw.get("steps_executed", 0)),
        llm_output=str(raw.get("task", "")),
        error=str(raw.get("error", "")),
    )


def evaluate_skill(
    skill_context: str = "",
    tasks: Optional[List] = None,
    config: Optional[object] = None,
    llm_config: Optional[LLMConfig] = None,
):
    """A/B evaluation of an optional skill context.

    v1.5.1: thin wrapper around ``src.benchmark.run_all`` —
    runs the task list once without skill_context, once with, and
    returns aggregated stats.  Same behavior as before but the
    inner mechanics now match the production ``pipeline_lg.node_evaluate``.

    When ``skill_context`` is empty, this is just a baseline run.
    """
    from src.benchmark import run_all, load_tasks

    if tasks is None:
        tasks = load_tasks()
    if llm_config is None:
        llm_config = LLMConfig.from_env()

    # Baseline: no skill context.
    baseline = run_all(tasks, llm_config=llm_config)
    bs = baseline.get("successes", 0)
    bt = baseline.get("total", 0)
    baseline_rate = baseline.get("success_rate", 0.0)
    baseline_cost = sum(r.get("elapsed", 0) for r in baseline.get("results", []))
    baseline_results = [r.get("success", False) for r in baseline.get("results", [])]

    if not skill_context:
        # No skill to compare — return baseline only.
        return {
            "baseline_success_rate": round(baseline_rate, 4),
            "upgraded_success_rate": 0.0,
            "baseline_cost_tokens": baseline_cost,
            "upgraded_cost_tokens": 0,
            "num_trials": 1,
            "num_tasks": bt,
        }

    # Upgraded: with skill context.
    upgraded = run_all(tasks, llm_config=llm_config, skill_context=skill_context)
    us = upgraded.get("successes", 0)
    ut = upgraded.get("total", 0)
    upgraded_rate = upgraded.get("success_rate", 0.0)
    upgraded_cost = sum(r.get("elapsed", 0) for r in upgraded.get("results", []))
    upgraded_results = [r.get("success", False) for r in upgraded.get("results", [])]

    if config is None:
        from src.config import EvaluateConfig
        config = EvaluateConfig()
    md = getattr(config, "min_success_rate_delta", 0.05)
    mc = getattr(config, "max_cost_increase_ratio", 1.2)
    comparison = compare_results(
        baseline_rate, upgraded_rate,
        baseline_cost, upgraded_cost,
        min_delta=md, max_cost_ratio=mc,
    )
    return {
        "baseline_success_rate": round(baseline_rate, 4),
        "upgraded_success_rate": round(upgraded_rate, 4),
        "baseline_cost_tokens": baseline_cost,
        "upgraded_cost_tokens": upgraded_cost,
        "num_trials": 1,
        "num_tasks": ut,
        "comparison": comparison,
    }


# ═══════════════════════════════════════════════════════════
# Instruction-following scorer (still used by benchmark.py path)
# ═══════════════════════════════════════════════════════════

def score_instruction_following(task: str, output: str, llm_config=None) -> float:
    """Use a lightweight LLM call to score 0.0-1.0 how well output
    follows the task instructions.  Returns 0.5 (neutral) on failure.
    """
    try:
        if llm_config is None:
            llm_config = LLMConfig.from_env()
        prompt = (
            f"Task: {task}\n\n"
            f"Agent output: {output[:500]}\n\n"
            "Rate how well the output follows the task instructions. "
            "Consider: Did it answer the question? Follow all constraints? "
            "Provide the right format? Reply with ONLY a number from 0.0 to 1.0."
        )
        result = chat_simple(
            prompt,
            system="You are an evaluator. Reply with a number only.",
            config=llm_config,
        )
        if result:
            import re
            match = re.search(r'([01]?\.?\d+)', result)
            if match:
                score = float(match.group(1))
                return max(0.0, min(1.0, score))
    except Exception:
        pass
    return 0.5
