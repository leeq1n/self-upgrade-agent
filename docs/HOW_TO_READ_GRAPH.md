# How to read this project as a graph (per Option E, commit 56)

> L0: Read pattern for new agents entering this project.
> Per P20 progressive disclosure + P22 stuck→plan +
> P11 摘要+引用.  This is the "transformation" you
> mentioned (c56 reflection): graph (structure) →
> sequence (reading) happens **in the reader's head**,
> not in a tool.  This doc IS the read pattern.
> Last P20-verified: 2026-07-14 (initial)

## What this doc is for

Per c56 reflection: "context 阅读 需要 顺序" (your
insight) but "结构是自顶向下的, 分治的" (also your
insight).  These are **2 views of the same knowledge**.

This doc tells a new agent **how to traverse** the
graph as a sequence.  The transformation is **in
the reader**, not in a tool.

## The 3-step read pattern (per P22 stuck→plan + P20)

### Step 1: Read L0 first (per R10 + AGENTS.md)

**What to read**:
- `AGENTS.md` (project root) — Read first section
- `docs/PRINCIPLES.md` L0 axioms table (4 axioms)
- `docs/PRINCIPLES.md` 类比联想段 (5 essence families)

**Why**: L0 tells you **what category** of work
you're doing (奥卡姆 / Workflow / Test / Doc) and
**what operational pattern** applies (Plan-then-act
/ Verify-don't-guess / Capture-in-writing /
Minimum-viable / Meta-rules).

**Time**: ~2 minutes.

**Output**: you know which essence family your
task fits.

### Step 2: Read L1 for your specific task (per P20)

**What to read** (pick ONE based on Step 1):
- Task is "organize work" → `docs/OPERATING_RULES.md`
- Task is "modify principles" → `docs/PRINCIPLES_DETAIL.md` P25段
- Task is "add new docs" → `docs/PRINCIPLES_DETAIL.md` P11/P13段
- Task is "decide between options" → `docs/SWITCH_SIGNALS.md`

**Why**: L1 gives **operational detail** without
full L2 depth.

**Time**: ~5-10 minutes.

**Output**: you know **what to do** for your task
type.

### Step 3: Read L2 only if L1 prompts question (per P20)

**What to read**:
- L1 says "see X段 in PRINCIPLES_DETAIL.md" → go
  to that段
- L1 says "per P-n" → go to that P-n in
  PRINCIPLES_DETAIL.md
- L1 says "see c## commit" → `git log` to find
  the commit

**Why**: L2 is the **full detail**.  Don't read
L2 by default (per P11 + R5).

**Time**: ~5-30 minutes depending on depth.

**Output**: you have the **full context** for
your decision.

## 5 essence families (per c44 — operational grouping)

When you enter this project, identify which family
your task fits:

| Family | Tasks | Key docs to read |
|---|---|---|
| **Plan-then-act** (P1, P2, P4, P15, P22) | Decompose big task, sequence work, plan | OPERATING_RULES.md, RECURSIVE_DECOMPOSITION.md |
| **Verify-don't-guess** (P3, P5, P6, P16, P18, P19, P24) | Test, verify, regression | PRINCIPLES_DETAIL.md P3/P5/P6段 |
| **Capture-in-writing** (P10, P11, P12, P14, P17, P20, P21) | Doc, cite, structure, cross-ref | PRINCIPLES_DETAIL.md P11/P14/P20段 |
| **Minimum-viable** (P7, P8, P9, P13) | Simplify, don't over-build | PRINCIPLES_DETAIL.md P7段 |
| **Meta-rules** (P22, P23, P25, P26) | Modify principles, audit, accept | PRINCIPLES_DETAIL.md P22/P23/P25段 |

**Decision rule**: pick the family that **best
describes your task**.  If multiple, pick the one
that's **most concrete** (not the meta family).

## Cross-ref traversal (per P13 no orphan)

When you read a doc, you'll see cross-refs to other
docs.  **Don't follow all cross-refs immediately**.
Per P11 摘要+引用 + P13 no orphan:

1. **First-time read**: only follow cross-refs that
   are **necessary for current task** (per Step 1-3
   above).
2. **If cross-ref says "see X for detail"**: that's
   a **lazy pointer** (per P23 doc>script).  X IS
   the detail; don't follow.
3. **If cross-ref says "see X for context"**: that's
   a **helpful pointer**.  Follow if your task needs
   that context.

