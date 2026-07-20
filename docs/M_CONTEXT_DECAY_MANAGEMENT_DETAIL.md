# M-context-decay-management (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> context-decay-management段 (M-n 26).  Per
> P11 摘要+引用 + R6, this companion is
> required when the summary 段 references
> detailed strategy + worked examples.

**Origin**: per user message 2026-07-15 explicit
True问题 "记忆遗忘的问题" + user message "项目
上下文可能变长" + M_RULE_AUTHORING 3-condition
gate (6+ observed sites).

## Why this M-rule exists

User concern: project 上下文 变长 (long
context = noise) + agent 记忆遗忘 (memory
decay).

Per M-n 14 entropy dimension: 类比 = 熵减,
逻辑 = 熵增.  Memory is finite; context
grows; both decay patterns.

Per P29 主动 reduce context: agent should
not be passive about memory decay.

## 4 sub-steps (per user message 5 directives)

### Step 1: Detection

Identify when context is long:
- commit threshold (10+ commits since
  last analysis, per M-n 23 trigger)
- time threshold (1+ hour session)
- explicit decay signal (agent forgets
  prior M-rule / P-n)
- context length (tool result > 50KB)

### Step 2: Classification

Classify decay pattern (5-types per
summary段):

1. **Working memory short**: agent
   forgets prior turn within session.
   Common cause: too many distractions.
2. **Working memory overflow**: agent has
   too many in-context items. Common
   cause: many parallel tasks.
3. **Episodic retrieval fail**: agent
   can't recall past session via
   session_search. Common cause: no
   snapshot in Temp.
4. **类比 inaccessible**: agent doesn't
   find similar prior pattern. Common
   cause: rules 乱 / not codified.
5. **L0 rule dropped**: agent forgets a
   P-n / M-n rule. Common cause: rule
   not applied recently.

### Step 3: Compression (per P29)

Apply P29 主动 reduce context:
- (a) destroy redundant summaries (per
  M-n 18 destruction contract + sibling
  isolation)
- (b) compress to essence (per M-n 14
  compression primitive)
- (c) move detail to L2 companion (per
  P11 + R6)
- (d) split large doc (per M-n 19 file
  naming)

### Step 4: Refresh

Load from MEMORY.md + 类比 retrieval:
- (a) MEMORY.md reload (per M-self-
  application level 3)
- (b) inter-domain MCP search (per M-n 17
  Path 2)
- (c) re-read source docs (per M-n 17
  Path 1)
- (d) ask user (per M-n 21 sub-step 1)

## 5 decay patterns (per summary段 + worked examples)

| Pattern | Detect | Action | Worked example |
|---|---|---|---|
| Working memory short | Forget prior turn | M-n 25 Pattern E + M-n 21 | SUA c165-c167: forgot P-n count, refreshed via c167 LIFT |
| Working memory overflow | Many in-context | M-n 18 + P29 | SUA c165: PRINCIPLES.md 8329 → 7030 bytes (R5) |
| Episodic retrieval fail | session_search no result | M-n 17 Path 2 MCP | prior turns (c155 prior): used session_search for history |
| 类比 inaccessible | Class类比找不到 | M-n 14 类比 compression | SUA c110: 类比=topology (parallel + graph) |
| L0 rule dropped | Forget P-n | M-n self level 3 + MEMORY.md | SUA c183: codified M-n 25 message-pattern-recognition |

## 5 anti-patterns

- **Don't** let context grow unbounded
  (always compress per P29).
- **Don't** skip Pattern classification
  (5 patterns have different actions).
- **Don't** rely on session_search alone
  (use MCP Path 2 for inter-domain).
- **Don't** ignore MEMORY.md (level 3
  reload important).
- **Don't** over-engineer: simple
  destruction usually works.

## Relationship to other M-rules

- **M-n 14 (类比)**: provides compression
  primitive.
- **M-n 17 (Path 2)**: provides inter-domain
  MCP search.
- **M-n 18 (destruction)**: provides summary
  destruction contract.
- **M-n 23 (re-analysis)**: provides
  detection trigger (10+ commits).
- **M-n 24 (pace-continuity)**: reduces
  risk of working memory overflow.
- **M-n 25 (message-pattern-recognition)**:
  provides Pattern A-E matching.
- **P29 (reduce context)**: provides
  compression ethos.

## Self-application (per P28 recursion)

This L2 companion IS itself an example of
M-context-decay-management: you turn
"上下文可能变长" + "记忆遗忘" 5 directives
codified in OPERATING_RULES.md summary段
+ L2 companion, demonstrating P29
compression (move detail to L2) +
P22 case-3 (principle about how principles
behave).

## Cross-references

- `docs/OPERATING_RULES.md` § M-context-
  decay-management (M-n 26 main段)
- `docs/OPERATING_RULES.md` § M-n 14
- `docs/OPERATING_RULES.md` § M-n 17
- `docs/OPERATING_RULES.md` § M-n 18
- `docs/OPERATING_RULES.md` § M-n 23
- `docs/OPERATING_RULES.md` § M-n 24
- `docs/OPERATING_RULES.md` § M-n 25
- `docs/PRINCIPLES_FULL.md` "P29"段
- user message 2026-07-15 — origin
