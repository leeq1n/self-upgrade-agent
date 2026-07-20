# M-pre-task-scan (full text)
Last P20-verified: 2026-07-16

> L0: L2 detail for `OPERATING_RULES.md` §
> M-pre-task-scan段 (M-n 34).  Per P11 摘要+引用
> + R6, this companion provides worked examples
> for the 4 sub-steps + scan output template.

**Origin**: per user message 2026-07-16 "我跟你说
问题的时候，你需要找办法，避免下一次还
出现一样的/相似的问题. 我不希望每次都
跟你说了问题你才从项目里找对应条目，你
应该自主阅读学习".

## Why this L2 doc exists

M-n 34 L1 段 in `OPERATING_RULES.md` defines
the 4 sub-steps.  This L2 companion provides:

1. **Worked examples** of the 4 sub-steps
   applied to real tasks
2. **Scan output template** for plan +
   commit message
3. **Decision tree** for "which P-n / M-n
   to apply" given a user message pattern
4. **Anti-pattern case studies** (what scan
   misses when applied incorrectly)

## Worked example 1: c237 M-n 33 codify (narrative-as-spec)

Applying M-n 34 to the task "codify M-n 33
narrative-as-spec based on user message '联想 分析
类比 看 性价比'":

**Sub-step 1**: Read AGENTS.md (already done
via Pre-task scan段).
**Sub-step 2**: Scan P-n / M-n:

| P-n / M-n | Applicable? | Reason |
|---|---|---|
| P25 6-step | YES | Codifying new M-n requires P25 |
| P11 摘要+引用 | YES | L1 + L2 摘要 + reference pattern |
| M-n 14 (two-track) | YES | 联想 + 分析 = two-track |
| M-n 16 (observe-think-execute) | YES | Standard 6-stage chain |
| M-n 22 (3W1H) | YES | What/Why/Who/How = M-n 33 trigger / action / 4 elements / 5 relationship |
| M-n 25 (message-pattern) | YES | user message explicit "联想 分析 类比" = Pattern C (5 parts + 真问题 + 隐含 codify) |
| M-n 30 (knowledge-context trade-off) | MAYBE | 4-priority + flat vs layered decision |
| P-n 1-24 (other) | NO | Not directly applicable to codification task |
| M-n 1-32 (other) | NO | Standard task, no special rule |

**Sub-step 3**: Apply 5 primitives:
- **Analyze**: 任务是 codify M-n 33 = 1 new
  M-n + 1 L2 companion doc + 1 commit.
- **Reason**: 为什么 this codify? user message
  explicit directive; M_RULE_AUTHORING
  3-condition gate met (3+ occurrences).
- **联想**: 类似 prior pattern = c100 M-n
  16 codify (same 6-stage chain + L2
  companion structure).
- **归纳**: general pattern = "codify
  M-n" = 1 L1 段 + 1 L2 段 + 1 commit
  + AGENTS.md update.
- **总结**: 1 L0 = M-n 33 codify for
  narrative-as-spec primitive.

**Sub-step 4**: Document scan result in
commit message — list 3-5 most relevant
(P25, P11, M-n 14, M-n 16, M-n 22) + 1-line
reasons.

## Worked example 2: this very commit (M-n 34 codify)

Applying M-n 34 to itself (per P28 recursion):
"codify M-pre-task-scan as M-n 34":

**Sub-step 1**: Read AGENTS.md Pre-task scan段
(just committed, line 9-38).
**Sub-step 2**: Scan P-n / M-n:

| P-n / M-n | Applicable? | Reason |
|---|---|---|
| P11 摘要+引用 | YES | L1 + L2 + reference pattern |
| P25 6-step | YES | Codifying new M-n requires P25 |
| P28 (recursion) | YES | M-n 34 is P28 applied to discovery |
| M-n 13 (layer-extension) | YES | L0 surface (AGENTS.md) must expose M-n 34 |
| M-n 14 (two-track) | YES | Scan uses both tracks |
| M-n 16 (observe-think-execute) | YES | Scan = Stage 1-2 |
| M-n 22 (3W1H) | YES | Standard 3W1H |
| M-n 25 (message-pattern) | YES | user message Pattern D + B |
| M-n 31 (task-lifecycle) | YES | Phase 1 task-init integrates scan |
| M-n 32 (self-learning-guardrail) | YES | Anti-pattern is "skip scan, rely on memory" |
| M-self-audit | MAYBE | M-n 34 is proactive (not reactive post-audit) |

