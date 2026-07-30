# Self-Upgrade Agent (SUA)

> L0: SUA project README — orientation, current state,
> recent commits.  Per 2026-07-20 consolidation:
> SUA is the **knowledge library** for the hermes-root
> family.  Goal: "一个能约束 agent 行为的项目,
> 让 agent 不依赖 hermes 也能按好规则行动".

## Project identity (per 2026-07-20 re-architecture)

SUA is the **knowledge library** for the hermes-root
family.  It holds 3 categories of knowledge:

1. **Agent behavior rules** — 25 P-n (P1-P29 minus
   P6/P15/P16/P24, per c96 P28 lift + c167 P29 lift)
   + 27 M-n (M-n 1-27, per c95-c183).
2. **Skill generation guidance** — `docs/SKILL_DESIGN.md`
   (4 conditions to incubate, 5-phase process, 5
   self-preservation rules; consolidated back from
   skill-incubator on 2026-07-20).
3. **Project self-coordination** — README, AGENTS,
   PROJECT_STATE, INDEX, HANDOFF (per the 3-layer
   architecture in [AUDIT_PHASE_1_2_3_2026_07_16.md](docs/AUDIT_PHASE_1_2_3_2026_07_16.md)).

**Siblings** (not downstream of SUA):

- `../agent-reflection-skill/` — **standalone skill** since
  v1.0.0 (2026-07-16).  Reasoning primitives (analogy,
  induction, reflection, etc.) live there as a portable
  skill, NOT as a downstream consumer of SUA.  SUA does
  not actively push updates to it.
- `../knowledge-graph-seed/` — **frozen MVP** (75 PASS
  tests, 0 active dev).  See its README for current status.

**Archived**:

- `../skill-incubator/` — archived 2026-07-20.  Content
  consolidated into SUA's [SKILL_DESIGN.md](docs/SKILL_DESIGN.md).
  Directory retained for git history.

**Legacy code** (maintained, not extended):

- `core/`, `tests/`, `upgrades/` — v1.x-v3.x self-improving
  agent code.  Functional but dormant.  Per c73 pivot.

## Quick start (new agent)

1. Read `AGENTS.md` (operating rules)
2. Read `docs/HOW_TO_READ_GRAPH.md` (3-step read pattern)
3. Read `docs/HANDOFF.md` (project-specific onboarding)
4. Read `docs/PROJECT_STATE.md` Goal段 (current state)
5. Read `docs/PRINCIPLES.md` (L0 + L1 layer only)
6. Optional: `docs/SKILL_DESIGN.md` (if designing or
   incubating a new skill)

Total: ~30 min onboarding.

**For non-canonical runtimes** (Hermes / Cursor / Codex / Antigravity
that prefer the Agent Skills `SKILL.md` format, or stateless sessions
that need a one-line entry point), see
[`docs/CROSS_RUNTIME_SKILL_BRIDGE.md`](docs/CROSS_RUNTIME_SKILL_BRIDGE.md).
The bridge is a convenience layer; the 6-step workflow above is the
canonical SUA onboarding.

## Working principles (P-n) + workflow (M-n)

See `docs/PRINCIPLES.md` (25 P-n working,
P1-P29 minus 4 demoted per c47 plan + c96
P28 lift + c167 P29 lift).  Hook enforces
P-n cite in commit messages.

See `docs/OPERATING_RULES.md` (25 M-n,
latest M-message-pattern-recognition per c183).

## Sibling project (skill)

`../agent-reflection-skill/` is a **standalone sibling**,
NOT a downstream of SUA.  Its v1.0.0 release (2026-07-16)
froze it as a portable, framework-agnostic skill.  SUA does
not actively synchronize with it; the skill preserves its
own lineage via `M-skill-synchronize` (c83) + its internal
self-preservation contract (5 rules in
`docs/SKILL_DESIGN.md`).

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
