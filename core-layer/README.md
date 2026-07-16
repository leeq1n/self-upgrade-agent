# SUA 3-layer governance (per 你 turn 2026-07-16)

> L0 marker for the SUA **核心 layer** boundary.  Per 你 turn
> 2026-07-16: "核心层只能由 agent 自己主动修改，规划 agent
> 的行为和 skill 的行为（修改时需要评估，修改后需要验收）".

## Path naming rationale (per M-n 32 retrospective 2026-07-16)

This directory is at SUA root (`./core-layer/`), NOT `./core/`,
because `core/` was already in use as SUA's **runtime agent
Python package** (per phase 4 C1 failure mode, commits
e7c9072 + a3de71f reverted via c681e0b + ad8835e).

**Per M-n 32 self-learning-guardrail Guardrail #1**:
verify target directory state before creating new content
in similar-named paths.

## 3-layer architecture

| Layer | Modifier | Where it lives (SUA) | Cross-repo location |
|---|---|---|---|
| **核心** (core) | Agent-only (with eval-before + verify-after) | `core-layer/` directory + `AGENTS.md` + `hooks/` + `.hermes/scripts/` + `docs/OPERATING_RULES.md` L1 | Future: skill project (per 你 turn 提案) |
| **用户** (user) | User (habits) + shared (general) | Currently implicit in memory system; needs codification | Future: skill project |
| **项目** (project) | Project owner | `docs/PRINCIPLES.md` + `docs/PROJECT_STATE.md` + project-specific docs | Per project (intra-repo) |

## 核心 layer scope

| In 核心 | NOT in 核心 |
|---|---|
| Agent behavior rules (M-n 25, M-n 29, M-n 34) | Project principle library (P1-P29) |
| Skill invocation rules (M-n 27) | User habits / cross-project knowledge |
| 5 primitives gate | Project-specific docs (L1+) |
| Hook whitelist P1-P29 + M-n 29 trailer | R-n invariants |
| Cold-start simulation method | Knowledge graph data |
| `m_n29_5step.py` script | `docs/PRINCIPLES_FULL.md` content |

## Modification governance (per 你 turn)

1. **Eval-Before**: 5 primitives applied + `python .hermes/scripts/m_n29_5step.py --self`
2. **Commit**: cite P-n + M-n in commit body
3. **Verify-After**: cold-start simulation + check hooks
4. **Failure**: revert via `git reset --hard HEAD~1` + retry

## Cross-references

- `core-layer/governance-template.md` (L1: detailed eval-before + verify-after steps)
- `AGENTS.md` (L0 operating rules)
- `.hermes/notes/phase4_c1_failure.md` (failure retrospective 2026-07-16)
- Plan: `hermes-plan-3-layer-architecture-2026-07-16.md`

---

**P-n cited**: P11, P14, P20, P22, P25 (per 你 turn audit).
**M-n cited**: M-n 30 (knowledge-context-trade-off
Priority 1), M-n 32 (self-learning-guardrail Guardrail #1),
M-n 34 (pre-task scan, self-application).
