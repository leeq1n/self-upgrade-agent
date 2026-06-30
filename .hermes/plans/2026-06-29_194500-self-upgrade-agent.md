# Self-Upgrade Agent Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a self-upgrading agent that searches academic papers, filters applicable innovations, implements them as Hermes Agent skills, evaluates improvements vs. cost, and decides whether to keep or revert each change.

**Architecture:** A modular pipeline orchestrated by `pipeline.py`. Each phase (Research, Filter, Implement, Evaluate, Decide) is an independent module. Generated skills follow Hermes Agent SKILL.md format. All attempts recorded in SQLite for long-term analysis.

**Tech Stack:** Python 3.12, arxiv API (stdlib), Semantic Scholar API, Hermes Agent skill system, SQLite (stdlib), pyyaml

---

## Feasibility and Value Assessment

### Feasibility: HIGH

Paper Search is low-risk (arXiv + Semantic Scholar free/stable with rate limiting). LLM Filtering is low-risk (same LLM powering Hermes, keyword fallback). Skill Generation is medium-risk (template-based with validation). Benchmarking is medium-risk (multiple trials for significance). Safety is low-risk (auto-backup before upgrade, fully reversible).

### Value: HIGH

1. Continuous Improvement: agent gets better over time without human intervention
2. Research Integration: bridges academia-to-practice gap automatically
3. Empirical Decision Making: keeps only changes with measured positive impact
4. Hygiene: even failed upgrades produce learnings recorded in history DB
5. Platform Building: pipeline itself reusable as Hermes skill

### Key Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Bad paper to bad upgrade | Medium | Multi-criteria scoring, consensus rejection |
| Auto-generated skill breaks system | High | Sandboxed testing, strict threshold, auto-rollback |
| Token cost from paper reads | Low | Configurable budget, batch evaluation |
| LLM hallucinates paper content | Medium | Verify against actual abstract/PDF |
| Evaluation metrics miss real quality | High | Multiple metrics, manual review gate option |

---

## Architecture

Pipeline phases:
1. Research: Search arXiv and Semantic Scholar for latest papers on agent-related topics
2. Filter: Score papers on abstract quality, applicability, novelty; select top candidates
3. Implement: Generate Hermes Agent SKILL.md from paper insight; validate and save
4. Evaluate: Run A/B benchmark comparing baseline (no skill) vs upgraded (with skill)
5. Decide: Compare results against thresholds; keep or revert with rollback


---

## Step-by-Step Implementation Plan

### Phase 1: Foundation

### Task 1: Project Scaffold

Create directory structure and configuration files.

**Files to create:**
- src/__init__.py, config.py, research.py, filter.py, implement.py, evaluate.py, decide.py, db.py, pipeline.py
- tests/__init__.py, test_config.py, test_research.py, test_filter.py, test_implement.py, test_evaluate.py, test_decide.py, test_db.py, test_pipeline.py
- config.yaml, requirements.txt, README.md

**config.yaml defaults:**
- research.keywords: agent framework improvement, prompt engineering technique, tool use optimization, multi-agent coordination, context compression, reinforcement learning agent, chain of thought reasoning, self-improving AI
- research.categories: cs.AI, cs.CL, cs.LG
- filter: min_abstract_score=6.0, min_applicability_score=5.0, min_novelty_score=5.0, max_papers_to_consider=5
- evaluate: trials_per_test=3, timeout_seconds=120
- decide: min_success_rate_delta=0.05, max_cost_increase_ratio=1.2

**Verification:** python -c "import yaml; yaml.safe_load(open('config.yaml'))"

---

### Task 2: Config Loader (src/config.py)

Load and validate YAML config with typed dataclass defaults.

Classes: Config, ResearchConfig, FilterConfig, ImplementConfig, EvaluateConfig, DecideConfig, PipelineConfig, DatabaseConfig (all dataclasses).
Function: load_config(path) parses YAML and fills defaults recursively.

Tests (test_config.py): test defaults, test YAML override, test validation rejects invalid.

---

### Task 3: Research Module (src/research.py)

Search arXiv and Semantic Scholar for papers.

Paper dataclass: arxiv_id, title, authors, published, abstract, categories, citation_count.
Functions: build_query_string(config), search_arxiv(config), fetch_paper_details(arxiv_id), enrich_papers_with_citations(papers).
Uses arXiv REST API (urllib) and Semantic Scholar API (json). Filters withdrawn papers.

Tests (test_research.py): query building, Paper dataclass, integration test with real API.

---

### Task 4: History Database (src/db.py)

SQLite tracking of all upgrade attempts.

UpgradeRecord dataclass with tracking fields.
UpgradeHistory class: insert, get_all, get_by_decision, get_stats.
Table: upgrades(id, paper_arxiv_id, paper_title, skill_name, skill_path, baseline_success_rate, upgraded_success_rate, baseline_cost_tokens, upgraded_cost_tokens, decision, notes, created_at).

Tests (test_db.py): insert and retrieve, filter by decision.


### Phase 2: Core Pipeline Modules

### Task 5: Paper Filter (src/filter.py)

Score papers on abstract quality, applicability, novelty.

