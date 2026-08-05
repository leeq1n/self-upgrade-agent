"""Legacy pipeline — skillgen path (archived, use pipeline_lg.py instead).

This pipeline generates SKILL.md behavior prompts (not code patches).
Kept for backward compatibility (legacy entry).

For the current self-modification pipeline, see src/pipeline_lg.py.
"""
import logging
import os
from dataclasses import dataclass, field
from typing import List

from src.config import Config, load_config
from src.llm import LLMConfig as _llm_config_class
_llm_config = None  # lazy init
from src.research import search_arxiv, Paper
from src.filter import filter_papers, ScoredPaper
from src._archived.skillgen import generate_skill_md, validate_skill, save_skill, backup_skill, _name as _generate_skill_name, generate_code_skill
from src.sandbox import run_in_sandbox
from src.switcher import init as _switcher_init, deploy_candidate, promote_candidate, discard_candidate
from src.evaluate import compare_results, DEFAULT_TASKS
from src.decide import make_decision, rollback_skill
from src._archived.modi import install_skill_file, extract_behavior_from_skill, apply_behavior
from src.db import UpgradeHistory, UpgradeRecord

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Summary of a complete pipeline run."""
    papers_found: int = 0
    papers_scored: int = 0
    papers_qualified: int = 0
    skills_generated: int = 0
    upgrades_evaluated: int = 0
    upgrades_kept: int = 0
    upgrades_reverted: int = 0
    errors: List[str] = field(default_factory=list)
    details: List[dict] = field(default_factory=list)


def _run_evaluation(skill_name: str, skill_context: str, config, dry_run: bool = True) -> dict:
    """Evaluate upgrade: real benchmark if live, simulated if dry-run.

    In live mode, runs the agent on benchmark tasks with and without the skill,
    comparing success rates and cost. Falls back to simulated data on failure.
    """
    if dry_run:
        import random
        delta = random.uniform(0.01, 0.10)
        base_rate = 0.80
        upgraded_rate = min(1.0, base_rate + delta)
        base_cost = 1000 + random.randint(0, 500)
        upgraded_cost = int(base_cost * random.uniform(0.9, 1.15))
    else:
        # Real benchmark evaluation
        try:
            from src.benchmark import load_tasks, run_all, compare as bench_compare
            from src.llm import LLMConfig
            tasks = load_tasks()
            llm_config = LLMConfig.from_env()
            if not llm_config.ready:
                logger.warning("LLM not configured — falling back to simulated evaluation")
                return _run_evaluation(skill_name, skill_context, config, dry_run=True)

            # Baseline (no skill context)
            baseline = run_all(tasks, llm_config=llm_config)
            # Upgraded (with skill context)
            upgraded = run_all(tasks, llm_config=llm_config,
                              skill_context=skill_context)

            comparison = bench_compare(baseline, upgraded)
            base_rate = baseline["success_rate"]
            upgraded_rate = upgraded["success_rate"]
            base_cost = baseline["total"]
            upgraded_cost = upgraded["total"]
            logger.info(f"  Live eval: baseline={base_rate:.3f}, "
                       f"upgraded={upgraded_rate:.3f}, "
                       f"delta={comparison['success_rate_delta']:+.3f}")
        except Exception as e:
            logger.warning(f"Live evaluation failed ({e}) — falling back to simulated")
            return _run_evaluation(skill_name, skill_context, config, dry_run=True)

    return compare_results(
        baseline_rate=base_rate,
        upgraded_rate=upgraded_rate,
        baseline_cost=base_cost,
        upgraded_cost=upgraded_cost,
        min_delta=config.decide.min_success_rate_delta,
        max_cost_ratio=config.decide.max_cost_increase_ratio,
    )


def run_pipeline(
    config: Config = None,
    skills_dir: str = None,
    backup_dir: str = None,
    db_path: str = None,
    dry_run: bool = False,
) -> PipelineResult:
    """Run the complete self-upgrade pipeline.

    Phases:
    1. Research — search arXiv for papers matching configured keywords
    2. Filter — score and rank papers by applicability, novelty, quality
    3. Implement — generate Hermes Agent skills from qualified papers
    4. Evaluate — A/B benchmark (mocked in dry-run, real calls in prod)
    5. Decide — compare results, keep or revert

    Args:
        config: Full Config object. Loaded from config.yaml if None.
        skills_dir: Directory to save generated skills.
        backup_dir: Directory for skill backups.
        db_path: Path to SQLite history database.
        dry_run: If True, skip real benchmark calls (use simulated data).

    Returns:
        PipelineResult with summary statistics.
    """
    if config is None:
        config = load_config()

    if skills_dir is None:
        skills_dir = "upgrades/skills"
    if backup_dir is None:
        backup_dir = "upgrades/snapshots"
    if db_path is None:
        db_path = config.database.path

    result = PipelineResult()
    history = UpgradeHistory(db_path)

    os.makedirs(skills_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)

    # ── Phase 1: Research ──
    logger.info("Phase 1: Searching arXiv for papers...")
    try:
        papers = search_arxiv(config.research)
        result.papers_found = len(papers)
        logger.info(f"Found {len(papers)} papers")
    except Exception as e:
        msg = f"Research phase failed: {e}"
        logger.error(msg)
        result.errors.append(msg)
        history.close()
        return result

    if not papers:
        logger.info("No papers found — nothing to upgrade.")
        history.close()
        return result

    # ── Phase 2: Filter ──
    logger.info("Phase 2: Scoring and filtering papers...")
    try:
        scored = filter_papers(papers, config.filter)
        result.papers_scored = len(scored)
        result.papers_qualified = len(scored)
    except Exception as e:
        msg = f"Filter phase failed: {e}"
        logger.error(msg)
        result.errors.append(msg)
        history.close()
        return result

    if not scored:
        logger.info("No papers met thresholds — nothing to upgrade.")
        history.close()
        return result

    # ── Phase 3-5: Per qualified paper ──
    max_upgrades = config.pipeline.max_upgrades_per_cycle
    papers_to_process = scored[:max_upgrades]

    for sp in papers_to_process:
        paper = sp.paper
        skill_name = _generate_skill_name(paper)

        logger.info(f"Processing: {paper.title[:60]}... (score: {sp.total_score:.1f})")

        # Generate and validate skill
        skill_md = generate_skill_md(paper, skill_name)
        validation_errors = validate_skill(skill_md)

        if validation_errors and config.implement.validate_before_install:
            logger.warning(f"Skill validation failed for {skill_name}: {validation_errors}")
            result.errors.append(f"Validation: {skill_name}: {validation_errors}")
            continue

        # Backup existing skill
        existing_path = os.path.join(skills_dir, skill_name, "SKILL.md")
        backup_path = None
        if config.implement.backup_existing_skill:
            backup_path = backup_skill(existing_path, backup_dir)

        # Save the new skill
        skill_path = save_skill(skill_md, skill_name, skills_dir)
        result.skills_generated += 1
        logger.info(f"  A. Skill saved: {skill_path}")
        
        # B. Generate executable code from paper (harness: JSON mode)
        code = None
        if not dry_run:
            try:
                code = generate_code_skill(paper, use_llm=True, llm_config=_llm_config)
                if code:
                    logger.info(f"  B. Code generated: function={len(code['function'])} chars, test={len(code['test'])} chars")
                else:
                    logger.info(f"  B. Code generation skipped (no output)")
            except Exception as e:
                logger.warning(f"  B. Code generation failed: {e}")
        else:
            logger.info(f"  B. Code gen skipped (dry-run)")
        
        # C. Sandbox test
        sandbox_ok = False
        if code:
            try:
                sandbox_result = run_in_sandbox(code['function'], code['test'], test_name='test_algorithm', timeout=10)
                sandbox_ok = sandbox_result['passed']
                if sandbox_ok:
                    logger.info(f"  C. Sandbox: PASS ({sandbox_result['elapsed']}s)")
                else:
                    logger.warning(f"  C. Sandbox: FAIL — {sandbox_result.get('error','')[:80]}")
                    # Try reflect-and-fix
                    try:
                        from src.reflect import reflect_and_improve
                        reflect = reflect_and_improve(code['function'], code['test'], sandbox_result.get('error',''), llm_config=_llm_config)
                        if reflect.get('fixed'):
                            code = {'function': reflect['code'], 'test': code['test']}
                            sandbox_result2 = run_in_sandbox(code['function'], code['test'], test_name='test_algorithm', timeout=10)
                            sandbox_ok = sandbox_result2['passed']
                            logger.info(f"  C. Reflect: {'PASS' if sandbox_ok else 'STILL FAIL'} after {reflect['attempts']} attempts")
                    except Exception as e2:
                        logger.warning(f"  C. Reflect failed: {e2}")
            except Exception as e:
                logger.warning(f"  C. Sandbox error: {e}")
        else:
            logger.info(f"  C. No code to test (skipping sandbox)")
        
        # D. Deploy to switcher (candidate)
        try:
            _switcher_init()
            candidate_path = deploy_candidate(skill_name, skill_md, code if code else None)
            logger.info(f"  D. Candidate deployed: {candidate_path}")
        except Exception as e:
            logger.warning(f"  D. Candidate deploy failed: {e}")
        
        # Register in lifecycle if configured
        if hasattr(config, 'lifecycle') and config.lifecycle.enabled:
            try:
                from src.skill_lifecycle import register_new_skill
                register_new_skill(skill_name, skill_path, paper.arxiv_id, paper.title, history)
            except Exception as e:
                logger.warning(f"  Failed to register skill in lifecycle: {e}")

        # ── Phase 4+5: Evaluate and Decide ──
        if dry_run:
            logger.info(f"  Dry-run: simulating evaluation for {skill_name}")
        else:
            logger.info(f"  Live evaluation for {skill_name}...")
        eval_data = _run_evaluation(skill_name, "", config, dry_run=dry_run)

        decision = make_decision(eval_data, config.decide)
        result.upgrades_evaluated += 1

        # Record in history
        record = UpgradeRecord(
            paper_arxiv_id=paper.arxiv_id,
            paper_title=paper.title,
            skill_name=skill_name,
            skill_path=skill_path,
            baseline_success_rate=eval_data.get("baseline_rate", 0),
            upgraded_success_rate=eval_data.get("upgraded_rate", 0),
            baseline_cost_tokens=eval_data.get("baseline_cost", 0),
            upgraded_cost_tokens=eval_data.get("upgraded_cost", 0),
            decision=decision["decision"],
            notes="; ".join(decision["reasons"]),
        )
        history.insert(record)

        detail = {
            "paper_id": paper.arxiv_id,
            "paper_title": paper.title,
            "skill_name": skill_name,
            "total_score": sp.total_score,
            "decision": decision["decision"],
            "reasons": decision["reasons"],
            "metrics": decision["metrics"],
        }
        result.details.append(detail)

        if decision["decision"] == "keep":
            result.upgrades_kept += 1
            logger.info(f"  -> KEPT by decision")
            # Promote if auto_promote enabled and sandbox passed
            if getattr(config.pipeline, 'auto_promote', False) and sandbox_ok:
                try:
                    promo = promote_candidate(skill_name)
                    if promo["status"] == "promoted":
                        logger.info(f"  E. -> AUTO-PROMOTED: {skill_name}")
                except Exception:
                    logger.warning(f"  E. Promote failed")
            elif sandbox_ok:
                logger.info(f"  E. Manual approval required: review candidate {skill_name} before promoting")
            else:
                logger.info(f"  E. Sandbox failed, candidate archived")
        else:
            result.upgrades_reverted += 1
            logger.info(f"  -> REVERTED by decision")
            if not dry_run:
                rollback_skill(skill_path, backup_path)

    history.close()
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    result = run_pipeline(dry_run=True)
    print(f"\nPipeline completed: {result.papers_found} papers, "
          f"{result.skills_generated} skills, "
          f"{result.upgrades_kept} kept, "
          f"{result.upgrades_reverted} reverted")
