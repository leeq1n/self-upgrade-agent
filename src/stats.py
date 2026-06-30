"""Statistical significance testing for benchmark comparisons.

[FROZEN v1.1.0] — stable bootstrap logic, tested, do not modify.

Provides bootstrap confidence intervals and significance tests to distinguish
real improvements from random variation in LLM benchmark results.
"""
import random
from typing import Dict, List


def bootstrap_test(
    baseline_results: List[bool],
    upgraded_results: List[bool],
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
) -> Dict:
    """Bootstrap test for difference in success rates.

    Args:
        baseline_results: List of bool results (True=success) for baseline.
        upgraded_results: List of bool results for upgraded agent.
        n_bootstrap: Number of bootstrap resamples.
        confidence: Confidence level (0.0-1.0, default 0.95).

    Returns:
        Dict with:
        - baseline_rate: mean baseline success rate
        - upgraded_rate: mean upgraded success rate
        - mean_delta: mean improvement (upgraded - baseline)
        - ci_lower: lower bound of confidence interval
        - ci_upper: upper bound of confidence interval
        - p_value: approximate p-value for H0: delta <= 0
        - significant: True if ci_lower > 0
        - n_baseline: number of baseline trials
        - n_upgraded: number of upgraded trials
    """
    if not baseline_results or not upgraded_results:
        return {
            "baseline_rate": 0.0,
            "upgraded_rate": 0.0,
            "mean_delta": 0.0,
            "ci_lower": 0.0,
            "ci_upper": 0.0,
            "p_value": 1.0,
            "significant": False,
            "n_baseline": len(baseline_results),
            "n_upgraded": len(upgraded_results),
        }

    n_base = len(baseline_results)
    n_up = len(upgraded_results)

    # Bootstrap
    deltas = []
    rng = random.Random(42)  # Deterministic seed for reproducibility
    for _ in range(n_bootstrap):
        base_sample = [rng.choice(baseline_results) for _ in range(n_base)]
        up_sample = [rng.choice(upgraded_results) for _ in range(n_up)]
        base_rate = sum(base_sample) / n_base
        up_rate = sum(up_sample) / n_up
        deltas.append(up_rate - base_rate)

    deltas.sort()
    mean_delta = sum(deltas) / len(deltas)

    # Confidence interval
    alpha = (1.0 - confidence) / 2.0
    lower_idx = int(alpha * n_bootstrap)
    upper_idx = int((1.0 - alpha) * n_bootstrap)
    ci_lower = deltas[max(0, lower_idx)]
    ci_upper = deltas[min(n_bootstrap - 1, upper_idx)]

    # Approximate p-value: proportion of bootstrap samples where delta <= 0
    p_value = sum(1 for d in deltas if d <= 0) / n_bootstrap

    baseline_rate = sum(baseline_results) / n_base
    upgraded_rate = sum(upgraded_results) / n_up

    return {
        "baseline_rate": round(baseline_rate, 4),
        "upgraded_rate": round(upgraded_rate, 4),
        "mean_delta": round(mean_delta, 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "p_value": round(p_value, 4),
        "significant": ci_lower > 0,
        "n_baseline": n_base,
        "n_upgraded": n_up,
    }


def is_real_improvement(
    baseline_rate: float,
    upgraded_rate: float,
    baseline_results: List[bool],
    upgraded_results: List[bool],
    min_delta: float = 0.05,
    confidence: float = 0.95,
) -> Dict:
    """Combined check: is the improvement both large enough AND statistically significant?

    Returns dict with decision ('keep'/'revert') and detailed metrics.
    """
    bootstrap = bootstrap_test(baseline_results, upgraded_results, confidence=confidence)
    delta = upgraded_rate - baseline_rate

    reasons = []

    if delta >= min_delta:
        reasons.append(f"Delta {delta:.2%} meets threshold ({min_delta:.2%})")
    else:
        reasons.append(f"Delta {delta:.2%} below threshold ({min_delta:.2%})")

    if bootstrap["significant"]:
        reasons.append(
            f"Statistically significant: CI [{bootstrap['ci_lower']:.2%}, "
            f"{bootstrap['ci_upper']:.2%}], p={bootstrap['p_value']:.3f}"
        )
    else:
        reasons.append(
            f"NOT significant: CI [{bootstrap['ci_lower']:.2%}, "
            f"{bootstrap['ci_upper']:.2%}], p={bootstrap['p_value']:.3f}"
        )

    decision = "kept" if (delta >= min_delta and bootstrap["significant"]) else "reverted"

    return {
        "decision": decision,
        "reasons": reasons,
        "metrics": {
            "success_rate_delta": round(delta, 4),
            "baseline_rate": round(baseline_rate, 4),
            "upgraded_rate": round(upgraded_rate, 4),
            "ci_lower": bootstrap["ci_lower"],
            "ci_upper": bootstrap["ci_upper"],
            "p_value": bootstrap["p_value"],
            "significant": bootstrap["significant"],
        },
    }
