# M-observe-think-execute (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-observe-
> think-execute段.  Per P11 摘要+引用 + R6, this
> companion is required when the summary rule段
> describes a multi-stage chain.  Load when: agent
> needs to perform a task with principled meta-level
> structure.

## Why this L2 doc exists

The OPERATING_RULES.md § M-observe-think-execute
段 (c100, per 你 turn "观察-思考-执行链") provides
the 6-stage chain.  This L2 doc provides worked
examples for each stage, decision tree, and how this
M-rule relates to M-n 14 (two-track reasoning) and
M-n 16 (this rule).

## The 6-stage chain (detailed)

### Stage 1: 观察 (observe)

**Action**: gather raw data, observe current state,
identify changes.

**Output**: a list of observations + key insights.

**When to skip**: never (observation is the
foundation).

**Worked example**: c102 (L2 companion for M-n 13)
started with observation: "M-n 13 (c97) has 段 in
OPERATING_RULES.md but no L2 companion."  This
observation triggered c102.

### Stage 2: 思考 (think 1) — 归纳总结 + 判断是否进入规划

**Action**: extract pattern from observations
(induction).  Decide if planning is needed.

**Output**: pattern summary + decision (plan or not).

**When to skip**: rarely (some tasks are simple
enough to skip planning, per M-n 16 chain
modification).

**Worked example**: c102 thinking was: "M-n 13 has
4 sub-steps, decision tree, naming convention.  This
warrants L2 companion (per P11 + R6).  Plan: write
L2 doc with worked examples."

### Stage 3: 执行 (execute 1) — 实际规划

**Action**: decide what to do, what memory is needed.

**Output**: plan + memory requirements.

**Worked example**: c102 plan: "Write M_LAYER_EXTENSION.md
with Q1-Q4 decision tree + 4 worked cases + 4 anti-
patterns + relationship to other M-rules.  Memory
needs: nothing new (memory 7 has M-n 13 already)."

### Stage 4: 思考 (think 2) — 怎么行动, 需要什么记忆

**Action**: identify similar past actions + memory
entries to use.

**Output**: action plan + memory references.

**Worked example**: c102 thinking: "M_TERMINOLOGY_CLARITY
(c93) used similar pattern.  Apply same structure:
Why + Trigger + Action + Anti-patterns + Relationship
+ Cross-references."

### Stage 5: 执行 (execute 2) — 调用记忆

**Action**: apply past patterns + memory entries.

**Output**: draft content based on past patterns.

**Worked example**: c102 applied c93's structure +
memory 7's M-n 13 entry.

### Stage 6: 思考 + 执行 (think 3 + execute 3) — 修改、运行代码

**Action**: actual code modification + verification.

**Output**: commit + verify (7-check + P25 6-step).

**Worked example**: c102 wrote M_LAYER_EXTENSION.md,
ran 7-check, ran P25 6-step, committed.

## How this M-rule relates to M-n 14 (two-track)

Per M-n 14, both tracks (类比 + 逻辑) compose:

- **Track 1 (类比)**: stages 1 (observe) + 2 (think 1
  induction) + 4 (think 2 类比 to past)
- **Track 2 (逻辑)**: stage 3 (plan, sequential) + 5
  (apply, sequential) + 6 (commit, sequential) + 6's
  thinking (P25 6-step 逻辑)

Both tracks interleaved across the 6 stages.

## When NOT to use (anti-patterns)

### Anti-pattern 1: Skip 观察 (start with 思考 or 执行)

Without observation, the agent is guessing.  Per P7
奥卡姆 + P5 verify, observation is mandatory.

### Anti-pattern 2: Skip 思考 between 执行 stages

Each 执行 should be preceded by 思考.  Skipping
思考 leads to mechanical execution (trap signal,
per memory 9).

### Anti-pattern 3: Conflate 思考 and 执行

They are distinct stages per 你 turn.  Don't merge
them.

### Anti-pattern 4: Use for trivial tasks

For 1-line changes (low-risk per 修订 L4 boundary
(a)), the 6-stage chain is over-engineering.  Use
when high-stakes (mid-risk or high-risk).

## Worked example: c100 M-n 16 (this rule)

- **观察**: 你 turn "观察-思考-执行链" + essence
  statement.
- **思考-1**: project already has M-n 14 (2 tracks);
  M-n 16 is higher-level 6-stage chain using both.
  归纳总结: this is "higher-level" per 你 turn.
- **执行-1**: plan: write M-n 16 段 in OPERATING_RULES.md
  with 6-stage chain + essence + relationship.
- **思考-2**: similar past: M-n 14 (c98) structure;
  apply same pattern + add higher-level position note.
- **执行-2**: write 段 based on c98 structure + 你 turn.
- **思考-3 + 执行-3**: 7-check + P25 6-step + commit.

## Relationship to other M-rules + P-n

- **M-n 11 (sub-project)**: this chain applies
  within sub-project lifecycle (Decide → Spawn →
  Set goal → Return → Accumulate).
- **M-n 12 (terminology-clarity)**: stage 1 (观察)
  may detect unclear terms.
- **M-n 13 (layer-extension)**: stage 6 (修改、运行
  代码) may add L0.5/L2.5/L3.
- **M-n 14 (two-track-reasoning)**: foundational;
  this chain uses both tracks.
- **M-n 15 (principle-reordering)**: stage 4 (思考-2)
  may invoke M-n 15.
- **P22 step 3**: stage 2 (思考-1) applies P22.
- **P25 6-step**: stage 6 (思考-3) applies P25.
- **P28 (recursion)**: this chain is recursion-level
  (apply to self).

## Self-application (per P28 recursion)

This L2 doc IS the chain applied to itself: c100
created M-n 16 段 via 6-stage chain, then c102-c103
created L2 companions via 6-stage chain.  Recursion
to self.

## Cross-references

- `OPERATING_RULES.md` § M-observe-think-execute —
  the L0/L1 段 (in SUA)
- `OPERATING_RULES.md` § M-n 14 — two-track foundation
- `OPERATING_RULES.md` § M-n 11/12/13/15 — related
- `docs/PRINCIPLES.md` — P22 + P25 + P28
- 你 turn 2026-07-15 — origin
