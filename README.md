# Self-Upgrade Agent (SUA)

> L0: SUA project README — orientation, current state,
> recent commits.  Per user meta-rule 2026-07-15: SUA
> 维护 2 类知识 — agent 行为规范 (per `docs/PRINCIPLES.md`)
> + skill 生成规范 (per `docs/SKILL_GENERATION.md`).
> Goal (per c73 sync): "一个能约束 agent 行为的项目,
> 让 agent 不依赖 hermes 也能按好规则行动".

## 2 个项目身份 (per information topology 方案 C, c81)

SUA has **2 aspects** — they're both real and live in
the same repo:

1. **Docs project** (active since 2026-07-14 turn reset):
   - 25 P-n (after c47 plan) + P28 candidate (recursion)
   - 10 M-n (M-task-summary through M-skill-synchronize)
   - 6 reasoning primitives (mirrored in
     `../agent-reflection-skill/`)
   - Sibling project: `../agent-reflection-skill/`
2. **Self-improving agent** (legacy, v1.x-v3.x history):
   - Code: `core/`, `tests/`, `upgrades/`
   - CLI: `python -m self_upgrade <subcommand>`
   - Status: dormant (per c73 vision pivot)

Both are real; the docs project is now the **active
focus**, while the code project is **maintained** but
not extended.

## Quick start (new agent)

1. Read `AGENTS.md` (operating rules)
2. Read `docs/HOW_TO_READ_GRAPH.md` (3-step read pattern)
3. Read `docs/HANDOFF.md` (project-specific onboarding)
4. Read `docs/PROJECT_STATE.md` Goal段 (current state)
5. Read `docs/PRINCIPLES.md` (L0 + L1 layer only)
6. Optional: `docs/SKILL_GENERATION.md` (if working on
   sibling project sync)

Total: ~30 min onboarding.

## Working principles (P-n) + workflow (M-n)

See `docs/PRINCIPLES.md` (P1-P27 minus 4 demoted to P5
实操 per c47 plan).  Hook enforces P-n cite in commit
messages.

See `docs/OPERATING_RULES.md` (10 M-n, latest
M-skill-synchronize per c83).

## Sibling project (skill)

`../agent-reflection-skill/` — sibling project for
**portable reasoning primitives**.  Pattern extraction
flow: SUA commit demonstrates pattern → skill commit
codifies it.  Per `M-skill-synchronize` (c83) +
sibling awareness 段 (HANDOFF_DETAIL.md 61aab30).

## Detailed content (L2)

For full project history, CLI documentation, code
architecture, version history, and other L2 detail,
see [`README_DETAIL.md`](README_DETAIL.md).  Per R6,
this companion is required when the README exceeds
7 KB.

## Self-improving agent (legacy code, v1.x-v3.x)

Per c73 pivot note: this project was originally a
self-improving agent that modifies `core/planner.py`.
The code still exists and is functional, but is no
longer the project's focus.  For code documentation
and CLI usage, see `README_DETAIL.md` § Code legacy.
