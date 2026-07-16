# Plan: 2026-07-16 Fix M-n 29 / M-n 31 self-referential trigger

> L0: Per 你 turn 2026-07-16 directive: "我之前
> 说过，skill 最后的时候要验收，你验收了吗？
> 你不知道要验收这件事，我认为这说明项目写
> 的有问题".  Root cause = M-n 29 / M-n 31
> triggers are self-referential ("agent 认为 任务
> 完成" + "all sub-tasks done") which can be
> silently bypassed.  Fix per P25 6-step +
> 分治 (per M-n 13 layer-extension) + 自顶向下
> (per M-n 16 observe-think-execute 6-stage).

## 总目标 (per 你 turn 2026-07-16)

让 **agent 在任何 "task done" / "验收" 触发时** 自动
apply M-n 29 5-step protocol（Design 角度 → Execute 5
primitives → Validate → FAIL cycle → Notify）—— 不依赖
agent 自己的 self-judgment。

## 根因 (per M-n 16 stage 2 思考-1 归纳)

| 问题 | 现状 | 根因 |
|---|---|---|
| M-n 29 trigger self-referential | "when agent 认为 任务 完成" | 没有 external signal |
| M-n 31 Phase 3 trigger 隐含 self-judgment | "all sub-tasks done" | agent 自报 done，没人 verify |
| M-n 32 Guardrail #4 trigger 隐含 | "claim 'task done' / 'all pass'" | claim 之后才校验，逻辑倒置 |
| AGENTS.md 缺 task-done-notify reminder | -- | 入口 doc 没 reminder |
| skill / v1.0.0 / skill-incubator / KG 缺 VERIFICATION.md (cold-start simulation) | -- | intended-accessibility 缺口 |

## 节点 生命周期 (per M-n 18 + 你 turn 2026-07-15)

| Node | 状态 | Sub-tasks | Trigger → Next |
|---|---|---|---|
| Root (this plan) | 未完成 → 完成 | 见下面分治 tree | All children done → commit + write retrospective |
| Node L0 (SUA) | 未完成 | 4 sub-tasks | All done → merge to v2.0.0-minimal |
| Node L1 (4 sibling) | 未完成 | 4 sub-tasks (1 per repo) | All done → notify 你 |
| Node L2 (verify) | 未完成 | 1 sub-task (重 run M-n 29 on all 5 repos) | All PASS → finalize |

## 分治 (per M-n 13 + P22 step 3)

按项目关系 (SUA → skill-incubator / skill / KG 是 reflection / sibling)：
**L0 (根因) → L1 (reflection) → L2 (verify)**

```
root: 修 M-n 29 + M-n 31 trigger
├── L0.1 (SUA): 改 OPERATING_RULES.md M-n 29 trigger [ext-signal]
├── L0.2 (SUA): 改 OPERATING_RULES.md M-n 31 Phase 3 [强制 M-n 29 5-step]
├── L0.3 (SUA): 改 OPERATING_RULES.md M-n 32 Guardrail #4 [pre-claim check]
├── L0.4 (SUA): 改 AGENTS.md [task-done-notify reminder]
│
├── L1.1 (skill): 补 VERIFICATION.md (cold-start simulation)
├── L1.2 (v1.0.0): 补 VERIFICATION.md (snapshot of v1.0.0 final state)
├── L1.3 (skill-incubator): 改 HANDOFF.md + 补 VERIFICATION.md
├── L1.4 (knowledge-graph-seed): 补 VERIFICATION.md
│
└── L2 (verify): 重 run M-n 29 5-step on all 5 repos
```

## 子任务 (per M-n 18 sub-task summary)

### Node L0.1 (SUA): M-n 29 trigger 改 external signal

**File**: `docs/OPERATING_RULES.md` § M-acceptance-protocol 段
**Action**:
- 改 "**Trigger**: when agent 认为 任务 完成 (per M-n 21 self-audit
  OR M-n 22 final 3W1H OR per 你 turn explicit "验收" OR after
  every major commit batch)" → 改 "**Trigger** (any ONE of these
  external signals)":
  - **S1**: Agent about to send "Task done" / "完成" / "PASS" /
    "all green" message to 你
  - **S2**: Agent about to make final commit in a planned commit
    batch (per M-n 18 sub-task summary "last commit" signal)
  - **S3**: Agent 收到 你 turn "验收" / "verify" / "check" 关键词
  - **S4**: After every N=5 commits in current session (per M-n 26
    context-decay periodic check)
  - **S5**: Before M-n 31 Phase 3 (task-done-notify) starts
