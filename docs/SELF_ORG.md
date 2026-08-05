# Project self-organization principle (per user meta-rule 2026-07-14)

> L0: Codification of "project should self-organize
> top-down without human prompting" as a first-class
> principle.  Per user meta-rule 2026-07-14: "未来
> 我不说的话, 这项目会自己整理原则和项目为顺序规范
> 吗?".
> Last P20-verified: 2026-07-14 (initial codification)

## What this doc is

Per M_RULE_AUTHORING 3-condition gate evaluation
(2026-07-14):

- **Reusable 3+ sites**: ✅ (any project with
  recurring commits can apply)
- **Triggerable fire-point**: ✅ (commits, audits,
  plan iterations)
- **3+ occurrences observed**: ✅ (commit 50
  audit + commit 41 P25 step 7 + commit 44
  class framework = 3+ explicit applications)

Per the 3-condition gate: **can codify as
full rule** now.

## Per P-n vs M-* boundary 3-case test (per c33)

- **"Project self-organizes top-down"** = about
  state invariant (what should be true at
  handoff) = **P-n (regular case 1)**
- **"Agent should trigger self-organization"** =
  about agent behavior = **M-*** (separate rule)

**This doc codifies the P-n** (state invariant).
The M-* trigger rule is in commit 53.

## P27. Project self-organization (proposed — candidate for PRINCIPLES.md lift)

**Trigger** (when this principle should fire):

- After every commit (post-commit phase)
- After every P-n / M-* modification
- After every doc reorganization
- After every parent verification (SUMMARY_LIFECYCLE)
- When project state entropy is detected (per
  c44 audit finding)

**Action** (what the principle requires):

1. **Top-down check**: project docs should be in
   L0/L1/L2 layers (per P20).  Fresh agent can find
   any doc by:
   - Reading AGENTS.md "Read first" (or "Read
     conditionally" for less-frequent docs)
   - Following cross-refs from L0 to detail

2. **类比 grouping check**: principles, docs, and
   M-rules should be grouped by operational
   essence (per c44 framework).  Related content
   should be near each other in the file or in
   cross-referenced files.

3. **Numerical / logical ordering check**: P-n
   sections, M-rule definitions, and doc sections
   should be in numerical or logical order (not
   insertion order).  Per c42 reorder.

4. **Cross-ref integrity check**: every doc has
   parent + sibling cross-refs.  No orphan nodes
   (per P13).  No forward refs without backward
   refs.

5. **Cap compliance check**: ≤ 7KB summary,
   > 7KB has _DETAIL companion.  ≤ 300 lines
   summary (per R5 + R8).

6. **L0 line + Last P20-verified**: every doc
   has both (per R9 + R10).

7. **Inductive summary check**: every doc with
   multiple sub-sections should have a "Inductive
   summary"段 or table that synthesizes the
   sub-sections (per P22 step 3 + c43 + c44).

**Anti-patterns** (what NOT to do):

- **Don't wait for user prompting**: this
  principle is the agent's default behavior.
  Per user meta-rule: "未来我不说的话, 项目
  会自己整理".
- **Don't do ad-hoc fixes**: each fix should
  follow P25 6-step + P20 + P11 + P13 + P7.
- **Don't add new structure without evaluating
  existing**: per P7 奥卡姆 + c50 audit (some
  P-n may be redundant).
- **Don't skip self-audit for "obvious" tasks**:
  obvious is where gaps hide (per c26 + c35).

**实操 (L2)**: per commit + per P-n modification
+ per batch end, apply the 7 checks above.

**Self-application**:

- This principle applies to itself: when P27 is
  modified, the 7 checks must be re-applied.
- P27 fires for **all other P-n** (it's a
  meta-principle about principle organization,
  per P22 case 3 of boundary test).
- P27 is NOT triggered for **M-* rule** additions
  (M-* are about agent behavior, not project
  state).  But P25 + P20 still apply to M-*.

## Why this principle matters (per user meta-rule)

Per user 2026-07-14: "未来我不说的话, 这项目会
自己整理原则和项目为顺序规范, 相关的内容在一起,
自顶向下分治的结构吗?"

This principle codifies the **default expectation**:
the project should self-organize via codified rules,
not via user prompting.  The codification gives
the agent a **triggerable** (per M_RULE_AUTHORING
3-condition gate) + **reusable** (per 3+ sites)
+ **observed** (3+ times) rule to apply.

Before this codification: P22 stuck→plan + P25
6-step + P20 progressive disclosure + P26 fresh-
agent simulation were all individual rules, but
**no rule said "the project should self-organize"**
explicitly.  P27 IS the explicit "the project
should self-organize" rule.

## P26 fresh-agent simulation (post-P27 codification)

| Discovery step | Pre-P27 | Post-P27 |
|---|---|---|
| Reads P27段 in PRINCIPLES.md | ❌ absent | ✅ explicit self-organization principle |
| Knows 7-check framework | ⚠️ implicit (c50 audit only) | ✅ codified in P27 |
| Knows trigger conditions | ⚠️ must recall from M-self-audit | ✅ explicit list |
| Knows anti-patterns | ⚠️ implicit | ✅ explicit list |
| Can apply on own initiative | ❌ requires user prompt | ✅ triggered by commit/P-n modification |

Fresh-agent simulation **PASS**.

## Per P22 step 3 self-application

Per P22 step 3 ("找 rule 之间的共性"): P27 IS P22
step 3 applied to the project as a whole (vs just
P-n).  P22 is the general principle; P27 is its
project-level application.

## Per M_RULE_AUTHORING

3-condition gate (all 3 satisfied):
- 3+ sites: ✅
- Triggerable: ✅
- 3+ observed: ✅ (c50, c41, c44 explicit + c45
  implicit + c47 implicit)

Codify as **P27** (regular P-n, case 1 of boundary
test).

## Per task-planning-order meta-rule

Per user "如果发现任务对其他任务可能有影响，就重新
计划整理一下" (2026-07-14 follow-up): P27 affects
**all future commits** (every commit should apply
P27 checks), so commit 53+ will codify the M-*
trigger (so agent can apply P27 on own initiative).

## Open question: M-* trigger (commit 53)

Per "项目 self-organize without user prompting" —
P27 is the state invariant, but the M-* trigger
("when should agent apply P27?") is separate.
Per P22 case 3 boundary test:

- **M-* candidate**: "before commit, apply P27
  7-check; after commit, apply P27 again".  This
  is agent behavior.

Commit 53 (planned) will codify the M-* trigger
rule.  Per P25 step 5 impact analysis, M-* trigger
may need:
- New trigger phrase for M-self-audit
- M-task-summary check
- Parent verification ritual

Per "1 个 1 个来" + P7 奥卡姆: don't implement M-*
trigger in this commit.  Commit 52 = P27 proposal
+ documentation only.

## See also

- `docs/PRINCIPLES.md` class framework (c44)
- `docs/OPERATING_RULES.md` M-self-audit (operational rule)