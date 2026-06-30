import re, time
from dataclasses import dataclass
from typing import List, Dict, Optional
from statistics import mean, stdev
from src.llm import chat_simple, LLMConfig

logger = __import__("logging").getLogger(__name__)

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

# Pattern: match 1. through 5. on separate lines
_P1 = chr(92) + "."
DEFAULT_TASKS = [
    BenchmarkTask(id="planning-1",
        query="Break down the task Build a REST API into exactly 5 numbered subtasks. Number them 1. through 5. Each on a separate line.",
        expected_output_pattern="1" + _P1 + ".*2" + _P1 + ".*3" + _P1 + ".*4" + _P1 + ".*5" + _P1,
        description="Break task into subtasks", difficulty="medium"),
    BenchmarkTask(id="reasoning-1", description="Logical deduction",
        query="All A are B. Some B are C. What can we conclude about A and C? Answer in one short sentence.",
        expected_output_pattern=r"(cannot|cannot conclude|cannot be certain)", difficulty="medium"),
    BenchmarkTask(id="debug-1", description="Find bug in code",
        query="This Python code has a bug: def add(a, b): return a - b. What is the bug? Fix in one sentence.",
        expected_output_pattern=r"(subtract|minus|error|bug|fix|should be)", difficulty="easy"),
]

def compute_statistics(values):
    if not values:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "stdev": 0.0}
    return {"mean": round(mean(values), 4), "min": round(min(values), 4),
            "max": round(max(values), 4),
            "stdev": round(stdev(values), 4) if len(values) > 1 else 0.0}

def compare_results(baseline_rate, upgraded_rate, baseline_cost, upgraded_cost, min_delta=0.05, max_cost_ratio=1.2):
    d = upgraded_rate - baseline_rate
    ok = d >= min_delta
    cr = upgraded_cost / baseline_cost if baseline_cost > 0 else (2.0 if upgraded_cost > 0 else 1.0)
    co = cr <= max_cost_ratio
    return {"success_rate_delta": round(d, 4), "success_rate_improved": ok,
            "cost_increase_ratio": round(cr, 4), "cost_acceptable": co,
            "recommendation": "kept" if (ok and co) else "reverted",
            "baseline_rate": round(baseline_rate, 4),
            "upgraded_rate": round(upgraded_rate, 4),
            "baseline_cost": baseline_cost, "upgraded_cost": upgraded_cost}

def run_benchmark_trial(task, skill_context="", llm_config=None):
    s = "You are an AI being evaluated. Answer the question precisely."
    if skill_context:
        s += " Additional context: " + skill_context
    t0 = time.time()
    c = chat_simple(prompt=task.query, system=s, config=llm_config)
    elapsed = time.time() - t0
    c = c or ""
    ok = bool(re.search(task.expected_output_pattern, c, re.IGNORECASE | re.DOTALL))
    return BenchmarkResult(task_id=task.id, success=ok, latency_seconds=round(elapsed, 2), token_count=len(c)//4, llm_output=c[:200])

def evaluate_skill(skill_context="", tasks=None, config=None, llm_config=None):
    if tasks is None: tasks = DEFAULT_TASKS
    if config is None:
        from src.config import EvaluateConfig
        config = EvaluateConfig()
    if llm_config is None:
        llm_config = LLMConfig.from_env()
    n = config.trials_per_test
    if not skill_context:
        br = []
        for t in tasks:
            for _ in range(n):
                br.append(run_benchmark_trial(t, llm_config=llm_config))
        sc = sum(1 for r in br if r.success)
        return {"baseline_success_rate": round(sc / max(len(br), 1), 4),
                "upgraded_success_rate": 0.0,
                "baseline_cost_tokens": sum(r.token_count for r in br),
                "upgraded_cost_tokens": 0, "num_trials": len(br), "num_tasks": len(tasks)}
    br = []; ur = []
    for t in tasks:
        for _ in range(n):
            br.append(run_benchmark_trial(t, llm_config=llm_config))
            ur.append(run_benchmark_trial(t, skill_context=skill_context, llm_config=llm_config))
    bs = sum(1 for r in br if r.success) / max(len(br), 1)
    us = sum(1 for r in ur if r.success) / max(len(ur), 1)
    bc = sum(r.token_count for r in br)
    uc = sum(r.token_count for r in ur)
    md = getattr(config, 'min_success_rate_delta', 0.05)
    mc = getattr(config, 'max_cost_increase_ratio', 1.2)
    cmp = compare_results(bs, us, bc, uc, min_delta=md, max_cost_ratio=mc)
    return {"baseline_success_rate": round(bs, 4),
            "upgraded_success_rate": round(us, 4),
            "baseline_cost_tokens": bc, "upgraded_cost_tokens": uc,
            "num_trials": len(br), "num_tasks": len(tasks), "comparison": cmp}