- 保留 "agent 认为 任务 完成" 作为 **S5 子条件** (not standalone)
- 引用 P25 step 7 (post-modify re-apply new rules check = cold-start
  reachability test) 作为 action 6th sub-step

**Why**: S1-S4 都是 external signal (可观测的，不依赖 agent self-judgment)
**P-n cite**: P17 (老实说 — explicit trigger = observable), P25 (principle
modification discipline — step 5 impact analysis required), M-self-application
**L2 companion**: `M_ACCEPTANCE_PROTOCOL_DETAIL.md` 同段加 trigger 修订

### Node L0.2 (SUA): M-n 31 Phase 3 强制 M-n 29 5-step

**File**: `docs/OPERATING_RULES.md` § M-task-lifecycle 段
**Action**: 改 Phase 3 description "用 M-n 29 Step 5 explicit notify" →
"**Mandatory pre-condition**: apply M-n 29 5-step (Step 1 Design → Step 2
Execute → Step 3 Validate → Step 4 FAIL-cycle-or-PASS → Step 5 Notify)
BEFORE any task-done message.  Reference: Node L0.1 trigger S5."

**Why**: 当前 trigger 隐含 "agent should"，改成 "MUST"
**P-n cite**: P5 (verify before commit — Phase 3 = verify), P17
**L2 companion**: `M_TASK_LIFECYCLE_DETAIL.md` Phase 3 段同改

### Node L0.3 (SUA): M-n 32 Guardrail #4 改 pre-claim check

**File**: `docs/OPERATING_RULES.md` § M-self-learning-guardrail 段
**Action**: 改 Guardrail #4 表格:
- Trigger: "claim 'task done' / 'all pass'" → "**Pre-claim** (before any
  'task done' / 'all pass' message)"
- Enforcement: "per M-n 29 5-step" → "MUST apply M-n 29 5-step
  (per L0.1 trigger S1) and produce 验收 report"

**Why**: 把 guardrail 从 "claim 后 catch" 改为 "claim 前 enforce"
**P-n cite**: P17, P25, M-self-audit (step 7 verify-before-edit)

### Node L0.4 (SUA): AGENTS.md 加 task-done-notify reminder

**File**: `AGENTS.md`
**Action**: 在 "Hard rules" 段后加新段 "## Task-done-notify reminder":
- 引用 M-n 31 Phase 3 + M-n 29 5-step
- 引用 P25 step 7 (cold-start fresh-agent simulation)
- 列出 "before sending 'task done' message" 必做的 5 步

**Why**: AGENTS.md 是新 agent 入场必读 doc (per "Read first" 段) —
在此 reminder 强制 trigger 是最 effective 的位置

### Node L1.1-1.4 (4 sibling): 补 VERIFICATION.md

**File**: 各 repo `VERIFICATION.md` (新)
**Content (template per 1 page)**:
- 1 段 L0 概述
- ## Cold-start simulation (intended-accessibility test)
  - 模拟新 agent 从 0 开始按 reading order 走一遍
  - 检查每个 trigger point 都能 reach 到对应内容
  - 列出 "intended coverage" (e.g., "6 case studies", "4 frameworks",
    "L0 ≤ 120 chars")
  - 列 "actual coverage" (verify via grep / wc / read)
  - 列出 "edge gaps" (如果 any)
- ## R1-R12 / P-n / M-n 摘要
- ## Cross-refs

