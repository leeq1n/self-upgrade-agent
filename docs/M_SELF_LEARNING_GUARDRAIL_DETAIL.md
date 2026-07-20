# M-self-learning-guardrail (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` §
> M-self-learning-guardrail段 (M-n 32).
> Per P11 摘要+引用 + R6.

**Origin**: per 你 vision 2026-07-15
explicit directive: "新 agent 还有 可能
改 + skill 修改 都需要 在 一开始 就 约束
好 + 应该 自动 学习 更新 + 希望 项目 里
自动学习 相关的 功能 还在".

## 4-level self-application (per M-n 2)

### Level 1 (literal): apply M-rule as written

- Read M-n 32 main段
- Apply 5 modification guardrails verbatim
- Verify enforcement mechanism

### Level 2 (analogical): apply M-rule by analogy

- "ESLint rule" → M-n 32 guardrail (like
  ESLint enforces code style)
- "API contract" → 5 guardrails (like API
  contracts enforce input/output)

### Level 3 (meta-level): apply M-rule to itself

- M-n 32 = guardrails for M-n (rules about
  rules) = META-level
- Self-referential = per P22 case-3 (how
  should principles behave case-3)

### Level 4 (recursive): apply M-rule recursively

- M-n 32 modifies M-n 32 (guardrails about
  guardrails) = META-META
- Per P28 recursion + P28 self-application

## 5 modification guardrails (worked examples)

### Guardrail 1: Cite P-n or M-n

**Trigger**: every commit message

**Current enforcement**: commit-msg hook
whitelist P1-P29 (per c175 + c217)

**Worked example**:
- ✅ PASS: `docs(...): add foo (P11, M-n
  18)` (cites P-n + M-n)
- ❌ FAIL: `docs(...): add foo` (no P-n
  reference)

### Guardrail 2: R5 ≤ 7168 bytes

**Trigger**: docs L0/L1 files (per R5)

**Current enforcement**: manual `wc -c`
pre-commit check

**Worked example**:
- ✅ PASS: 6000 bytes (≤ 7168)
- ❌ FAIL: 9000 bytes (> 7168, R5 violation)

### Guardrail 3: Cross-ref check

**Trigger**: file edits that drift
cross-references

**Current enforcement**: manual review per
M-n 20 + P14 docs stay current

**Worked example**:
- ✅ PASS: When SUA M-n 30 codify, also
  update SUA AGENTS.md + skill
  SKILL_DETAIL.md (per c213 + c219)
- ❌ FAIL: When SUA M-n 31 codified but
  forgot to update skill SKILL_DETAIL.md

### Guardrail 4: Acceptance protocol

**Trigger**: claim "task done" / "all pass"

**Current enforcement**: per M-n 29
5-step protocol

**Worked example**:
- ✅ PASS: "✅ Task done, per M-n 29 Step
  5 + user message directive 2" (explicit notify)
- ❌ FAIL: "task done" without explicit
  notification

### Guardrail 5: Update order rule

**Trigger**: SUA change (P-n, M-n, etc.)

**Current enforcement**: per M-n 30
Priority 5 (SUA → skill-incubator → skill)

**Worked example**:
- ✅ PASS: SUA c222 M-n 30 codified → 
  skill-incubator c224 + skill c225 (3
  projects all updated)
- ❌ FAIL: SUA change without
  propagation to 2 sibling projects

## Auto-learning functionality status (per user message)

### Verified EXISTS (per audit 2026-07-15):

| Function | Where | Status |
|---|---|---|
| M-self-application (M-n 2) | OPERATING_RULES.md § M-n 2 | ✅ EXISTS (4 levels) |
| M-self-audit (M-n 3) | OPERATING_RULES.md § M-n 3 | ✅ EXISTS (6 step + step 7) |
| M_RULE_AUTHORING (M-n 4) | OPERATING_RULES.md § M-n 4 | ✅ EXISTS (3-condition gate) |
| M-context-decay-management (M-n 26) | OPERATING_RULES.md § M-n 26 | ✅ EXISTS (4 sub-steps) |

### NOT explicit (gaps):

| Function | Status |
|---|---|
| "auto-learning" explicit 段 | ⚠️ NOT EXPLICIT (this 段 fills gap per c234) |
| "self-improve" 段 in PRINCIPLES.md | ⚠️ NOT EXPLICIT |
| "新 agent 修改 guardrails" 段 | ⚠️ NOT EXPLICIT (this 段 fills gap per c234) |

### Coverage after c234:

After this commit (c234), project
auto-learning IS explicit + 5 guardrails IS
codified.  Future new agents will have:
- Auto-learning 4 levels documented
- 5 modification guardrails documented
- M_RULE_AUTHORING 3-condition gate
- commit-msg hook enforcement (P1-P29)

## Relationship to other M-n

- **M-n 2** (self-application): Level 4
  recursion
- **M-n 3** (self-audit): step 7 verify-
  before-edit
- **M-n 4** (RULE_AUTHORING): 3-condition
  gate
- **M-n 26** (context-decay-management):
  re-read + 类比归纳
- **M-n 30** (knowledge-context-trade-off):
  Update order rule
- **M-n 29** (acceptance-protocol):
  explicit notify

## Cross-references

- `docs/OPERATING_RULES.md` § M-self-
  learning-guardrail (M-n 32 main段)
- `docs/OPERATING_RULES.md` § M-n 2 / M-n
  3 / M-n 4 / M-n 26 / M-n 29 / M-n 30
- user message 2026-07-15 — origin (新 agent
  修改 约束 + 自动学习)