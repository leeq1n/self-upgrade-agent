# M-acceptance-protocol (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> acceptance-protocol段 (M-n 29).  Per P11
> 摘要+引用 + R6, this companion is required
> when the summary段 references detailed
> 5-step protocol + 验收 report template +
> cycle loop.

**Origin**: per 你 turn 2026-07-15 explicit
6 parts + 你 implicit research directive
(project acceptance + agent acceptance +
harness references).

## 5-step protocol (detailed)

### Step 1: Design 验收 角度 + 要求

Per M-n 22 3W1H first + NASA SWE-034
("Formulation phase") + Claude
acceptance-criteria-verification skill:

| 角度 | 验收 criteria examples |
|---|---|
| **functional** | 所有 functional requirements met |
| **performance** | latency / throughput / memory OK |
| **兼容性** | framework-agnostic + 跨 project sync |
| **安全** | no PII / no leak / no unsafe patterns |
| **维护性** | docs stay current + R5/R6/R8 PASS |
| **user-facing** | L0 + L1 + L2 + cross-refs visible |
| **framework-agnostic** | Hermes + Codex + Claude Code 全部 |
| **跨项目 sync** | SUA ↔ skill ↔ skill-incubator ↔ KG |
| **R1-R12** | ALL PASS (per c173 VERIFICATION.md) |
| **P-n compliance** | 25 P-n all cited + applied |
| **M-n compliance** | 28 M-n all applied per context |
| **P29 self-application** | agent 主动 reduce context |
| **项目 整洁度 (per 你 turn 2026-07-15 reminder)** | 路径 + 命名 + 文档结构 consistent (per M-n 19 file-naming-convention + c149-c151 .gitignore + c191 整理 + c115 整理 process) |
| **新 agent 可读性 (per 你 turn 2026-07-15 reminder)** | 项目 内容 可读 + 充分 (per M-n 20 agent-discoverability + P26 fresh-agent + VERIFICATION.md per c193 + 你 turn prior 7 docs in sync) |

### Step 2: Execute 验收 (5 logic primitives per 你 turn)

Per 你 turn Part 3 explicit: "按照规范分析、
推理、联想、归纳、总结的逻辑过一遍完整的
项目".  This is 5 primitives from M-n 16 +
M-n 14 + M-n 25 + M-n 26:

1. **Analyze** (per M-n 16 observe-think-
   execute stage 1):
   - What: 任务 IS what?
   - Boundaries: 范围 (per R11)
   - Components: 哪些 part / file / commit?
2. **Reason** (per M-n 16 stage 2 + M-n 22
   3W1H):
   - Why: 为什么 这样设计?
   - Trade-offs: what sacrificed?
   - Alternative: what else considered?
3. **联想 (analogize)** (per M-n 14 class比
   + M-n 17 Path 2 inter-domain):
   - 类似 prior pattern in SUA / skill /
     skill-incubator / KG?
   - MCP search (per c94 MCP-first
     verification pattern) for prior art?
4. **归纳 (induct)** (per M-n 14 induction
   + M-n 18 recursive summary):
   - General pattern from specific?
   - What can be applied to other 任务?
5. **总结 (summarize)** (per M-n 26
   compression + M-n 18 destruction):
   - Synthesize into 1-paragraph L0
   - Apply 节点 生命周期 (destroy redundant
     details)

### Step 3: Validate 验收 condition

Per 你 turn Part 4 "确认没问题":

| Check | PASS criteria |
|---|---|
| All acceptance criteria | 全部 PASS (no FAIL / PARTIAL) |
| 5 primitives applied | All 5 used |
| Evidence recorded | test output / commit hash / file size |
| R1-R12 ALL PASS | Per c173 + per latest VERIFICATION.md |
| P-n compliance | All 25 P-n applicable cited |
| M-n compliance | All applicable M-n applied |
| Framework-agnostic | All 4 frameworks (Hermes/Codex/Claude Code/Cursor) |
| P17 老实说 | Don't claim green when yellow |

