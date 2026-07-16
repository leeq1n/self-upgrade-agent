# M-knowledge-context-trade-off (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` §
> M-knowledge-context-trade-off段 (M-n 30).
> Per P11 摘要+引用 + R6.

**Origin**: per 你 turn 2026-07-15 explicit
5 parts + Part 3 trade-off directive.

## 4-priority decision tree

### Priority 1 (HIGHEST): Knowledge 充足

**Definition**: agent has all knowledge
needed for the task.

**Methods**:
- All audit points PASS (per M-n 29)
- Reasoning primitives (6 per skill)
- Case studies (6 per skill)
- Documentation cross-refs

**Failure if violated**: agent can't
perform task.  This is 最高优先级.

### Priority 2 (HIGH): Context 管理

**Definition**: agent doesn't exceed
context budget.

**Methods**:
- M-n 26 (context-decay-management)
- M-n 23 (periodic re-analysis)
- M-n 18 (节点 生命周期 + destruction)
- Lazy-load for smaller models

**Failure if violated**: agent context
explosion, performance degradation.

### Priority 3 (TIE): Trade-off

**Definition**: balance between knowledge
充足 度 and context 管理.

**Methods**:
- 分层 (hierarchical) for knowledge layer
- 平铺式 (flat) for behavior spec (per
  你 turn Part 5)
- 类比 (analogy) for compression
- 自顶向下 分治 for decomposition

**Failure if violated**: imbalanced (too
much context for too little knowledge, or
vice versa).

### Priority 4 (Always): 分层 自顶向下 分治

**Definition**: 永远 apply 分层 自顶向下 分治
方法 (per 你 turn Part 4 隐含 ask).

**Methods**:
- M-n 16 stage 3 top-down 分治
- M-n 18 recursive-summary-protocol
- M-n 22 3W1H-think-first
- M-n 27 knowledge-layer-architecture

**Failure if violated**: 没 分层, project
混乱, hard to maintain.

## Trade-off method (per 你 turn Part 3)

### 分层 (hierarchical)

When to apply:
- Knowledge layer (primitives + case
  studies)
- Cross-project docs
- Multi-level abstractions

Example: P11 摘要+引用 L0/L1/L2 + _DETAIL
companion.

### 平铺式 (flat)

When to apply:
- 行为规范 (agent behavior spec)
- Stable rules (per M-n 18 节点 生命周期:
  core layer rarely changes)
- Quick reference docs

Example: SKILL.md 7 sections + AGENTS.md
5 sections = 12 sections 平铺式 (per c211).

### 类比 (analogy)

When to apply:
- Compression (per M-n 14 entropy)
- Cross-context transfer (per M-n 14
  two-track-reasoning)
- Pattern recognition (per M-n 14 class比
  + 归纳)

Example: 5 logic primitives (analyze /
reason / 联想 / 归纳 / 总结) per M-n 29
Step 2 + 你 turn.

### 自顶向下 分治

When to apply:
- Project decomposition (per M-n 16)
- Task breakdown (per M-n 18)
- Plan construction (per M-n 22)

Example: PLAN file 维护 (per c112 + c115
split) + sub-task summaries + parent
synthesis + destruction.

## 3-layer application (per M-n 27)

| Layer | Trade-off method | Rationale |
|---|---|---|
| 核心层 (core) | 平铺式 | rarely changes, quick read |
| 知识层 (knowledge) | 分层 + 类比 | grows via new primitives + case studies |
| 项目层 (project) | 分层 as needed | framework-specific, high churn |

## Worked example (c213 self-application)

Apply M-n 30 to current task (codify M-n 30):

- Q1 (Knowledge 充足): M-n 30 段 codifies
  trade-off 4-priority table ✅
- Q2 (Context 管理): OPERATING_RULES.md
  no R5 cap (81209 → 81352 bytes, +143)
- Q3 (Trade-off): 4 methods (分层 + 平铺式
  + 类比 + 自顶向下 分治)
- Q4 (分层 自顶向下 分治): applied to M-n
  30 codification itself

Result: trade-off 4-priority PASS.

## Relationship to other M-n

- **M-n 14 (two-track-reasoning)**: M-n 30
  uses 类比 + 归纳 for compression.
- **M-n 18 (recursive-summary-protocol)**: M-n
  30 uses 分层 for node 生命周期.
- **M-n 22 (3W1H-think-first)**: M-n 30 uses
  3W1H for priority decision.
- **M-n 26 (context-decay-management)**: M-n
  30 addresses context 管理.
- **M-n 27 (knowledge-layer-architecture)**: M-n
  30 IS M-n 27 applied to trade-off.
- **M-n 29 (acceptance-protocol)**: M-n 30
  priority 1 (Knowledge 充足) = M-n 29 audit.

## Cross-references

- `docs/OPERATING_RULES.md` § M-knowledge-
  context-trade-off (M-n 30 main段)
- `docs/OPERATING_RULES.md` § M-n 14 / M-n
  18 / M-n 22 / M-n 26 / M-n 27 / M-n 29
- SUA `agent-reflection-skill/SKILL.md` §
  Flat structure (per c211)
- 你 turn 2026-07-15 — origin

---

## UPDATE ORDER RULE (added per 你 turn 2026-07-15 priority directive)

### Priority 5 (Always): Update order rule

**Trigger**: when 知识 changes in SUA (P-n, M-n, R-n, docs, etc.).

**Rule** (per 你 turn 4 parts):
1. **SUA** (知识库) = **source** — change 起源.
2. **skill-incubator** (孵化器) = **middle** — process propagation.
3. **skill** (final) = **downstream** — receives change.

**Propagation path**: SUA → skill-incubator → skill.

**Reverse propagation NOT allowed** (per M-n 20 framework-agnostic + P21 cross-project independence).

**Why this rule**:
- SUA holds 原则 + M-rules + R-rules (core 知识库).
- skill-incubator holds 5-phase process + 4 sub-knowledge areas + case studies.
- skill holds 6 reasoning primitives + when-to-reflect + Stand-alone spec.

**When SUA changes**:
- P-n change: re-evaluate all M-n that cite P-n, then update skill references
- M-n change: update skill SUBSET (primitives that match new M-n), then update skill-incubator case studies
- R-n change: verify skill + skill-incubator compliance

**When skill changes**:
- Should NOT happen — skill is downstream, must follow SUA source
- If 必要, write a SUA proposal first (per M_RULE_AUTHORING)

**Worked example (c222 self-application)**:

This 段 IS M-n 30 self-application: codify Update order rule as Priority 5 (Always), per 你 turn 2026-07-15 explicit directive.

SUA c222 codify → THEN propagate to skill-incubator (c223) → THEN propagate to skill (c224).