L0: Project state — goal, current version, next step (1-paragraph).
Last P20-verified: 2026-07-13

---
description: "Project goal, status, mistakes, constraints, next step"
status: "summary"
last_updated: "2026-07-14 (35 commits: doc cleanup + P25 lift + final audit)"
---

# PROJECT_STATE — brief
> L0: Current project state (1-paragraph).  Load when: need snapshot of current goal/version/next step.

**Goal (1 sentence) (updated 2026-07-15 turn reset)**: 一个原则库项目 + skill 孵化器 + 已孵化的自我改进 skill 项目的 3-project 架构。SUA 自身 = 原则库（agent 行为规范 + 跨项目知识）；skill 孵化器 = sibling project（`../skill-incubator/`，设计并孵化 skill）；已孵化 skill = `../agent-reflection-skill/`（6 reasoning primitives + recursion + self-application）。

**Pivot note**: 之前目标是 self-improving agent that modifies core/planner.py（session 早期定义）。中间用户调整为"项目自组织 + 知识图谱/平铺式 + agent-onboarding skill 给其他项目用"。新目标替代旧目标，旧 self-improving 实现仍存在 core/planner.py 但不再是 project 焦点。

**3 个子目标** (per c50 audit + c52 SELF_ORG + c53 KNOWLEDGE_ORG + c57 HOW_TO_READ_GRAPH):

1. **A. 项目自组织 + 自规划**：agent 写新 commit 时自动 self-audit（per P27 candidate）
2. **B. 知识组织**：图/树（项目文档）+ 平铺式（agent-onboarding skill 给其他项目用）
3. **C. 新 agent 入场可学**：HOW_TO_READ_GRAPH.md 提供 3 步读模式，新 agent 不需要 hermes 也能按规则行动

**V2 起源**: PROJECT_STATE.md + README.md + AGENTS.md 三处之前都说旧目标"自进化 agent"，用户 turn reset 指出 vision drift。c73 同步三处目标陈述。

**Tests**: 621 PASS + 6 skip + 0 fail (last commit `2b88a79`).
*Excludes* 1 deselected test (`test_core_planner_md5_matches_head`)
because the user modified `core/planner.py` directly (LLM Round 5
KEPT, commit `20e958d`) — user decides keep/revert.

## Doc cleanup session 2026-07-14 (commits 95097fb..f6c796d)

31 commits across 8 batches addressing doc drift +
extending workflow rules.  Per M-task-summary parent
verification, the latest batch is documented in
`git log 7802611..HEAD~1` (or by message body
search "batch verification").

Key changes:
- Orphan-reference cleanup (commits 95097fb..c414821)
- EXTENSIONS.md X2 consolidation (commits 31ea3ce..e7a0c1f)
- Switch action protocol (commits 05312d2..b6adb74)
- Follow-ups cleanup (commits 0c59e4f..aa2710f)
- Verify-before-edit rule (commits 0a4240a..c8efd26)
- Follow-ups + design filtering (commits 99596e9..6d30895)
- Lessons learned + follow-up propagation (commits 264c4cd..7802611)
- Principle modification discipline (commit f6c796d)

**Note**: all 35 commits this session were docs-only;
no code changes.  Project functionality unchanged.

## P25 lift batch (commits 6c6cb6c..6ca8b3a)