**P-n cite**: P11 (摘要+引用), P14 (docs stay current), P20 (L0 ≤ 120),
P21 (cross-project), P25 (post-modify re-apply), M-n 18, M-n 20, M-n 29

### Node L2 (verify): 重 run M-n 29 on all 5 repos

**Action**: 用之前的 verify 脚本（在 agent-reflection-skill/ 上跑过）扩展到 5
个 repo.  检查每个 repo 的 12-15 acceptance criteria 全 PASS.  Output 一份
对比表 (5 repos × 15 criteria = 75 cells).  Notify 你 "✅ Task done".

## 粒度 (per P4 1 commit = 1 feature + P7 奥卡姆 + P25 step 3 verify-no-duplication)

按你 override"根据原则判断修复粒度"——P4 1 commit 1 feature + P25 step 5 impact
analysis 强制逐 P-n / M-n 改：

| Commit | File(s) | Feature | P-n |
|---|---|---|---|
| c-f01 | docs/OPERATING_RULES.md M-n 29 trigger | external signal trigger | P17, P25 |
| c-f02 | docs/OPERATING_RULES.md M-n 31 Phase 3 | MUST apply M-n 29 5-step | P5, P17 |
| c-f03 | docs/OPERATING_RULES.md M-n 32 Guardrail #4 | pre-claim check | P17, P25 |
| c-f04 | M_ACCEPTANCE_PROTOCOL_DETAIL.md + M_TASK_LIFECYCLE_DETAIL.md + M_SELF_LEARNING_GUARDRAIL_DETAIL.md | L2 companion sync | P11, P14, P25 |
| c-f05 | AGENTS.md | task-done-notify reminder | P5, P11, P25 |
| c-f06 | VERIFICATION.md | cold-start simulation 段 | P14, P20, P25, M-n 29 |
| c-f07 (skill) | agent-reflection-skill/VERIFICATION.md | new file | P11, P14, P20, P25 |
| c-f08 (v1.0.0) | agent-reflection-skill-v1.0.0/VERIFICATION.md | new file | 同上 |
| c-f09 (incubator) | skill-incubator/VERIFICATION.md + HANDOFF.md fix | new + fix | P11, P14, P17, P20, P25 |
| c-f10 (KG) | knowledge-graph-seed/VERIFICATION.md | new file | 同上 |
| c-f11 (verify) | none (run script) | 5-repo verify + 报告 | P5, P17, M-n 29 |

**Total: 11 commits** (per P4 1 commit 1 feature, no squashing)

## 抗陷阱 (per M-n 28 + P22 + P25 step 6 详细 trace)

- **Anti-trap 1**: 不把 11 个 commit squash 成 1 个 (per P4 + git history 透明度)
- **Anti-trap 2**: 不在 commit message 罗列 30+ P-n 标签 (per P7 奥卡姆 — v2.0.0-minimal
  branch 上之前 commits 都违反，这是个新规约，self-apply)
- **Anti-trap 3**: L0.1-L0.4 改 M-n / P-n 段必须每 commit 独立 (per P25 step 5 impact
  analysis — 1 commit 改 4 个 P-n/M-n 的话 impact 纠缠)
- **Anti-trap 4**: 不在 SUA 项目里改 sibling 仓库文件 (per P21 — sibling 各自 commit)
- **Anti-trap 5**: 每个 sibling VERIFICATION.md 不引用 SUA 内部 c-hash (per
  M-n 30 knowledge-context trade-off — sibling 只需引用 M-n / P-n 编号)

## 销毁 (per M-n 18 节点 生命周期 + 你 turn "节点 生命周期管理")

- 这个 plan 完成后，节点 总结 留 1 段 (verdict + 11 commits list)，
  详细 sub-task 销毁
- SUA VERIFICATION.md 是 L0 (永久保留) — 不销毁
- sibling VERIFICATION.md 是 L1 (永久保留) — 不销毁

## Next step

按 M-n 24 pace-continuity + 你 override"按规划推进完成"——

**开始执行 L0.1 (SUA: 改 M-n 29 trigger)**。
