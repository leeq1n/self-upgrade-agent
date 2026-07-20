# M-narrative-as-spec (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` §
> M-narrative-as-spec段 (M-n 33).
> Per P11 摘要+引用 + R6.

**Origin**: per user message 2026-07-15 autonomy
directive ("如果能直接做决定就直接做") +
联想 analytical insight per M-n 14 + M-n
21 (ask-or-infer-mark-guess).

## 3-primitive decision tree

### Primitive 1: Parse

**Trigger**: agent receives user message.

**Methods**:
- M-n 25 (turn-pattern-recognition) —
  classify into 5 patterns A-E
- user message history analysis
- 你 vision keywords extraction

**Output**: user message 真意 summary.

### Primitive 2: Structure

**Trigger**: user message parsed 真意 clear.

**Methods**:
- M-n 22 (3W1H-think-first) — apply
- M-n 14 (类比 entropy) — abstract +
  induction
- M-n 23 (periodic re-analysis) — re-analyze
  if needed

**Output**: structured sub-tasks + approach.

### Primitive 3: Codify (or Execute)

**Trigger**: sub-tasks structured.

**Methods**:
- M-n 28 (plan-conditional) — 4-condition
  self-audit
- M-n 32 (self-learning-guardrail) — 5
  guardrails check
- M-n 31 (task-lifecycle) — 4-phase execute
- M-n 30 (knowledge-context-trade-off) —
  update order rule

**Output**: executed decision OR asked 你
(if decision ambiguous).

## Worked examples (c237 self-application)

Apply M-n 33 to user message "如果能直接做决定
就直接做 + 联想 valuable insight":

### Phase 1: Parse (user message 真意)

- user message 真意 = "autonomy + 联想"
- user message 真意 per M-n 25 = Pattern E
  variant + 你 vision deep + Pattern D
  variant

### Phase 2: Structure (3W1H)

- What: codify M-n 33
- Why: Insight A HIGH 性价比 + LOW risk
- Who: future agents
- How: 1 段 + L2 companion + AGENTS update +
  propagation

### Phase 3: Codify (autonomous decision)

- Q1 (agent 不确定): NO (clear 3W1H)
- Q2 (plan 混乱): NO
- Q3 (重大调整): YES (new M-n 33 codify)
- Q4 (user explicit): YES (user message
  "如果能直接做决定就直接做")

→ enter 自主 mode + execute (per M-n 28 +
M-n 32 5 guardrails).

### Result

M-n 33 codified in OPERATING_RULES.md + L2
companion created + AGENTS.md updated +
skill downstream propagation per M-n 30.

## Autonomy decision framework (per 你 vision)

### When to act autonomously (per M-n 33):

| Criterion | Trigger |
|---|---|
| 你 vision alignment clear | YES |
| HIGH 性价比 + LOW risk | YES |
| M_RULE_AUTHORING 3-condition met | YES |
| M-n 32 5 guardrails satisfied | YES |
| user message 真意 Parse + Structure clear | YES |

### When to ask 你 (NOT autonomous):

| Criterion | Trigger |
|---|---|
| 你 vision ambiguity | YES (need clarification) |
| Multiple valid options | YES (selection needed) |
| HIGH risk + you impact | YES (need 你 approval) |
| user message 真意 conflict with prior turns | YES (resolve conflict) |
| 你 vision impact MAJOR (e.g., vision drift) | YES (need 你 vision reframe) |

## Relationship to other M-n

- **M-n 25**: parses user message 5 patterns
- **M-n 22**: 3W1H-first structure
- **M-n 21**: ask-or-infer-mark-guess (fallback)
- **M-n 28**: 4-condition self-audit
- **M-n 31**: 4-phase lifecycle
- **M-n 32**: 5 modification guardrails
- **M-n 30**: priority 5 update order rule

## Cross-references

- `docs/OPERATING_RULES.md` § M-narrative-as-
  spec (M-n 33 main段)
- `docs/OPERATING_RULES.md` § M-n 21 / M-n 22
  / M-n 25 / M-n 28 / M-n 30 / M-n 31 / M-n 32
- user message 2026-07-15 — origin (autonomy
  directive + 联想 insight)