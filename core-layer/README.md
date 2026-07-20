# SUA 3-layer governance (per user message 2026-07-16)

> L0 marker for the SUA **核心 layer** boundary.  Per user message
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
| **核心** (core) | Agent-only (with eval-before + verify-after) | `core-layer/` directory + `AGENTS.md` + `hooks/` + `.hermes/scripts/` + `docs/OPERATING_RULES.md` L1 | Future: skill project (per user message 提案) |
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

## Modification governance (per user message)

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

**P-n cited**: P11, P14, P20, P22, P25 (per user message audit).
**M-n cited**: M-n 30 (knowledge-context-trade-off
Priority 1), M-n 32 (self-learning-guardrail Guardrail #1),
M-n 34 (pre-task scan, self-application).

## 3-layer modification policy (per user message 2026-07-16)

Per user message "skill 在别人电脑上还会主动修改
skill, 但是核心层修改需要尽可能少, 主要修改
用户层 (根据学到的知识判断改哪一层), 而项目层
知识随着项目变化而变化":

### Layer-specific modification frequency

| Layer | Modification frequency | Who modifies | When |
|---|---|---|---|
| **核心** | **As little as possible** | Agent (with eval-before + verify-after gates) | Only when agent behavior must change to maintain usefulness |
| **用户** | **Mainly** | Agent (with light verification) | When user habits / patterns emerge from observation |
| **项目** | **Continuously** | Project owner / agent (with knowledge-base update) | As project evolves — knowledge base, not log |

### Why this policy

| Layer | Risk if too frequently modified | Risk if not modified |
|---|---|---|
| **核心** | Stability loss; agents behave inconsistently across installations; commits pile up | Agent can't adapt; users find it useless |
| **用户** | Drift from user's actual habits | Same behavior even when user changes |
| **项目** | Stale project knowledge | Project-specific guidance becomes wrong |

### Trigger conditions per layer

**核心 layer modification triggers** (rare):

1. Agent's current behavior pattern produces
   consistent failures (e.g., 5+ failed tasks of
   same type).
2. New M-n is added that supersedes old behavior.
3. User explicitly requests core change (rare).

**用户 layer modification triggers** (frequent):

1. Observation: user shows consistent preference
   (e.g., "always concise", "always in 中文").
2. Observation: user corrects same anti-pattern
   3+ times.
3. New user-specific convention emerges (e.g.,
   specific output format).

**项目 layer modification triggers** (continuous):

1. Project state changes (new files, new
   conventions, new decisions).
2. Project lessons learned (failures + insights).
3. New project-specific docs created.

### Self-application (P29 recursion)

This 3-layer policy should apply to itself:
when updating this section, ask which layer
am I modifying?

- If the policy itself (meta) → **核心** layer.
  Modify rarely.
- If specific user-habit examples → **用户**
  layer. Modify when habits emerge.
- If specific project-state changes → **项目**
  layer. Modify as project evolves.

### Project knowledge = latest version + lessons (NOT log)

Per user message "项目层知识随着项目变化而变化 (这
不是日志而是知识库. 过去的知识只保留经验, 不
保留细节, 主要有最新版本的项目知识)":

| Wrong (log-style) | Right (knowledge-base-style) |
|---|---|
| Keep every commit message in detail | Keep only the latest version's key facts |
| Preserve all debugging stories | Preserve only the lessons (what to do differently next time) |
| Record all decisions | Record only the current decision (old decisions replaced, not stacked) |
| Append-only history | Latest + lessons (compact) |

**Implementation**: when project docs grow, they
should be **compacted** (per M-n 18 destruction +
M-n 26 compression).  Old content is replaced by
"lesson learned" notes, not preserved verbatim.

**Example**: if project has 5 retrospective docs,
the 6th one should reference the lessons from the
first 5, not duplicate their content.  The first
5 can be archived (still in git history) but the
**active** knowledge base has only the consolidated
lessons.

### Modification audit (per M-n 32 Guardrail #1)

Before any layer modification, verify:

1. **Target layer correct?** (核心 / 用户 / 项目)
2. **Trigger condition met?** (per layer-specific
   triggers above)
3. **Compactable?** (per project knowledge rule)
4. **Commit cites both layer + trigger**

If any answer is NO, defer or reclassify.

### Cross-references

- `AGENTS.md` (L0 operating rules + 继续
  protocol — per user message "继续 = 推进 + 思考 + 验收")
- `docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md`
  (M-n 35 — apply when deciding layer modifications)
- `docs/M_PRE_TASK_SCAN_DETAIL.md` (M-n 34 — pre-modify scan)
