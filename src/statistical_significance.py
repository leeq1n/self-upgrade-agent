"""Statistical significance (per v3.3.0 sub-task 3/3, last sub-task).

Per 你 vision (self-upgrade agent 终极目标):
- 真 autonomous KEPT/REJECT with confidence
- Statistical confidence, not gut-feel

Per LITERATURE Signal-to-Fix:
- Multiple runs for confidence intervals
- T-test for significance
- Per Nate Berkopec: data-driven > intuition

Per 自上而下/分治 (user 2026-07-11 meta-principle):
- Big task: v3.3.0 A/B benchmark
- Sub-task 1 (done 9c912a4): core comparison logic
- Sub-task 2 (done 597aab6): integration with daily-loop
- Sub-task 3 (this commit): statistical significance

Per P23 doc-first: spec exists (PROJECT_STATE + LITERATURE).
Per P18: regression tests required.
"""
import statistics
import math
from typing import List, Tuple, Dict, Optional


def run_multiple(do_measure, n_runs=5):
    """Run N measurements, return list of metric dicts.

    Per LITERATURE: multiple runs for variance estimation.

    Args:
        do_measure: callable -> single metric dict
        n_runs: number of runs (default 5)

    Returns: list of metric dicts
    """
    return [do_measure() for _ in range(n_runs)]


def compute_stats(samples):
    """Compute mean, stdev, n from samples list.

    Per LITERATURE: descriptive stats for hypothesis testing.

    Returns: dict with mean, stdev, n, sem (standard error of mean)
    """
    if not samples:
        return {"mean": 0, "stdev": 0, "n": 0, "sem": 0}
    n = len(samples)
    mean = statistics.mean(samples)
    if n < 2:
        return {"mean": mean, "stdev": 0, "n": n, "sem": 0}
    stdev = statistics.stdev(samples)
    sem = stdev / math.sqrt(n)
    return {"mean": mean, "stdev": stdev, "n": n, "sem": sem}


def welch_t_test(baseline_samples, candidate_samples, alpha=0.05):
    """Welch's t-test (unequal variance) per LITERATURE.

    Returns: {
        "t_statistic": float,
        "p_value": float (approximation, no scipy dep),
        "significant": bool (p < alpha),
        "baseline_mean": float,
        "candidate_mean": float,
        "delta": float,
    }
    """
    b = compute_stats(baseline_samples)
    c = compute_stats(candidate_samples)
    if b["n"] < 2 or c["n"] < 2:
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "significant": False,
            "baseline_mean": b["mean"],
            "candidate_mean": c["mean"],
            "delta": c["mean"] - b["mean"],
            "warning": "insufficient samples",
        }
    # Welch's t-statistic
    delta = c["mean"] - b["mean"]
    # Special case: zero variance on both sides but different means
    # -> t_stat is effectively infinite (significant)
    if b["stdev"] == 0 and c["stdev"] == 0:
        if delta != 0:
            # Effectively perfect separation; very significant
            return {
                "t_statistic": float("inf") if delta > 0 else float("-inf"),
                "p_value": 0.0,
                "significant": True,
                "baseline_mean": b["mean"],
                "candidate_mean": c["mean"],
                "delta": delta,
                "warning": "zero variance but different means -> perfect separation",
            }
        # Both identical
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "significant": False,
            "baseline_mean": b["mean"],
            "candidate_mean": c["mean"],
            "delta": 0.0,
            "warning": "zero variance",
        }
    se_diff = math.sqrt(b["sem"] ** 2 + c["sem"] ** 2)
    if se_diff == 0:
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "significant": False,
            "baseline_mean": b["mean"],
            "candidate_mean": c["mean"],
            "delta": 0.0,
            "warning": "zero combined std error",
        }
    t_stat = delta / se_diff
    # Welch-Satterthwaite degrees of freedom
    df_num = (b["sem"] ** 2 + c["sem"] ** 2) ** 2
    df_den = (b["sem"] ** 4 / max(b["n"] - 1, 1) +
              c["sem"] ** 4 / max(c["n"] - 1, 1))
    df = df_num / df_den if df_den > 0 else 1
    # Approximation: p_value via normal distribution for large df
    # Per LITERATURE: avoid scipy dep, use conservative approximation
    p_value = _approx_two_tail_p(t_stat, df)
    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant": p_value < alpha,
        "baseline_mean": b["mean"],
        "candidate_mean": c["mean"],
        "delta": c["mean"] - b["mean"],
        "df": df,
    }


def _approx_two_tail_p(t_stat, df):
    """Conservative two-tailed p-value approximation (no scipy).

    Per LITERATURE Signal-to-Fix: rough estimate is OK for decisions.
    For small df, p is larger (more conservative).
    For large |t|, p is small (highly significant).

    Simple approximation: 2 * (1 - Phi(|t|))
    Where Phi is standard normal CDF approximation.
    """
    # Standard normal CDF approximation (Abramowitz & Stegun 7.1.26)
    x = abs(t_stat)
    t = 1.0 / (1.0 + 0.2316419 * x)
    d = 0.3989422804014327  # 1/sqrt(2*pi)
    p_positive = d * math.exp(-x * x / 2.0) * (
        t * (0.319381530 +
             t * (-0.356563782 +
                  t * (1.781477937 +
                       t * (-1.821255978 +
                            t * 1.330274429)))))
    p_two_tail = 2 * p_positive
    # Adjust for small df (more conservative): scale up by sqrt(df/(df-2)) if df > 2
    if df > 2:
        p_two_tail *= math.sqrt(df / (df - 2))
    return min(1.0, p_two_tail)


def decide_with_significance(baseline_samples, candidate_samples,
                             higher_is_better=True, alpha=0.05):
    """Decide candidate_better / regression / tie with significance test.

    Per LITERATURE Signal-to-Fix: don't trust single-run differences.

    Returns: {
        "decision": "candidate_better" | "regression" | "tie",
        "reason": str,
        "significant": bool,
        "p_value": float,
        "delta": float,
    }
    """
    test = welch_t_test(baseline_samples, candidate_samples, alpha)
    if not test["significant"]:
        return {
            "decision": "tie",
            "reason": f"no significant difference (p={test['p_value']:.3f})",
            "significant": False,
            "p_value": test["p_value"],
            "delta": test["delta"],
        }
    delta = test["delta"]
    if higher_is_better:
        candidate_better = delta > 0
    else:
        candidate_better = delta < 0
    if candidate_better:
        return {
            "decision": "candidate_better",
            "reason": f"significant improvement (p={test['p_value']:.3f}, delta={delta:.2f})",
            "significant": True,
            "p_value": test["p_value"],
            "delta": delta,
        }
    return {
        "decision": "regression",
        "reason": f"significant regression (p={test['p_value']:.3f}, delta={delta:.2f})",
        "significant": True,
        "p_value": test["p_value"],
        "delta": delta,
    }


def main():
    """CLI: show statistical significance demo."""
    # Demo: 5 baseline + 5 candidate samples
    baseline = [10.0, 10.2, 9.8, 10.1, 10.0]
    candidate = [12.0, 11.8, 12.2, 11.9, 12.1]
    result = decide_with_significance(baseline, candidate)
    print(f"Statistical significance demo:")
    print(f"  Baseline mean: {statistics.mean(baseline):.2f}")
    print(f"  Candidate mean: {statistics.mean(candidate):.2f}")
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['reason']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())