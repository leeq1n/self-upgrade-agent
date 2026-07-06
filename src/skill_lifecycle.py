"""Skill lifecycle management module.

Tracks skill usage, evaluates effectiveness over time, and culls
underperforming or obsolete skills to prevent context bloat.

Key capabilities:
- register/cull/archive skills
- record usage statistics
- re-evaluate skills periodically
- context budget management (select best N skills within token limit)
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def register_new_skill(skill_name, skill_path, paper_arxiv_id, paper_title, db):
    """Register a newly generated skill in the lifecycle registry."""
    db.register_skill(skill_name, skill_path, paper_arxiv_id, paper_title)
    logger.info(f"Skill registered: {skill_name}")


def record_evaluation_usage(skill_name, task_id, success, tokens, latency, db):
    """Record a benchmark trial that used this skill."""
    db.record_usage(skill_name, task_id, success, tokens, latency)


def get_skills_for_context(max_context_tokens, db):
    """Select best skills to load within a token budget.
    
    Uses utility score (use_count * avg_improvement) to prioritize.
    Returns list of skill names that fit in the budget.
    """
    skills = db.get_active_skills()
    if not skills:
        return []
    
    # Sort by utility score descending
    skills.sort(key=lambda s: (s.get("use_count", 0) or 0) * 
                abs(s.get("avg_improvement", 0) or 0), reverse=True)
    
    selected = []
    budget = max_context_tokens
    # Estimate each skill at ~500 tokens
    est_per_skill = 500
    for s in skills:
        if budget >= est_per_skill:
            selected.append(s["skill_name"])
            budget -= est_per_skill
        else:
            break
    
    return selected


def evaluate_all_skills_static(db, cull_threshold: float = 0.0):
    """v1.8.0: static skill evaluation — 0 LLM calls.

    Reads from skill_registry (use_count, avg_improvement, last_used,
    status) and computes a quality score for each active skill.

    Quality score = avg_improvement * use_count
      (high improvement + high usage = high score)
      (low improvement + low usage = low score → cull candidate)

    Args:
      db: UpgradeHistory instance.
      cull_threshold: skills with quality_score < this get culled.
                      Default 0.0 = only cull clearly bad skills.

    Returns:
      dict mapping skill_name → {quality_score, use_count,
      avg_improvement, last_used, action}
      where action is "kept" or "culled".
    """
    from datetime import datetime
    skills = db.get_active_skills()
    if not skills:
        return {}

    results = {}
    for s in skills:
        name = s.get("skill_name", "?")
        use_count = s.get("use_count", 0) or 0
        avg_imp = s.get("avg_improvement", 0.0) or 0.0
        last_used = s.get("last_used")

        quality_score = round(use_count * avg_imp, 4)

        if quality_score < cull_threshold:
            action = "culled"
        else:
            action = "kept"

        results[name] = {
            "quality_score": quality_score,
            "use_count": use_count,
            "avg_improvement": avg_imp,
            "last_used": last_used,
            "action": action,
        }
    return results


def cull_obsolete(db, max_active=10, inactivity_days=30):
    """Archive skills that are underperforming or inactive.
    
    Returns list of (skill_name, reason) tuples for archived skills.
    """
    skills = db.get_active_skills()
    archived = []
    
    for s in skills:
        name = s["skill_name"]
        use_count = s.get("use_count", 0) or 0
        avg_imp = s.get("avg_improvement", 0) or 0
        
        # Rule 1: Negative improvement (skill actively hurts)
        if avg_imp < -0.02 and use_count >= 2:
            archived.append((name, f"negative improvement: {avg_imp:.1%}"))
            db.archive_skill(name)
            continue
        
        # Rule 2: Never used and old (> inactivity days)
        last_used = s.get("last_used_at", "")
        if not last_used and use_count == 0:
            import time
            created = s.get("created_at", "")
            if created:
                try:
                    created_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S")
                    age_days = (datetime.now() - created_dt).days
                except:
                    age_days = 0
                if age_days > inactivity_days:
                    archived.append((name, f"unused for {age_days} days"))
                    db.archive_skill(name)
                    continue
        
        # Rule 3: Exceed max active skills — archive lowest utility
        # (handled separately to archive the lowest-utility ones)
    
    # If still over limit, archive lowest utility
    remaining = db.get_active_skills()
    if len(remaining) > max_active:
        remaining.sort(key=lambda s: (s.get("use_count", 0) or 0) * 
                      abs(s.get("avg_improvement", 0) or 0))
        excess = len(remaining) - max_active
        for s in remaining[:excess]:
            archived.append((s["skill_name"], "exceeded max active limit"))
            db.archive_skill(s["skill_name"])
    
    if archived:
        for name, reason in archived:
            logger.info(f"Archived skill: {name} ({reason})")
    
    return archived


def evaluate_all_skills(db, config=None):
    """Re-evaluate all active skills using the LLM benchmark."""
    skills = db.get_active_skills()
    if not skills:
        logger.info("No active skills to evaluate.")
        return {}
    
    from src.evaluate import evaluate_skill, DEFAULT_TASKS
    from src.llm import LLMConfig
    
    llm_config = LLMConfig.from_env()
    results = {}
    
    for s in skills:
        name = s["skill_name"]
        skill_path = s.get("skill_path", "")
        
        if not skill_path or not os.path.exists(skill_path):
            logger.warning(f"Skill file not found for {name}, archiving.")
            db.archive_skill(name)
            continue
        
        try:
            with open(skill_path, "r", encoding="utf-8") as f:
                skill_content = f.read()[:1000]
            
            eval_result = evaluate_skill(
                skill_context=skill_content,
                tasks=DEFAULT_TASKS[:2],
                config=config,
                llm_config=llm_config,
            )
            
            comparison = eval_result.get("comparison", {})
            delta = comparison.get("success_rate_delta", 0)
            db.update_improvement(name, delta)
            results[name] = delta
            logger.info(f"  Re-evaluated {name}: delta={delta:+.2%}")
            
        except Exception as e:
            logger.warning(f"  Failed to evaluate {name}: {e}")
    
    return results
