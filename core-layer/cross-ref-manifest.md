# Cross-ref manifest — SUA 核心 layer exports

> L0: Manifest of cross-refs from SUA 核心 layer to sibling
> repos.  Per user message 2026-07-16 "核心+用户 → skill 项目
> (分开维护)" + M-n 21 cross-project.

## What is "exported" from 核心 layer

Per user message 3-layer architecture:
- 核心 layer = **agent behavior rules** (in SUA)
- User + agent behavior = **shared** (in skill projects)
- Project-specific = **in project** (KG, individual repos)

**Physical placement** (per 你 directive):
- 核心 LAYER docs stay in SUA's `core-layer/` directory
- **Cross-refs** in sibling VERIFICATION.md files
  ensure discoverability from sibling entry points
- **NO content extraction** — sibling repos don't get
  their own copy of M-n 29 / M-n 35; they get
  cross-references to SUA's authoritative source

## Cross-ref matrix (post-Phase A + Phase 4)

| Source (SUA) | Target (sibling) | Trigger | Committed in |
|---|---|---|---|
| `core-layer/README.md` | `agent-reflection-skill/VERIFICATION.md` "3-layer governance cross-ref" | `08ed89e` |
| `core-layer/README.md` | `skill-incubator/VERIFICATION.md` "3-layer governance cross-ref" | `274ad5d` |
| `core-layer/README.md` | `knowledge-graph-seed/VERIFICATION.md` "3-layer governance cross-ref" | `7438fc4` |
| `docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md` | `agent-reflection-skill/VERIFICATION.md` "4 critical-thinking primitives cross-ref" | `ba3376e` |
| `docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md` | `skill-incubator/VERIFICATION.md` "4 critical-thinking primitives cross-ref" | `f3b4f5d` |
| `docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md` | `knowledge-graph-seed/VERIFICATION.md` "4 critical-thinking primitives cross-ref" | `9395424` |
| `docs/INDEX.md` | (entry navigation for all 88 docs) | `a348011` |
| `AGENTS.md` Read first item 8 | (core-layer entry for fresh agents) | `3ac8221` |
| `AGENTS.md` Read first item 9 | (M-n 35 critical-thinking entry for fresh agents) | `6a26b7c` |

## Why this design (not content extraction)

Per M-n 35 critical-thinking primitive 2 (逆向) + 你
turn 之前 turn pattern:

- **Alternative A**: extract M-n 29 + M-n 35 content
  to skill projects (orphan risk + sync overhead)
- **Alternative B** (CHOSEN): keep authoritative source
  in SUA + add cross-refs in siblings

B is better because:
- Single source of truth (no sync drift)
- Lower risk (cross-ref additions are non-destructive)
- Per M-n 32 Guardrail #1: small commits = safe
- Per M-n 27 knowledge-layer-architecture: 3 layers
  but content taxonomy ≠ extraction

## Future extension

When M-n 35 critical-thinking primitives get adopted
in new contexts (new sibling project), apply same
pattern:
1. Add VERIFICATION.md "4 critical-thinking primitives
   cross-ref"段
2. Cross-ref to SUA's docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md
3. Commit + propagate to next-cycle project

## P-n / M-n cited

P11 (摘要+引用), P14 (docs stay current), P17 (老实说),
P21 (cross-project), P25 (post-modify re-apply),
P29 (recursion).

M-n 21 (cross-project — explicitly codify), M-n 27
(knowledge-layer-architecture 3 layers), M-n 32
(self-learning-guardrail), M-n 35 (critical-thinking).
