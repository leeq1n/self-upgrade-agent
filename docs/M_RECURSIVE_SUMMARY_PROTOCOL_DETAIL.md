# M-recursive-summary-protocol (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> recursive-summary-protocol段 (M-n 18).  Per
> P11 摘要+引用 + R6, this companion is required
> when the summary rule describes a multi-step
> protocol.  Load when: agent enters 分治 task
> or considers writing summary hierarchy.

## Why this L2 doc exists

The OPERATING_RULES.md § M-recursive-summary-
protocol 段 (c111 + c114 clarification) provides
the 6 sub-steps.  This L2 doc provides decision
tree, worked examples, and 节点 生命周期管理
(sibling isolation, lifecycle states, destruction).

## 6 sub-steps (per M-n 18 + 你 turn clarification)

1. **写子任务总结**: when sub-task completes,
   write summary.
2. **父看自己子任务总结**: parent sees OWN
   children's summaries only (sibling isolation).
3. **父写父总结**: parent synthesizes → 1 parent
   summary via 类比 compress.
4. **交父总结给爷爷节点**: hand parent summary to
   grandparent.
5. **销毁子节点**: destroy child summaries to
   avoid pollution.
6. **爷爷只看父总结**: grandparent sees only
   parent summary, not 2nd/3rd-level summaries.

## 节点 状态 生命周期 (per 你 turn clarification)

| State | Content |
|---|---|
| **未完成** | 任务 摘要 + 子任务 说明 |
| **完成** | 只留 总结 |
| **销毁** | (after 父 读 + 写) 子 总结 销毁 |

Transition: sub-task 完成 → 总结 written → 任务
摘要 + 子任务 说明 replaced by 总结.

## 兄弟 隔离 (per 你 turn clarification)

二级节点 should NOT see other 二级兄弟节点's 子
总结.  Each 父 only sees OWN children.

## Decision tree: when to invoke M-n 18

```
Q1: Is this a 分治 task (multiple sub-tasks)?
├── No → Don't invoke M-n 18
└── Yes → Q2

Q2: Are sub-tasks completed (any of them)?
├── No → sub-task is in "未完成" state
│        (task description + sub-task descriptions)
└── Yes → Apply M-n 18 protocol:
         1. 写子任务总结
         2. 父看自己子任务总结
         3. 父写父总结
         4. 交父总结给爷爷节点
         5. 销毁子节点
         6. 爷爷只看父总结
```

## Worked example: c112 (PLAN file)

When c112 was committed (`.hermes/plans/2026-07-
15_160000-replan.md` created per M-n 18 + 你 turn
"写下来"):

- **Sub-task done**: PLAN file written
- **M-n 18 applied**:
  - Sub-task 7 summary written in PLAN (not in
    response, to avoid pollution)
  - Parent summary future (after c114-c118 done)
  - Grandparent (你 turn) sees only PLAN summary,
    not all sub-task details
- **Per M-n 19 (file naming)**: file path is
  `.hermes/plans/2026-07-15_160000-replan.md`
  (not `.hermes/plan/` singular)

## Worked example: c114 (M-n 18 clarification)

When c114 was committed (M-n 18 + 节点 生命周
期管理段 added):

- **Sub-task done**: M-n 18 clarification codified
- **M-n 18 applied**:
  - Sub-task summary written in PLAN file (M-n 18
    + 节点 生命周期管理 段)
  - PLAN file is single source of truth (avoid
    pollution)
- **Per M-n 19**: no new file created (段 added
  to existing OPERATING_RULES.md)

## How M-n 18 composes with other M-rules

- **M-n 14 (two-track reasoning)**: parent synthesis
  uses 类比 (compress N child summaries → 1 parent
  summary).
- **M-n 15 (principle-reordering)**: parent summary
  may trigger M-n 15 6-step if principles are
  disordered.
- **M-n 16 (observe-think-execute)**: stage 6
  applies M-n 18 after sub-task completion.
- **M-n 17 (context-freshness-check)**: Path 1
  (intra-agent re-read) ensures sub-task summary
  reflects current state.
- **M-n 19 (file-naming-convention)**: PLAN files
  named + placed consistently.
- **P11 摘要+引用**: M-n 18 enforces P11 via
  recursive summary.
- **P14 docs stay current**: parent summary ensures
  docs reflect all sub-task changes.
- **P28 (recursion)**: M-n 18 IS recursion applied
  to summary protocol.

## When NOT to use (anti-patterns)

### Anti-pattern 1: Skip sub-task summary

Loses child insights; parent can't synthesize without
them.

### Anti-pattern 2: Forward all child summaries to grandparent

Causes context pollution (per 你 turn "不然一堆二级
三级节点的总结会污染上下文").

### Anti-pattern 3: Skip parent synthesis

Grandparent gets N child summaries instead of 1
parent summary (causes pollution).

### Anti-pattern 4: Include unrelated sub-tasks' summaries

Violates 兄弟 isolation; each 父 only sees OWN
children.

### Anti-pattern 5: Skip destruction after parent synthesis

子 总结 remain in context, polluting future turns.

### Anti-pattern 6: 爷爷 越级 看 孙子

Grandparent should see only parent summary, not
2nd/3rd-level summaries.

## Self-application (per P28 recursion)

This L2 doc IS M-n 18 applied to itself:
- Before writing this L2 doc (c116 future),
  re-read OPERATING_RULES.md M-n 18段 + memory 7.
- Sub-task summary will be written in PLAN file
  after this L2 doc is committed.

## Cross-references

- `OPERATING_RULES.md` § M-recursive-summary-protocol
  — the L0/L1 段 (in SUA)
- `OPERATING_RULES.md` § M-n 18 clarification
  (节点 生命周期管理)
- `.hermes/plans/2026-07-15_160000-replan.md` —
  M-n 18 applied
- 你 turn 2026-07-15 (multiple) — origin

## Changelog

- c111 (OPERATING_RULES.md): add M-n 18段 (summary,
  5 sub-steps).
- c114 (OPERATING_RULES.md, PLAN): M-n 18
  clarification + 节点 生命周期管理 (6 sub-steps +
  sibling isolation + lifecycle + destruction).
- c116 (this file): add L2 detail companion per
  P11 + R6.