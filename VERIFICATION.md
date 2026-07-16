# VERIFICATION — Project-level verification summary

> L0: One-page verification summary — what's
been verified + cross-refs.  Per P11 摘要+
引用 + R6 + M-n 20 framework-agnostic.

Last P20-verified: 2026-07-15

## 1-axiomatic verification (per P5 measure
twice commit once)

- [x] SUA 621 tests PASS + 6 skip + 0 fail
- [x] `hooks/commit-msg` INSTALLED (P-n 1-29
  whitelist per c96 P28 LIFT + c167 P29 LIFT)
- [x] All commits reference at least 1 P-n

## R1-R12 invariant compliance (per c173)

| R-n | Status | Last verified |
|---|---|---|
| R1 | ✅ | c173 |
| R2 | ✅ | c173 |
| R3 | ✅ | c138 (trigger annotations) |
| R4 | ✅ | c173 |
| R5 | ✅ | c60-c192 (24+ docs fixed) |
| R6 | ✅ | c131-c136 (L2 companions) |
| R7 | ✅ | c173 |
| R8 | ✅ | c173 (3 OS-safe paths) |
| R9 | ✅ | c173 |
| R10 | ✅ | c173 |
| R11 | ✅ | c173 |
| R12 | ✅ | c139 + c169 (KG sync) |

**R1-R12 ALL PASS** (per c173 + c191).

## P-n / M-n completeness (per c167 + c183 + c189)

- **25 P-n working** (P1-P29 minus P6/P15/P16/P24)
- **27 M-n codified** (M-n 1-27, per c183 + c189 + c197)
- **24 M-n L2 companions** + 3 段 in OPERATING_RULES.md

## 3-project arch (per round 82 + c101)

| Project | Status | Arch role |
|---|---|---|
| SUA | ~95% | 原则库 (P-n + M-n + R-n) |
| skill-incubator | 100% | Skill 孵化器 (5 phases) |
| agent-reflection-skill | 100% | 已孵化 skill (6 primitives) |
| knowledge-graph-seed | synced | Cross-project KG (P1-P29) |

## Framework-agnostic compliance (per M-n 20 + c116)

- SUA: framework-agnostic (Hermes / Claude Code / Codex)
- skill-incubator: framework-agnostic
- agent-reflection-skill: framework-agnostic + AGENTS.md framework compatibility matrix
- knowledge-graph-seed: framework-agnostic

## Cross-references

- SUA `docs/PRINCIPLES.md` — 25 P-n working
- SUA `docs/OPERATING_RULES.md` — 26 M-n codified
- SUA `AGENTS.md` — operating rules for new agents
- SUA `docs/PROJECT_STATE.md` — current snapshot
- SUA `.hermes/plans/2026-07-15_160000-replan_DETAIL.md` — Changelog
- skill-incubator `SKILL_DESIGN.md` — 5-phase process
- agent-reflection-skill `SKILL.md` — invocation contract
- knowledge-graph-seed `docs/PHILOSOPHY.md` — P1-P29 sync

## Verification procedure for future agents

1. Read `VERIFICATION.md` (this file, L0).
2. Read `AGENTS.md` (operating rules).
3. Run `pytest` to confirm tests still PASS.
4. Spot-check `git log --grep='P[0-9]'` for
   P-n citation in recent commits.
5. Re-read 1 sample M-n 段 per M-n 26
   (context-decay-management) + 1 sample
   P-n 段 per P29.

## Mechanical enforcement layer (per retrospective 2026-07-16)

Per 你 turn "根据原则做决定" + retrospective 4-FAIL
diagnosis (M-n 32 Guardrail #4 violation across
multiple turns — claimed DONE without applying
5-step), this project adds mechanical external
trigger layer:

- **`.hermes/scripts/m_n29_5step.py`** (commit `05cd4d5`):
  deterministic baseline — 15 design criteria + 5
  primitives + validate cycle
- **`hooks/prepare-commit-msg`** (commit `f11b145`):
  commit-time reminder trailer when commit body
  mentions "task done" / "完成" / "PASS"
- **`AGENTS.md` "Task-done-notify reminder"段** (commit
  `e80fc73`): L0 surface with hard step 5 = external
  script invocation

## What's NOT yet enforced

Per 你 turn "怎么样才能保证自主阅读学习" + M-n 32
Guardrail #5 (auto-learning): LLM self-invocation
of M-n 29 5-step is NOT 100% guaranteed.  AGENTS.md
reminder + commit-time trailer + external script
all maximize external-trigger coverage.  Future
agents reading this project should:

1. Run `python .hermes/scripts/m_n29_5step.py --self`
   BEFORE claiming task done
2. Apply 5 primitives (Analyze / Reason / 联想 /
   归纳 / 总结) in plan / commit message
3. Cite P-n / M-n values that motivated changes

P-n cited: P17 (老实说 — explicit retrospective
diagnosis), P25 (post-modify re-apply per M-n 34
self-application), P29 (recursive enforcement).
M-n cited: M-acceptance-protocol (M-n 29 external
trigger), M-self-learning-guardrail (M-n 32
Guardrail #4 mechanical enforcement), M-knowledge-
context-trade-off (M-n 30 Priority 1).

## How to update this verification

When a new P-n / M-n is added (codified +
LIFTED), update this file (per M-n 17 Path 1
re-audit).