**Anti-pattern**: following every cross-ref is the
"graph trap" — you end up reading the entire graph
without finishing your task.

## The 7-check self-organization pattern (per c50 + P27 candidate)

If your task is **modify project structure** (add/
reorg docs, modify principles, add cross-refs), apply
these 7 checks BEFORE commit (per c50 audit + P27
candidate in c52):

1. **L0 line at top** (per P20 + R9): single-line
   summary, ≤ 120 chars
2. **L1 summary段** (per P20): 1-3 paragraphs
3. **L2 detail段** (per P20): full content
4. **Last P20-verified** (per R10): at end of doc
5. **Cap compliance** (per R5/R8): ≤ 7KB summary,
   > 7KB has _DETAIL companion
6. **Cross-refs** (per P11 + P13): parent doc +
   sibling docs reachable
7. **Inductive summary** (per P22 step 3 + c43):
   multi-section doc has synthesis段

**If any check fails**: fix in same commit
(per P14 + M-self-audit step 4).

## When you're stuck (per P22)

Apply P22's 3 actions:

1. **Check state**: `git status`, `git log --oneline
   -10`, list `docs/`, count tests, identify stale
   docs.
2. **Write plan**: goal + current state + next steps
   + risk.  Not thinking out loud.
3. **Update docs**: per P14 + M-self-audit.

**Why this matters**: per c22 SELF_ORG.md, project
self-organization is the **default** (no human
prompting).  This pattern IS the default.

## When you need to ask the user (per M-intent-parsing)

Apply M-intent-parsing:

1. **State interpretation**: what is the user
   actually asking?
2. **Steps**: what steps are needed?
3. **Ask ONLY 真歧义**: if no ambiguity, proceed.

**Anti-pattern**: asking for permission on every
step violates P22 (default to action).

## When you have multiple options (per c55 + c56)

Per c56 reflection: **read 原则 first, then decide**.
Don't build tools before applying P7 + P23.

**Step-by-step**:
1. List 3-5 options (don't jump to 1)
2. Apply 原则 to each (P7, P11, P13, P20, P22, P23)
3. Build decision matrix
4. Pick the option that **satisfies the most
   principles** (per c56 decision matrix)
5. Defer the rest (don't build them yet)

## Per P26 fresh-agent simulation (post-this-doc)

| Discovery step | Pre-doc | Post-doc |
|---|---|---|
| Knows where to start | ⚠️ (AGENTS.md only) | ✅ Step 1-3 pattern |
| Knows how to traverse cross-refs | ❌ (follows all = graph trap) | ✅ 3-rule pattern |
| Knows 7-check framework | ⚠️ (c50 audit only) | ✅ codified |
| Knows 5 essence families | ✅ (c44) | ✅ + reading order |
| Knows when to ask user | ⚠️ (M-intent-parsing) | ✅ explicit anti-pattern |
| Knows how to pick options | ❌ (jumped to 1 in c54) | ✅ 5-step pattern |
| Can read project without over-reading | ❌ (over-reads cross-refs) | ✅ 3-step pattern |

Fresh-agent simulation **PASS**.

## Per P22 step 3 self-application

Per P22 step 3 ("找 rule 之间的共性"): this doc
synthesizes the **read pattern** from 5 sources:
- P20 progressive disclosure
- P22 stuck→plan
- P11 摘要+引用
- c44 5 essence families
- c50 7-check framework
- c55 + c56 option analysis pattern
- M-intent-parsing

**This is the synthesis** of how to read the graph
as sequence.  Not a tool — a **read pattern**.

## Per M-self-application 4-level

- **Level 1**: ✅ 1 file (this read pattern doc) +
  1 commit.
- **Level 2 (rule itself)**: P11 + P13 + P14 + P20
  + P22 + P23 + P25 + P26 all applied.  8 rules.
- **Level 3 (memory / project structure)**: this
  doc IS the read pattern; cross-references
  existing L0/L1/L2 structure.
- **Level 4 (own operating behavior)**: future
  new agents reading this doc should follow the
  3-step pattern (L0 → L1 → L2) without
  over-reading cross-refs.

## See also

- `docs/PRINCIPLES.md` 类比联想段 (5 families)
- `docs/OPERATING_RULES.md` (M-rules for workflow)
- `docs/PRINCIPLES_DETAIL.md` (P20 + P22 detail)
- `AGENTS.md` "Read first" (parent reference)