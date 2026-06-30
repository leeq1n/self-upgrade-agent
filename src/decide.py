"""Decision module: evaluate benchmark results and decide keep or revert.

The decision logic uses configurable thresholds:
- Keep: success rate improvement >= min_delta AND cost increase <= max_ratio.
- Revert: otherwise. Auto-revert on regression (worse + more expensive).
"""
import os
import shutil
from typing import Dict, Optional
from src.config import DecideConfig


def make_decision(eval_data: Dict, config: DecideConfig) -> Dict:
    """Decide whether to keep or revert an upgrade based on evaluation data.

    Args:
        eval_data: Output from evaluate.compare_results().
        config: DecideConfig with thresholds.

    Returns:
        Dict with 'decision' (keep/revert), 'reasons' (list of strings),
        and 'metrics' (summary dict).
    """
    reasons = []

    delta = eval_data.get("success_rate_delta", 0.0)
    improved = eval_data.get("success_rate_improved", False)
    cost_ratio = eval_data.get("cost_increase_ratio", 1.0)
    cost_ok = eval_data.get("cost_acceptable", True)

    # Check for regression (worse performance at higher cost)
    if delta < 0 and cost_ratio > 1.0:
        reasons.append(
            f"REGRESSION: performance dropped by {abs(delta):.2%} "
            f"while cost increased {cost_ratio:.2f}x"
        )
        return {
            "decision": "reverted",
            "reasons": reasons,
            "metrics": {
                "success_rate_delta": delta,
                "cost_increase_ratio": cost_ratio,
                "baseline_rate": eval_data.get("baseline_rate", 0),
                "upgraded_rate": eval_data.get("upgraded_rate", 0),
            },
        }

    if improved:
        reasons.append(
            f"Success rate improved by {delta:.2%} "
            f"(threshold: {config.min_success_rate_delta:.2%})"
        )
    else:
        reasons.append(
            f"Success rate delta {delta:.2%} "
            f"below minimum threshold {config.min_success_rate_delta:.2%}"
        )

    if cost_ok:
        reasons.append(
            f"Cost increase {cost_ratio:.2f}x "
            f"within limit (max: {config.max_cost_increase_ratio:.2f}x)"
        )
    else:
        reasons.append(
            f"Cost increase {cost_ratio:.2f}x "
            f"exceeds limit (max: {config.max_cost_increase_ratio:.2f}x)"
        )

    decision = "kept" if (improved and cost_ok) else "reverted"

    return {
        "decision": decision,
        "reasons": reasons,
        "metrics": {
            "success_rate_delta": delta,
            "cost_increase_ratio": cost_ratio,
            "baseline_rate": eval_data.get("baseline_rate", 0),
            "upgraded_rate": eval_data.get("upgraded_rate", 0),
        },
    }


def rollback_skill(
    skill_path: str,
    backup_path: Optional[str] = None,
) -> bool:
    """Rollback a skill change — either restore from backup or delete file.

    Args:
        skill_path: Path to the SKILL.md file.
        backup_path: Optional path to a backup file to restore from.

    Returns:
        True if rollback succeeded, False otherwise.
    """
    try:
        if backup_path and os.path.exists(backup_path):
            os.makedirs(os.path.dirname(skill_path), exist_ok=True)
            shutil.copy2(backup_path, skill_path)
            return True
        elif os.path.exists(skill_path):
            os.remove(skill_path)
            return True
        return False
    except (OSError, PermissionError):
        return False