ScoredPaper dataclass: paper, abstract_score, applicability_score, novelty_score, total_score (weighted), meets_thresholds.
Keyword-based heuristic scoring using three dictionaries: ABSTRACT_QUALITY_TERMS, APPLICABILITY_TERMS, NOVELTY_TERMS.
Keyword density mapped to 0-10 scale. Abstract length used as quality proxy.
Weighted total: applicability 50%, novelty 30%, abstract quality 20%.
filter_papers: score all, filter by thresholds, sort, take top N.

Tests (test_filter.py): scoring returns valid ranges, filtering ranks by total score.

---

### Task 6: Skill Generator (src/implement.py)

Generate Hermes Agent SKILL.md from paper insight.

Functions: generate_skill_md(paper, skill_name), validate_skill(skill_md), save_skill(skill_md, skill_name, skills_dir), backup_skill(skill_path, backup_dir).
Template includes: frontmatter (name, description, version, tags, source_paper), sections: Overview, Paper Source, Technique, Integration, Usage, Limitations.
Validation checks: frontmatter delimiters, required fields (name, description), minimum body length.

Tests (test_implement.py): required sections in output, validation rejects empty, validation accepts valid.

---

### Task 7: Evaluator (src/evaluate.py)

A/B benchmark comparing baseline vs upgraded agent.

BenchmarkTask dataclass: id, description, query, expected_output_pattern, difficulty.
BenchmarkResult dataclass: task_id, success, latency_seconds, token_usage, raw_output.
DEFAULT_TASKS: 3 tasks testing planning, reasoning, tool use.
run_single_benchmark: subprocess call to hermes chat -q.
evaluate_skill: runs trials with and without skill, returns comparison dict.
compare_results: computes deltas and recommendation.
compute_statistics: mean, min, max, stdev.

Tests (test_evaluate.py): task creation, statistics computation, comparison detects improvement.

---

### Task 8: Decision Module (src/decide.py)

Decide keep/revert based on evaluation results.

make_decision(eval_data, config): keep if success_rate_improved AND cost_acceptable. Auto-revert on regression (worse at higher cost). Returns dict with decision, reasons, metrics.
rollback_skill(skill_path, backup_path): restore from backup or remove.

Tests (test_decide.py): keep on improvement, revert on no improvement, revert on cost too high.


### Phase 3: Orchestration and Integration

### Task 9: Pipeline Orchestrator (src/pipeline.py)

Orchestrate the full research-filter-implement-evaluate-decide loop.

PipelineResult dataclass: papers_found, papers_scored, skills_generated, upgrades_evaluated, upgrades_kept, upgrades_reverted, errors, details.
run_pipeline(config, skills_dir, backup_dir, db_path, dry_run):
1. Search papers via research module
2. Enrich with citation data (non-fatal if fails)
3. Score and filter papers
4. For each qualified paper (up to max_upgrades_per_cycle):
   a. Generate skill MD and validate
   b. Backup existing skill if present
   c. Save new skill
   d. Run A/B benchmark (skip if dry_run)
   e. Decide keep/revert
   f. Record in history DB
   g. Rollback if reverted
5. Return PipelineResult with summary

Tests (test_pipeline.py): end-to-end dry run completes without errors.

---

### Task 10: CLI Entry Point (run.py)

Command-line interface for the self-upgrade agent.

argparse: --dry-run, --stats, --config, -v.
--stats: queries history DB and displays summary table.
main flow: load config, run pipeline, print results.

README.md: quick start guide, architecture overview, test instructions.

---

### Task 11: Verification

1. Run all tests: python -m pytest tests/ -v (Expected: 19 tests passed)
2. Dry run pipeline: python run.py --dry-run -v (Expected: pipeline completes)
3. Check stats: python run.py --stats (Expected: shows upgrade history)
4. Final commit

---

## File Summary

```
self-upgrade-agent/
  .hermes/plans/2026-06-29_194500-self-upgrade-agent.md   <-- THIS FILE
  config.yaml              Configuration
  requirements.txt         pyyaml>=6.0
  run.py                   CLI entry point
  README.md                Documentation
  src/
    __init__.py
    config.py              Config loader with dataclasses
    research.py            arXiv + Semantic Scholar search
    filter.py              Keyword-based paper scoring
    implement.py           SKILL.md generation from paper
    evaluate.py            A/B benchmark harness
    decide.py              Keep/revert decision + rollback
    db.py                  SQLite upgrade history
    pipeline.py            Full orchestrator
  tests/
    __init__.py
    test_config.py         (2 tests)
    test_research.py       (3 tests, 1 integration)
    test_filter.py         (2 tests)
    test_implement.py      (3 tests)
    test_evaluate.py       (3 tests)
    test_decide.py         (3 tests)
    test_db.py             (2 tests)
    test_pipeline.py       (1 integration test)
  upgrades/
    skills/                Generated skills land here
    snapshots/             Backups before modification
```

## Future Enhancements (Post-MVP)

| Enhancement | Priority | Effort |
|-------------|----------|--------|
| LLM-based paper scoring (replace keyword heuristics) | High | Medium |
| Full paper PDF reading via web_extract | High | Medium |
| Multi-paper synthesis skills | Medium | High |
| Human-in-the-loop approval mode | Medium | Low |
| Cron-based scheduled upgrade cycles | Medium | Low |
| Skill regression detection over time | Medium | Medium |
| Auto-rollback on later degradation | Medium | Medium |
| Cost budget enforcement | Low | Low |
| Web dashboard for upgrade history | Low | High |