**Sub-step 3**: Apply 5 primitives (already
done in this doc; this is meta-self-application).
**Sub-step 4**: Document scan result in
commit message (this commit) + L2 companion
(this file).

## Scan output template

When agent runs M-n 34 scan, output the result
in this format (per P11 摘要+引用):

```
## M-n 34 scan result

Most relevant P-n / M-n (3-5):

1. [P-n or M-n name + number]: [1-line reason]
2. [P-n or M-n name + number]: [1-line reason]
3. [P-n or M-n name + number]: [1-line reason]

5 primitives applied:
- Analyze: [finding]
- Reason: [finding]
- 联想: [finding]
- 归纳: [finding]
- 总结: [1-paragraph L0]

Anti-patterns avoided (per M-n 32):
- [x] Did not skip scan
- [x] Did not rely on memory alone
- [x] Did not treat scan as one-time
```

## Decision tree: "which P-n / M-n to apply"

| user message pattern | Scan priority |
|---|---|
| Pattern A (2-3 parts + directive) | M-n 22 3W1H + M-n 12 + direct execute |
| Pattern B (3-4 parts + 真问题) | M-n 22 + M-n 21 答 (P17 老实说) + M-n 25 |
| Pattern C (5 parts + 真问题 + 隐含 codify) | M-n 25 + M_RULE_AUTHORING 3-condition gate |
| Pattern D (directive + verify) | M-n 21 答 + apply directive |
| Pattern E (implicit + 主动) | M-n 24 + M-n 28 4-condition self-audit + continue |

## Anti-pattern case studies

### Case 1: Skip scan, rely on memory

user message: "fix this bug"
Agent: applies memory of past bug fixes, ignores
P5 (verify before commit) + P17 (老实说) +
P22 (when stuck→plan).
**Result**: bug "fixed" but tests not run;
P5 violation; task declared done without
M-n 29 5-step.  Per M-n 34 sub-step 2, scan
would have surfaced P5 + P17 + M-n 29.

### Case 2: Scan only 1-2 P-n / M-n

user message: "refactor this doc"
Agent: scans only P11 (摘要+引用), ignores
P20 (L0 line) + P14 (docs stay current) + M-n
19 (file-naming).
**Result**: refactored but L0 line missing +
file name inconsistent.  Per M-n 34 sub-step 2,
scan must cover ALL P-n / M-n, not 1-2.

### Case 3: Treat scan as one-time

Agent runs scan at session start, never
re-scans.  Mid-session user message introduces
new context (M-n codification).
**Result**: mid-session task violates P25 6-step
because agent didn't re-scan.  Per M-n 34
trigger, scan is per user message (not session-once).

## Self-application (per P28 recursion)

This L2 doc IS M-n 34 applied to itself.  The
recursive structure:
- M-n 34 L1 段 defines 4 sub-steps
- M-n 34 L2 段 (this file) provides worked
  examples using M-n 34 on itself
- M-n 34 trigger is "any user message" — so this
  doc itself was written by applying M-n 34

## Cross-references

- `docs/OPERATING_RULES.md` § M-pre-task-scan
  (M-n 34) — L1 段
- `AGENTS.md` § "Pre-task scan" — L0 surface
- `AGENTS.md` § "Read first" item 7 (M-n 34
  addition)
- `docs/M_SELF_AUDIT.md` — reactive complement
- `docs/M_SELF_LEARNING_GUARDRAIL_DETAIL.md` —
  M-n 32 (modification guardrails, 5 rules)
- `docs/OPERATING_RULES.md` § M-knowledge-
  context-trade-off (M-n 30) — Priority 1
  (knowledge 充足)
- user message 2026-07-16 "自主阅读学习" — origin
