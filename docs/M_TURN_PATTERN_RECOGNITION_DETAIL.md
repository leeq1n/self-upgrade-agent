# M-turn-pattern-recognition (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> turn-pattern-recognition段 (M-n 25).  Per
> P11 摘要+引用 + R6, this companion is
> required when the summary 段 references
> detailed worked examples + decision tree.

**Origin**: per user message 2026-07-15 explicit
ask "学习我发言思路这个也需要看看有没有
学习过" + M_RULE_AUTHORING 3-condition gate.

## Why this M-rule exists

user message (用户回合) often has 2-5 distinct
parts + 1+ 真问题 + 隐含 codify request.
Per M-self-application 4 levels (c18):
agent should:
- (L1) parse user message parts
- (L2) apply pattern (per 5 patterns below)
- (L3) update memory
- (L4) adjust own behavior

## 4 sub-steps (per M-self-application 4 levels)

1. **Parse turn (L1)**: identify all parts.
2. **Apply pattern (L2)**: recognize user message
   patterns.
3. **Update memory (L3)**: if new pattern
   observed, add to 7+ observed cases list.
4. **Adjust behavior (L4)**: for next turn,
   recognize pattern faster + apply correct
   M-rule (M-n 21/22/23/24).

## 5 observed user message patterns

### Pattern A: 2-3 parts + directive

**Structure**: 2-3 directives, no explicit
真问题, no 隐含 codify request.

**Example**: user message "M-n 21 + top-down 默认"
(prior turn).  2 parts: M-n 21 codify + top-
down 默认.

**Action**: apply M-n 12 + M-n 22 + direct
M-rule codification.

### Pattern B: 3-4 parts + 真问题

**Structure**: 3-4 directives + 1 explicit
真问题.

**Example**: user message "M-n 22 3W1H + 自顶向下"
(prior turn).  3 parts: 3W1H / 自顶向下 /
"继续按计划推进任务" 真问题.

**Action**: apply M-n 22 codify + 答 真问题.

### Pattern C: 5 parts + 真问题 + 隐含 codify

**Structure**: 5+ directives + 1+ 真问题 +
隐含 codify request.

**Example**: user message 2026-07-15 (5 parts:
规划 角度 / 方法 / 任务管理 / 记录 / 学习
思路).  真问题 = "学习我发言思路这个
也需要看看有没有学习过".

**Action**: this turn 实践 = codify M-n 25
(per M_RULE_AUTHORING 3-condition gate +
你 vision 主动).

### Pattern D: directive + 真问题 verify

**Structure**: 1+ directive + 1 explicit
真问题 that asks for verification (e.g.,
"对吧？" or "能做到吗？").

**Example**: user message "项目整洁 + skill 跟 SUA
规范 + agent 行为规范 2 来源 + 做到了吗？"
(prior turn).

**Action**: M-n 21 答 (P17 老实说) + apply
directive.

### Pattern E: implicit + 主动

**Structure**: 1 short directive (e.g.,
"按计划继续推进") + 隐含 主动 mode.

**Example**: user message "按计划继续推进任务"
(many turns).  Implies agent should
autonomously continue per PLAN.

**Action**: M-n 24 (pace-continuity) +
commit + continue per PLAN + no verbose
ending段.

## Per-turn-type decision tree

```
Q1: user message has explicit 真问题?
├── Yes → M-n 21 (ask-or-infer-mark-guess)
│         + 答 (P17 老实说)
│         + verify per M-n 22 3W1H
└── No  → M-n 24 (pace-continuity) + continue

Q2: user message has 隐含 codify request?
├── Yes → M_RULE_AUTHORING 3-condition gate
│         + codify as new M-n or P-n
└── No  → direct execution

Q3: user message has 隐含 verification ask?
├── Yes → M-n 17 Path 1 (re-read) + 答
└── No  → continue
```

## 5 anti-patterns

- **Don't** ignore user message 真问题
  (P17 老实说 requires 答).
- **Don't** confuse user message 真意 with
  surface directive (apply M-n 22 3W1H
  first).
- **Don't** apply only L1 (parse) without
  L2-L4 (apply pattern + memory + behavior).
- **Don't** codify new M-n without
  M_RULE_AUTHORING 3-condition gate.
- **Don't** ignore framework-agnostic (per
  M-n 20) when codifying.

## 7 worked examples

1. c18 (M-self-application 4 levels)
2. c92 (M-n 12 terminology-clarity,
   per user message "撞到一起" → "replan")
3. c98 (M-n 14 类比 vs 逻辑, per user message
   "类比 是 抽象 + 归纳")
4. c106 (M-n 17 re-read, per user message
   "经常 修改 文件 需要 确认")
5. c118 (M-n 21 ask-or-infer-mark-guess,
   per user message "问 + 推理 + 标注猜测")
6. c122 (M-n 22 3W1H-think-first, per
   user message "自顶向下 之前 需要 3W1H")
7. user message 2026-07-15 (this turn = 7th,
   Pattern C)

## Relationship to other M-rules

- **M-self-application**: this M-rule IS
  level 4 (own behavior) application
- **M-n 12**: refine user message terms
- **M-n 14**: 类比 (find similar user message) vs
  逻辑 (parse 1 turn)
- **M-n 17**: re-read before answering
- **M-n 21**: 答 真问题
- **M-n 22**: find user message 真意
- **M-n 23**: re-analyze at 最终目标
- **M-n 24**: pace-continuity (don't break
  rhythm)

## Self-application (per P28 recursion)

This L2 companion IS itself an example of
M-self-application level 4: codifying 你
turn pattern recognition so future agents
can apply it.

## Cross-references

- `docs/OPERATING_RULES.md` § M-self-
  application
- `docs/OPERATING_RULES.md` § M-n 12
- `docs/OPERATING_RULES.md` § M-n 14
- `docs/OPERATING_RULES.md` § M-n 17
- `docs/OPERATING_RULES.md` § M-n 21
- `docs/OPERATING_RULES.md` § M-n 22
- `docs/OPERATING_RULES.md` § M-n 23
- `docs/OPERATING_RULES.md` § M-n 24
- user message 2026-07-15 — origin
