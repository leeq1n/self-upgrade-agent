# SUA 核心 layer (created 2026-07-16, per 你 turn 3-layer proposal)

> L0 marker for the SUA **核心 layer** boundary.  Per 你 turn
> 2026-07-16: "核心层只能由 agent 自己主动修改，规划 agent
> 的行为和 skill 的行为（修改时需要评估，修改后需要验收）".

## Boundaries

| In 核心 | NOT in 核心 |
|---|---|
| Agent behavior rules (M-n 25, M-n 29) | Project principle library (P1-P29) |
| Skill invocation rules (M-n 27) | User habits / cross-project knowledge |
| 5 primitives gate | Project-specific docs (L1+) |
| M-n 34 (M-pre-task-scan) | OPERATING_RULES.md content |
| Hook whitelist P1-P29 + M-n 29 trailer | R-n invariants |
| Cold-start simulation method | Knowledge graph data |
| Scope: AGENTS.md, hooks/, .hermes/scripts/, OPERATING_RULES.md L1 | Scope: docs/, PRINCIPLES.md, PROJECT_STATE.md |

## Modification governance (per 你 turn)

- **Modify 核心**: agent self-edit ONLY
- **Evaluate before**: `python .hermes/scripts/m_n29_5step.py --self --claim <X>`
  + 5 primitives applied in commit message body
- **Verify after**: M-n 29 5-step + cold-start sim
- **Fail** → revert via `git checkout - .` (no destructive)

## Cross-references

- **Plan**: `hermes-plan-3-layer-architecture-2026-07-16.md`
  (Temp, last update 2026-07-16)
- **Phase 1-3 audit**: `docs/AUDIT_PHASE_1_2_3_2026_07_16.md`
- **AGENTS.md**: operating rules surface
- **M-n 27 (existing)**: knowledge-layer-architecture (3-source
  content taxonomy: HERMES/SUA/SKILL).  Coexists with
  this 核心 layer (option (a) per plan).

## Lifecycle

Per M-n 18 destruction principle: this directory's
**content** follows extract-on-merge cycle (subject to
change).  Each commit to core/ is documented in
`core/CHANGELOG.md` (to be created when content extracts
happen).

---

**P-n cited**: P11 (摘要+引用), P14 (docs stay current),
P20 (L0 line), P22 (when stuck→plan), P25 (post-modify
re-apply).
**M-n cited**: M-knowledge-context-trade-off (M-n 30
Priority 1), M-self-learning-guardrail (M-n 32
Guardrail #4), M-pre-task-scan (M-n 34).