### Step 4: If FAIL → 新 任务 cycle

Per 你 turn Part 5: "如果验收没通过，就需
要当作新任务继续修改（每次你认为做完任务
都需要验收，没通过就修复，修复完再测，循环）":

1. Create new task in PLAN_DETAIL
2. Re-execute fix
3. Re-verify (回到 step 2)
4. Loop until ALL PASS

### Step 5: If PASS → 明确 通知 你

Per 你 turn Part 6: "通过了得跟用户明确说明":

- 明确 indicate "任务 完成 + 验收 通过"
- List acceptance criteria + evidence
- Per P17: don't claim PASS without evidence
- Per M-n 24: pace-continuity 中 明确 通知
  you is allowed

## 验收 report template

Per Claude acceptance-criteria-verification
skill + NASA SWE-034:

```
## Verification Report

**Run**: 2026-07-15T15:30:00Z
**By**: agent
**Commit**: <hash>
**Branch**: master

### Results

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | <criterion text> | PASS / FAIL / PARTIAL / SKIP | <evidence> |
| 2 | <criterion text> | PASS / FAIL / PARTIAL / SKIP | <evidence> |
| ... | ... | ... | ... |

### Summary

| Status | Count |
|--------|-------|
| PASS | X |
| FAIL | X |
| PARTIAL | X |
| SKIP | X |
| **Total** | **X** |

### Evidence

- Test output: <path or inline>
- Commit hash: <hash>
- File size: <bytes>
- R1-R12 status: <per VERIFICATION.md>

### 5 primitives applied

- [x] Analyze: <findings>
- [x] Reason: <findings>
- [x] 联想: <findings>
- [x] 归纳: <findings>
- [x] 总结: <findings>

### Next steps

- [ ] <if FAIL: action items>
- [x] <if PASS: notification>
```

## Worked example (c203 self-application)

Apply M-n 29 to current task (c203 codify
M-n 29 itself):

**Step 1 (Design 角度)**: Functional (5
primitive protocol defined) + Framework-
agnostic (per M-n 20) + R-n (per R1-R12) +
P-n (per 25 P-n) + M-n (per 28 M-n).

**Step 2 (Execute 验收)**:
- Analyze: M-n 29 段 IS 5-step protocol
  (defined in OPERATING_RULES.md 83323 → 78618).
- Reason: 5 primitives match 你 turn Part 3
  explicit + M-n 16 stage 1-2 + M-n 14 class比
  induction + M-n 18 recursive summary + M-n
  26 compression.
- 联想: 类似 Claude acceptance-criteria-
  verification skill + NASA SWE-034.  MCP
  search per c94 confirms pattern.
- 归纳: 5-step pattern = general protocol
  for task acceptance.
- 总结: this L2 companion IS the protocol
  总结.

**Step 3 (Validate)**: All PASS.

**Step 4 (FAIL check)**: No FAIL.

**Step 5 (PASS notification)**: This
section.

## Relationship to M-n 28

M-n 28 (plan-conditional) is BEFORE M-n 29
(acceptance):
- M-n 28 = when to plan vs continue.
- M-n 29 = when task complete, verify.

Sequence: plan (M-n 28) → execute → accept
(M-n 29) → notify.

## Relationship to VERIFICATION.md (c193)

VERIFICATION.md is THE 1-page project-level
verification summary (per c193).  M-n 29 IS
the protocol that PRODUCES such summaries
(each major commit batch → fresh verification
per M-n 29 → update VERIFICATION.md per
P14 docs stay current).

## Cross-references

- `docs/OPERATING_RULES.md` § M-acceptance-
  protocol (M-n 29 main段)
- `docs/OPERATING_RULES.md` § M-n 14/16/17/
  18/24/26/28
- `docs/PRINCIPLES.md` P17 + P22
- `VERIFICATION.md` (1-page summary per c193)
- NASA SWE-034 (research reference)
- Claude acceptance-criteria-verification
  skill (research reference)
- 你 turn 2026-07-15 — origin