3 commits lifting "P-n / M-* modification discipline"
to a first-class P-n (P25) + extending the P-n vs
M-* boundary段 with a 3rd case ("meta-principles
about principles").  Fixes a mis-classification
introduced in commit f6c796d.

Key changes:
- **PRINCIPLES.md**: new `### P25. Principle modification
  discipline` 段 (canonical location); boundary段
  extended with 3rd case + test question
- **AGENTS.md**: 4 places updated P1-P24 → P1-P25
- **hooks/commit-msg**: regex updated to `P([0-9]|1[0-9]|2[0-5])`
- **PRINCIPLES_DETAIL.md + MEMORY_TOOLS.md**: L0 lines updated

**Note**: installed hook at `.git/hooks/commit-msg`
still has P1-P24.  User must `cp hooks/commit-msg
.git/hooks/commit-msg && chmod +x` for hook to
accept P25-only citations.

## Current status (v3.0.2 OVERALL COMPLETE, doc cleanup + P25 lift 2026-07-14)

Per LITERATURE (Self-Harness 40→62%, Lilian Weng "harness as
important as model"), v3.0.2 implements a think-execute harness:

| Module | Purpose | LOC |
|--------|---------|-----|
| `src/v3_multipaper.py` | read all 11 papers from catalog | 180 |
| `src/v3_judge.py` | LLM judge picks best paper (with mock fallback) | 265 |
| `src/v3_persist.py` | save summaries + decisions (P19) | 167 |
| `src/v3_replay.py` | inspect failures (fast, no LLM) | 81 |
| `src/v4_thinker.py` | Thinker abstract (plan API + 5 fallback paths) | 169 |
| `src/v4_executor.py` | Executor abstract (skill dispatcher) | 129 |
| `src/v4_loop.py` | Loop controller (Think → Execute → Observe) | 124 |
| `src/v2_round.py` | extended: `run_one_round_with_harness()` | 360+ |

**CLI (unified, 3 visible subcommands)**:
```bash
python -m self_upgrade improve --multi --max-retries 2 --count 5
python -m self_upgrade replay   # inspect failures (default) or --live
python -m self_upgrade test-scale 5  # N consecutive single-paper rounds
```

**Hidden aliases** (backward compat): `improve-multi`, `improve-harness`.

## Real LLM data (v3.0.2 follow-up #4 + #5)

- `--count 5` multi-paper run (commit `20e958d`): **1/5 KEPT (20%)**
- Round 5 KEPT: LLM added `generate_tests` option to `core/planner.py`
  (Self-Harness-style improvement, 16/16 tests pass)
- `core/planner.py` is LLM-modified, **user decides keep/revert**

## Mistakes made (do not repeat)

See full table in
[`PROJECT_STATE_DETAIL.md §Mistakes`](PROJECT_STATE_DETAIL.md#mistakes-made-do-not-repeat);
short version: 12 specific bugs (LLM timeout misinterpreted, key bypass
missing, hardcoded pre-filter, `git add -A` danger, retry logic
status confusion, etc.) — don't re-introduce them.

## Constraints

See [CONSTRAINTS.md](CONSTRAINTS.md) for the full list (奥卡姆,
fail-OPEN, atomic, user-edits-keys-never-agent, etc.).  Project
constraints change rarely; that file is the source of truth.

## Next step

See [../../TODO.md](../../TODO.md) for pending work.  Top priority
is **v3.0.3 — autonomous daily loop** (per user 2026-07-10
"我希望这个项目之后可以自己独立运行"):

1. **More 5-round data** — `--count 5` 拿 10+ runs 拿统计 KEPT ratio
2. **Decide `core/planner.py`** — keep (LLM 真贡献) or revert
3. **`daily-loop --interval 24h`** — autonomous, cron-driven
4. **state.json + failure recovery** (P18 + P19)
5. **Skill registry** (per LITERATURE: SkillOpt)

## References

- INDEX: [INDEX.md](INDEX.md)
- User intent (verbatim quotes): [USER_INSIGHTS.md](USER_INSIGHTS.md)
- Hard rules: [CONSTRAINTS.md](CONSTRAINTS.md)
- LLM choice: [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- Working principles: [PRINCIPLES.md](PRINCIPLES.md)
- Real-run data: [OBSERVATIONS.md](OBSERVATIONS.md)
- Pending tasks: [../../TODO.md](../../TODO.md)
- Done tasks: [../../DONE.md](../../DONE.md)
- **Detailed technical history** (the long form): [PROJECT_STATE_DETAIL.md](PROJECT_STATE_DETAIL.md)
- **Knowledge Graph (P1, deferred)**: [TODO_KNOWLEDGE_GRAPH.md](TODO_KNOWLEDGE_GRAPH.md)
