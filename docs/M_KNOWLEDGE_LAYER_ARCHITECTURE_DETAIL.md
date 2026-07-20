# M-knowledge-layer-architecture (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> knowledge-layer-architecture段 (M-n 27).
> Per P11 摘要+引用 + R6, this companion is
> required when the summary段 references
> detailed 3-layer + 3 sources + lifecycle.

**Origin**: user message 2026-07-15 (6 parts: 3-layer + 3 sources + single-skill + new-agent perspective + lifecycle + 联想).

## 3-layer knowledge structure (detailed)

### Layer 1: 核心层 (core layer)

**Definition**: self-referential behavior rules.  Per P22 case-3, self-reference (自指) needs careful boundary.

**Content**:
- **P-n**: P7 (奥卡姆), P17 (老实说), P20
  (R5), P22 (case-3 meta), P27 (cross-
  axiom), P28 (recursion)
- **M-n**: M-n 12 (terminology), M-n 14
  (two-track), M-n 18 (recursive-summary),
  M-n 21 (ask/infer/guess), M-n 22 (3W1H),
  M-n 25 (turn-pattern), M-n 26 (context-
  decay), M-n 27 (knowledge-layer)

**Why case-3 = 核心**: per P22 case-3, principles about principles apply to agent itself (regardless of project).

**Risk**: self-reference can spiral (自指悖论).  Solution: P22 + P28 strict boundary.

### Layer 2: 知识层 (knowledge layer)

**Definition**: general cross-project capabilities.

**Content**:
- **Reasoning primitives** (6): analogy,
  induction, reflection, abduction,
  compression, recursion
- **Case studies** (5-6): recursion, analogy,
  induction, reflection, abduction,
  compression
- **when-to-reflect**: decision tree for
  primitive selection
- **M-n**: M-n 14 (类比), M-n 23 (re-
  analysis), M-n 26 (decay)
- **P-n**: P10 (capture), P11 (摘要+引用),
  P29 (reduce context)

**Why this is knowledge layer**: 类比
reasoning, induction, etc. work in any
project.  Not project-specific.

### Layer 3: 项目层 (project layer)

**Definition**: project-specific knowledge.

**Content**:
- **框架 specifics**: which framework, which
  combinations, which APIs
- **项目 history**: CHANGELOG, prior
  decisions
- **Conventions**: project-specific naming,
  structure
- **Examples**: skill-incubator's 5-phase
  process, SUA's P-n/M-n, hermes memory

**Why this is project layer**: only useful
in this specific project context.  When
skill is portable, this layer may differ
across projects.

## 3 sources relationship (detailed)

### Source A: hermes 自进化 files

**Nature**: ephemeral (per-session) +
cross-project memory.

**Examples**: MEMORY.md, T-NNN dormant
triggers, session_search results, runtime
config.

**Application**:
- M-n 7 (M-task-summary): captures runtime
  task state.
- M-n 8 (M-task-graph): captures task
  dependency graph.
- M-self-application level 3 (memory):
  reloads MEMORY.md per turn.

**Single-skill scenario**: hermes =
ABSENT.  Skill must work without hermes
(per user message Part 3).

### Source B: SUA 项目知识库

**Nature**: persistent (project-internal) +
project-agnostic.

**Examples**: 25 P-n + 26 M-n + R1-R12.

**Application**: Case-2 M-n 4 P-n (主),
case-3 self-application (level 4).

**Single-skill scenario**: SUA = ABSENT.
Skill should encode the portable subset of
SUA rules (per c195 cross-ref: 22 SUA
rules = 10 P-n + 12 M-n).

### Source C: skill (final 3rd source)

**Nature**: portable + cross-framework +
the ONLY reliable source in single-skill
scenario.

**Examples**: 6 reasoning primitives +
6 case studies + when-to-reflect + AGENTS.md
framework compatibility + c195 SUA cross-ref.

**Application**: All 3 layers in portable
subset form.

**Conflict resolution** (per M-n 26 + R6):

When 3 sources conflict:
1. hermes (most contextual) - local
2. SUA (most authoritative) - project
3. skill (most portable) - cross-project

For single-skill scenario: skill > SUA >
hermes (since hermes absent, SUA absent).

## Single-skill fallback protocol

### 4-Step protocol

1. **Detection**: Skill-only / +SUA / +SUA+hermes.
2. **Bootstrap**: Read SKILL.md + HANDOFF.md + AGENTS.md + when-to-reflect.
3. **Self-application**: per P28 + M-n 25 recursion.
4. **Refresh**: M-n 18 destruction + M-self-application level 3 + M-n 14 compression.


## 跨项目 memory management

### Memory types

| Type | Source | Persistent | Scope |
|---|---|---|---|
| Session | hermes | No | per-session |
| Episodic | MEMORY.md | Yes | project |
| Semantic | SUA | Yes | project |
| Procedural | skill | Yes | cross-project |

### Sync protocol

- hermes ↔ SUA: M-n 17 Path 2 (inter-domain MCP).
- SUA ↔ skill: M-skill-synchronize (c83) + c195.
- hermes ↔ skill: M-self-application level 3.

### Boundaries (per R11)

project-agnostic memory (skill + general M-n) should NOT bleed into project-specific memory (project layer).

## 10 open questions (per user message Part 6 联想)

| # | Question | Status (per current 段) |
|---|---|---|
| 1 | 3-layer boundary enforcement (P22) | Solution: strict case-3 + R11 invariant |
| 2 | 3-source conflict resolution | hermes (local) > SUA (project) > skill (portable) |
| 3 | Offline fallback | per Single-skill protocol above |
| 4 | Cold vs warm start (M-n 26) | cold=all layers, warm=L0+lazy L1/L2 |
| 5 | Skill version + memory | Pending SemVer; memory persistence across versions |
| 6 | Bootstrap (no SUA history) | Start from 核心 layer (always exists) |
| 7 | Discovery protocol (M-n 20) | Per AGENTS.md L0 + L1 layer |
| 8 | Failure modes (3 layer conflict) | P-n > M-n > context per P22 |
| 9 | Meta-meta level (L5?) | 3-layer IS meta-meta about self-application |
| 10 | Recursive destruction (M-n 18) | project layer can be destroyed, core + knowledge preserved |

## Relationship to other M-n / P-n

- **P22 / P28 / P29**: applied (P22 case-3 meta, P28 recursion, P29 reduce-context).
- **M-n 18 / 20 / 26**: support (destruction + discoverability + context-decay prevention).

## Self-application

This L2 IS M-n 27 self-application (P28 recursion): 3-layer codified in OPERATING_RULES.md (summary) + this L2 (detail) + skill HANDOFF_DETAIL.md (c195).

## Cross-refs

- OPERATING_RULES.md § M-n 27 main 段
- OPERATING_RULES.md § M-n 26 / M-self-application / M-n 18
- PRINCIPLES_FULL.md "P29"段
- skill/HANDOFF_DETAIL.md "SUA cross-ref" (c195)
- user message 2026-07-15 — origin
