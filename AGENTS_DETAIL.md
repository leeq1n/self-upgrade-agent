# AGENTS — Operating Rules (detail)

> **LAYER**: project (L2 detail — see `AGENTS.md` "3-layer architecture")
>
> L0: Live L2 source for the per-task rules indexed by `AGENTS.md`,
> plus conditional project-document loading guidance.

## Per-task rule source

These sections are the canonical live content referenced by the compact
`AGENTS.md` index. Read only the section whose trigger matches the task.

## "继续" protocol

Per user message "我说继续的时候, 一般都和我之前说的
那段是一个意思":

When user message says "继续", agent MUST interpret it as:
**推进任务 (考虑之前说的那些思考方法, 考虑是否
重新做规划等, 考虑自顶向下等原则)**, NOT as a
generic continuation.

**Two cases**:

| Case | user message signal | Agent action |
|---|---|---|
| **任务未完成** | 该消息隐含承接上文 (e.g., previous turn left tasks undone) | Continue: apply thinking methods (5 primitives + 4 critical-thinking + 自顶向下分治); replan if撞到一起 (per M-n 12 + M-n 28 4-condition); keep committing |
| **任务完成** | 消息含“验收” / “完成了” / explicit done | Apply M-n 29 5-step acceptance protocol: design 验收 角度, execute 5 primitives + 4 critical-thinking, validate all PASS, cycle if FAIL, **明确告知** (per user message "完成了的时候跟我明确说明情况") |

**Anti-patterns**:

- DON'T stop mid-task and ask "next" (per
  PITFALL 39 batch rule).
- DON'T ignore thinking methods when continuing.
- DON'T skip 验收 when task is done.
- DON'T claim "task done" without M-n 29 5-step
  (per M-n 32 Guardrail #4).

## "学习一下" protocol

Per user message "我说学习一下的时候, 指的是不仅仅
是hermes学习, 也是这几个项目里 agent 的核心层
/ 用户层需要学习, 需要在迁移到其他用户之后还能
有充足的这类知识":

"学习" = **cross-project learning**, NOT single-
hermes learning.

**Three layers of learning**:

| Layer | Where | What | Persistence |
|---|---|---|---|
| **核心** | `core-layer/` + `AGENTS.md` + `hooks/` + `.hermes/scripts/` + `docs/OPERATING_RULES.md` | Agent behavior rules | Cross-project, cross-user (migrates to other users' machines via skill) |
| **用户** | `memory/` system + user-specific files | User habits / preferences | Cross-session (per user) |
| **项目** | `docs/PRINCIPLES.md` + `docs/PROJECT_STATE.md` + project docs | Project-specific knowledge | Per project (NOT cross-project) |

**Cross-project requirement**: per user message
"迁移到其他用户之后还能有充足的这类知识" =
skills must carry 核心 + 用户 layer knowledge
to new users.  Skill zip should include enough
context that a fresh user on a different machine
has the same 核心 + 用户 knowledge the original
user had.

**Implementation**: when designing skills, ask
"would a stranger on a different machine have
enough 核心 + 用户 knowledge to use this skill
effectively?"  If NO, the skill isn't portable.

## "主动修改 skill" protocol

Per user message "我希望这skill在别人电脑上还会主动
修改skill, 但是核心层修改需要尽可能少, 主要
修改用户层 (根据学到的知识判断改哪一层), 而
项目层知识随着项目变化而变化":

**3-layer modification policy**:

1. **核心层修改尽可能少** — modify core only
   when absolutely necessary (e.g., new M-n,
   consistent failure pattern).
2. **用户层主要改** — modify user layer mainly,
   based on observed habits (per "判断改哪一层"
   rule).
3. **项目层随项目变化** — modify project layer
   continuously, but as **knowledge base** (NOT
   log).

**Project knowledge base rule**: past knowledge
keeps only lessons (经验), not details (细节).
Latest version of project knowledge is primary.

See `core-layer/README.md` § "3-layer modification
policy" for trigger conditions + audit checks
per layer.

## Iterative thinking protocol

Per user message "有的时候, 一层思考不够充分, 执行
阶段可以判断需要额外轮的思考, 下一轮继续":

**Thinking is iterative, not single-pass**.

When the first round of thinking produces an
output, the agent should:

1. **Apply the output** (execute / commit / reply)
2. **Observe results** (what worked, what didn't,
   what's missing)
3. **Re-think if needed** (下一轮思考 = pass 2+)

### When to trigger a next pass

| Trigger | Signal | Action |
|---|---|---|
| **Output feels shallow** | Agent output looks superficial | Pass 2: dig deeper |
| **New info emerged** | Execution revealed facts not in initial thinking | Pass 2: incorporate |
| **矛盾 / conflict** | Output contradicts earlier reasoning | Pass 2: reconcile |
| **User correction** | User points out a flaw | Pass 2+: address specifically |
| **Critical-thinking primitive fires** | 质疑 / 逆向 / 预演失败 / 对立论证 reveals gap | Pass 2: re-plan |

### Termination conditions

Iterative thinking has **bounded depth**:

1. **Termination by satisfaction**: pass N
   produces an output that passes all 4
   critical-thinking primitives + 5-step
   acceptance protocol.
2. **Termination by user signal**: user message
   explicit "够" / "验收" / "完成".
3. **Termination by depth limit**: if pass 3
   still produces gaps, escalate (per M-n 28
   4-condition: plan, don't brute-force).

### Anti-patterns

- **Don't infinite-loop** — if pass 3 still has
  gaps, the issue is upstream (wrong assumption,
  missing data), not "more thinking".
- **Don't re-do pass 1** — each pass should add
  depth, not repeat shallow analysis.
- **Don't skip pass 1** — even when user is
  impatient, the first pass establishes baseline.

### Self-application (P29 recursion)

This rule applies to itself. When updating this
段:

- If you're tempted to keep iterating without
  converging → check termination conditions.
- If you're tempted to declare done after one
  pass → check critical-thinking primitives.
- If you're tempted to escalate → check user
  signal first (per 继续 protocol above).

## Recursive test-verify protocol

Per user message "我希望你能在修改后主动验收" + "自顶
向下分治法做任务的时候, 子任务做完的时候也需要
一直测试-验收直到通过才能结束, 交给父任务":

**类比 (per M-n 14 Track 1)**: this rule is
**TDD + recursive testing + 测试金字塔**:

| Analog | Mechanism |
|---|---|
| **TDD (Test-Driven Development)** | Write test first, code until pass |
| **Recursive testing** | Base case test + recursive case test |
| **测试金字塔** | Unit + integration + system tests at each level |
| **CI pipeline** | Every commit triggers test pipeline; red blocks merge |
| **BDD (Behavior-Driven Development)** | Acceptance criteria per feature |
| **Strong robustness testing** | Invalid inputs fail gracefully |

**Rule**: at every level of top-down task
decomposition, after completing a sub-task:

1. **Test it** (does it work?)
2. **Verify it** (does it meet acceptance criteria?)
3. **Iterate until pass** (max 3 attempts per
   sub-task, per iterative thinking termination)
4. **Hand off to parent task** (only when pass)

### Sub-task verify pattern

```
Parent task: "Implement X"
├─ Sub-task 1: "Implement X.A"
│   ├─ Implement
│   ├─ Test (TDD: write test first)
│   ├─ Verify (acceptance criteria)
│   ├─ Iterate until pass (max 3 attempts)
│   └─ Hand off to parent (only when pass)
├─ Sub-task 2: "Implement X.B"
│   ├─ Implement
│   ├─ Test
│   ├─ Verify
│   ├─ Iterate until pass
│   └─ Hand off to parent (only when pass)
└─ Sub-task 3: "Integrate X.A + X.B"
    ├─ Integrate
    ├─ Test (integration test)
    ├─ Verify (system-level acceptance)
    ├─ Iterate until pass
    └─ Hand off to user (only when pass)
```

### When to apply

| Task type | Apply recursive test-verify? |
|---|---|
| Code commit | ✅ YES (eval_before + verify_after + commit-msg hook) |
| Doc update | ✅ YES (release_audit + per-section trigger check) |
| Skill modification | ✅ YES (skill self-modify trigger + portability filter) |
| Principle modification | ✅ YES (M-n 15 6-step + slippery-slope detection) |
| Quick chat reply | ❌ NO (no sub-task; simple response) |
| user message question | ❌ NO (clarification needed) |

### Anti-patterns (when NOT to apply)

- **Don't apply to trivial sub-tasks** (e.g.,
  "rename a file") — overhead > benefit.
- **Don't infinite-loop** — max 3 attempts per
  sub-task (per iterative thinking termination).
- **Don't skip verify step** — "looks correct" is
  not the same as "verified pass".
- **Don't hand off unverified work** — parent task
  accumulates errors.

### Active verify (vs user message-triggered verify)

Per user message "我希望你能在修改后主动验收":
agent should **主动 verify** (not wait for user message
ask).  Specifically:

| Verify trigger | Action |
|---|---|
| After any commit | Run release_audit.py (5/5 PASS) |
| After any doc edit | Check L0 ≤ 120 chars + cross-refs |
| After any principle change | Apply M-n 15 6-step |
| After any skill change | Apply portability filter + per-section triggers |
| Before "task done" claim | Apply M-n 29 5-step |

### Relationship to other protocols

- **继续 protocol**: sub-task completion → 继续
  trigger for next sub-task, OR 验收 trigger if
  parent done.
- **学习 protocol**: sub-task verification = part
  of "learning" (per cross-project learning).
- **主动修改 protocol**: skill self-modification =
  sub-task with recursive verify.
- **Iterative thinking**: provides termination
  conditions (max 3 attempts).

### Self-application (P29 recursion)

This rule applies to itself:

- If a sub-task needs > 3 attempts → escalate
  (per iterative thinking termination).
- If a sub-task passes without verify → it's not
  actually verified (false positive).
- If a parent task accumulates unverified sub-
  tasks → the parent is at risk of cascade
  failure.

## Skill context cleanliness (P-14 self-contained mandate)

Per user message "skill 库是最终面向用户的库, 需要
为新agent保持项目上下文干净":

When working on skills (or any user-facing
artifact):

- **NO dev-session references** in skill content
  (e.g., dev history retrospective = not user-facing)
  dev history; not user-facing).
- **NO SUA-specific examples** in skill content
  (e.g., "in SUA, we have Y" = project-specific;
  not portable).
- **YES generic patterns** (e.g., "When user
  shows consistent preference" = universal; user-
  facing).

**Audit checklist** before declaring skill ready:

1. Search skill for "per user message <date>" → should
   be 0.
2. Search skill for project-specific names (SUA,
   parent project) → should be 0 in operational
   content.
3. Search skill for session-specific wisdom
   ("this session we learned", "retrospective",
   "4-FAIL") → should be 0.
4. Each section earns its place by being
   universally useful (per portability filter).

**Why this matters**: a new agent reading the
skill should see only the skill's domain (how
to reason), not the development context (what
SUA did).  Otherwise the agent inherits SUA's
frame of reference, polluting its own reasoning.

**Implementation**: when designing skill content,
imagine a stranger on a different machine, with
zero context, reading the skill for the first
time.  Would they understand and use it?  If
NO, simplify or remove context-specific
references.

## Multi-perspective audit angles

Per user message "我教过的那几个角度" + "或许你需
要学习下这个" + "你说学习的时候要考虑本地的
这几个项目":

When working on skills (or any user-facing
artifact), apply **2 audit angles**:

### A1: User-skill angle (skill usability)

**Question**: when user installs skill, can they
USE all the primitives + 段s effectively?

**Sub-checks**:

1. **README入口** — does README have explicit
   trigger items (e.g., "If you see X, do Y")?
2. **SKILL.md usability** — are all 9 primitives
   documented with definitions + triggers?
3. **Quick reference card** — is there a 1-page
   summary for quick lookup?
4. **Decision tree** — is there a step-by-step
   decision aid?
5. **4-line format** — is the output contract
   documented?
6. **HANDOFF orientation** — does a fresh agent
   know where to start?
7. **AGENTS framework compat** — does it work in
   Hermes / Claude Code / Codex / Cursor /
   generic agents?
8. **Per-primitive triggers + examples** — does
   each primitive have explicit trigger + use
   example?
9. **Anti-patterns** — does the skill warn about
   when NOT to use?

### A2: User-project angle (skill fit per project)

**Question**: for each project in the local
ecosystem (SUA + sibling projects + others), what skill applies +
is it the right fit?

**Sub-checks** (per project):

1. **Project type** — what kind of work is this
   (principle project / skill deliverable / meta-
   skill / knowledge graph / etc.)?
2. **Skill fit** — which of the 9 reasoning
   primitives apply to this project's phases?
3. **Cross-reference** — does the project's
   AGENTS.md or VERIFICATION.md reference the
   relevant skill?
4. **Reasoning application** — for each phase of
   work, which primitives to use?
5. **Pre-commit check** — before committing,
   verify the reasoning was applied correctly?

### When to apply these angles

| Task | Apply A1? | Apply A2? |
|---|---|---|
| Skill design / modification | ✅ YES | ✅ YES |
| Project AGENTS.md update | ❌ NO | ✅ YES |
| Cross-project integration | ⚠️ Partial | ✅ YES |
| Single-repo task | ❌ NO | ⚠️ Optional |
| user message question / clarification | ❌ NO | ❌ NO |

### Self-application (P29 recursion)

This rule applies to itself:

- If A1 audit keeps finding gaps → skill design
  needs more work (loop in skill design).
- If A2 audit reveals wrong-skill → reconsider
  project purpose (loop in project design).
- If both audits pass + 验收 cycles → task done.

### Cross-reference to other protocols

- **继续 protocol**: A1/A2 audit is part of
  "tasks not done" detection.
- **学习 protocol**: A1/A2 audit angles are part
  of "learning to apply" (per user message "考虑本地
  项目").
- **Recursive test-verify**: A1/A2 audit = a
  verify step that must pass before "task done".

## Task-done-notify reminder

Per user message "我之前说过，skill 最后的时候要验收，你验收
了吗？你不知道要验收这件事" + user message 2026-07-16
"很多地方说的思考都需要用原则里的思考方法。在工作
的时候你经常想不到用这思考方法，你得问问自己为什么"
+ L0.1-L0.3 commits in `fix/m29-trigger-explicit` branch:

**Before any commit / before sending "task done" message**,
agent MUST apply **5 primitives** (per M-n 16 stage 1-2
+ M-n 14 two-track + M-n 25 message-pattern + M-n 26
context-decay; codified in M-n 29 Step 2):

**Per M-n 14 two-track**: complete
thinking needs BOTH constructive + adversarial.  Apply
**4 critical-thinking primitives** FIRST (default-on for
high-stakes, optional for single-file refactors, skip for
trivial fixes; per
`docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md`):

0a. **质疑 (Challenge)**: 3 specific weaknesses + which
    weakness has highest damage
0b. **逆向 (Invert)**: OPPOSITE state + 2-3 reasons OPPOSITE
    could be true + what would change
0c. **预演失败 (Pre-mortem)**: "this FAILED in 30 days" +
    3-5 failure modes + 1-2 preventable (Gary Klein 2007)
0d. **对立论证 (Steelman-the-opposite)**: most charitable
    opposing case + 2-3 strongest opposing arguments +
    acknowledge valid opposing points

1. **Analyze** (M-n 16 stage 1): 任务 IS what? 范围
   components / files / commits involved?
2. **Reason** (M-n 16 stage 2 + M-n 22 3W1H): Why
   this design? Trade-offs? Alternatives considered?
3. **联想 (analogize)** (M-n 14 class比 + M-n 17
   Path 2): 类似 prior pattern? (e.g., linter 漏检
   / compiler self-host / API doc 漏 cover — common
   pattern: "rules written ≠ rules invoked")
4. **归纳 (induct)** (M-n 14 induction + M-n 18):
   General pattern from specific? What can be
   applied to other tasks?
5. **总结 (summarize)** (M-n 26 compression + M-n
   18 destruction): Synthesize 1-paragraph L0;
   节点 生命周期 (destroy redundant detail).

**Why this is a gate, not a step description**:
"5 primitives written in M-n 29 Step 2" is L2
detail.  LLM agents don't auto-invoke L2 detail
content (root cause: same self-referential
problem as M-n 29 trigger).  Lifting these 5
primitives to L0 (AGENTS.md "Read first" 段)
+ this reminder段 makes them **observable to
fresh agents on every commit** (per P25 step 7
+ P26 fresh-agent simulation).

**Self-application reminder** (per M-n 14
Track 1 类比): my own failure on the previous
batch (5 commits without explicit 5-primitives
apply) was the same pattern as M-n 29
self-referential trigger — rules written ≠
rules invoked.  This reminder IS the fix.

Then MUST apply **M-n 29 5-step protocol**:

1. Apply **M-n 29 5-step protocol**:
   - **Step 1**: Design 验收 角度 (per M-n 22 3W1H):
     functional / 兼容性 / 安全 / 维护性 / user-facing /
     framework-agnostic / R1-R12 / 项目 整洁度 /
     **新 agent 可读性** (intended-accessibility test)
   - **Step 2**: Execute 验收 with 5 primitives:
     Analyze (M-n 16 stage 1) / Reason (M-n 16 stage 2
     + M-n 22 3W1H) / 联想 (M-n 14 class比 + M-n 17
     Path 2) / 归纳 (M-n 14 induction + M-n 18) /
     总结 (M-n 26 compression)
   - **Step 3**: Validate (all PASS / no FAIL / no PARTIAL)
   - **Step 4**: If FAIL → fix → re-verify (loop)
   - **Step 5**: Notify (this is the "完成" message)

2. **Hard external trigger**: per direct user instruction with explicit authorization
   retrospective 4-FAIL diagnosis (M-n 29 pre-claim
   + M-n 32 #4 violations across multiple turns),
   mechanical enforcement is required.  Run the
   external 5-step script BEFORE claiming task done:

   ```bash
   python .hermes/scripts/m_n29_5step.py --self --claim "<task description>"
   ```

   This script externalizes M-n 29 5-step from
   LLM-self-judgment to deterministic mechanical
   baseline.  Per M-n 30 Priority 1 (knowledge 充足)
   + M-n 28 4-condition autonomous execute.

3. Include a **"Cold-start simulation"** section in the
   验收 report: list 3+ trigger points in the project
   + verify each is reachable from the entry doc by a
   fresh agent (per P25 step 7 + P26 fresh-agent simulation).

4. Cite the P-n / M-n that motivated each acceptance
   criterion (per commit-msg hook contract above).

**Anti-pattern**: skipping 5-step and going directly to
"完成" message — this is the exact failure mode user message
flagged.  Per M-n 32 Guardrail #4 (pre-claim): NOT
allowed to claim PASS before 5-step is complete.

**Per retrospective**: previous
session claimed "✅ Task DONE" multiple times without
applying M-n 29 5-step.  This external trigger script +
AGENTS.md reminder段 are the structural fix.

See:
- `docs/OPERATING_RULES.md` § M-acceptance-protocol (M-n 29)
- `docs/OPERATING_RULES.md` § M-task-lifecycle (M-n 31)
- `docs/OPERATING_RULES.md` § M-self-learning-guardrail
  (M-n 32 Guardrail #4)
- `.hermes/scripts/m_n29_5step.py` (mechanical external
  trigger)

## Post-completion verification suggestion

Per user message "因为有了更改, 现在应该再次验收"
+ "做完任务后, 跟用户明确说明的同时, 也需要
跟用户说建议下一步做验收":

When agent reports **task completion** to user,
the report MUST include:

1. **明确说明** (clear statement): "task done" /
   "complete" / "ACCEPTED" — explicit.
2. **建议下一步做验收** (suggest next verification):
   "建议你进行下一步验收" / "建议验证 X / Y / Z"
   / "请运行 release_audit.py 验证" — explicit
   suggestion.

These 2 actions are NOT optional and NOT
substitutable.  Both must appear in every
completion message.

### When to apply

| Task type | Apply both (明确说明 + 建议验收)? |
|---|---|
| Code commit | ✅ YES |
| Doc update | ✅ YES |
| Skill modification | ✅ YES |
| Cross-project integration | ✅ YES |
| user message question / clarification | ❌ NO (no completion) |
| Trivial chat reply | ❌ NO (no completion) |

### What "建议下一步做验收" should include

A good verification suggestion includes:

1. **What to verify** (specific dimensions):
   - Run release_audit.py
   - Check release-audit.py 5/5 PASS
   - Verify tag at HEAD
   - Read this section for cross-refs

2. **How to verify** (specific commands):
   - `python .hermes/scripts/release_audit.py
     <target>`
   - `git log --oneline | head -3`
   - `git status --porcelain`

3. **Acceptance criteria** (what "pass" looks like):
   - All 5 checks PASS
   - Working tree clean
   - Tag at HEAD
   - 0 errors in fresh verify

### Classify via 类比 (per M-n 14 Track 1)

| Analog | Mechanism |
|---|---|
| **CI pipeline** | Every commit triggers verify pipeline; green = ok, red = block |
| **Definition of Done (DoD)** | DoD includes verification step |
| **Code review workflow** | Submit → review → re-verify if changes |
| **Hospital discharge** | Patient leaves with explicit follow-up recommendation |
| **Construction inspection** | Work complete + sign-off + next inspection scheduled |

### Self-application (P29 recursion)

This rule applies to itself:

- If agent reports completion without
  verification suggestion → incomplete
  notification (false positive).
- If verification suggestion is too verbose →
  noise (apply M-n 18 destruction).
- If verification suggestion is too brief →
  user can't act (apply 3 sub-items above).

### Anti-patterns (when NOT to apply)

- **Don't suggest verification on every chat
  reply** (only on completion).
- **Don't include verification suggestion as
  boilerplate** (must be specific to the task).
- **Don't skip 明确说明** (both are required).

### Cross-reference to other protocols

- **继续 protocol**: "建议下一步做验收" is part
  of task completion, separate from "继续".
- **学习 protocol**: verification = part of
  learning to apply correctly.
- **Recursive test-verify**: this rule is the
  meta-application of recursive test-verify
  (verify the verification-suggestion itself).

## Operating rules (M-n 1-34)

**34 M-n** in `docs/OPERATING_RULES.md` (per Phase 3 audit
2026-07-16: 28 M-n codified with L1段, 22 with L2 _DETAIL.md
companion.  M-n 1, 5, 6, 9, 10 not in L1 (P-layer principles,
not operational).):

- **M-n 1**: (top-level: principle-layer, no L1)
- **M-n 2**: (concept-layer, no L1 in OPERATING_RULES)
- **M-n 3**: 3w1h-think-first (BEFORE top-down)
- **M-n 4**: (concept-layer)
- **M-n 5**: (top-level: principle-layer, no L1)
- **M-n 6**: (recognition, no L1)
- **M-n 7-10**: (early-stage, not in OPERATING_RULES L1)
- **M-n 11**: experiment-in-subproject (sub-project pattern)
- **M-n 12**: terminology-clarity (refine "撞到一起" → "replan")
- **M-n 13**: layer-extension (L0/L1/L2 + extensions)
- **M-n 14**: two-track-reasoning (类比+逻辑, 6-stage distribution)
- **M-n 15**: principle-reordering (6-step after 原则 混乱)
- **M-n 16**: observe-think-execute (6-stage + top-down 分治)
- **M-n 17**: context-freshness-check (intra-agent + inter-domain)
- **M-n 18**: recursive-summary-protocol (6 sub-steps + 节点 生命周期)
- **M-n 19**: file-naming-convention (PLAN dir + name + L2 companion)
- **M-n 20**: agent-discoverability-check (cross-framework + naming + discoverability)
- **M-n 21**: ask-or-infer-mark-guess (3 sub-steps + top-down 默认)
- **M-n 22**: 3w1h-think-first (3W1H 分析法 BEFORE top-down)
- **M-n 23**: periodic-re-analysis (re-分析 at 最终目标)
- **M-n 24**: pace-continuity (commit + continue, no verbose ending)
- **M-n 25**: message-pattern-recognition (parse user message + 5 patterns + M-n self-application 4 levels)
- **M-n 26**: context-decay-management (detection + classification + compression + refresh)
- **M-n 27**: knowledge-layer-architecture (3-layer core/knowledge/project + 3 sources hermes/SUA/skill + single-skill fallback)
- **M-n 28**: plan-conditional (4-condition check: uncertain → plan; clear → continue)
- **M-n 29**: acceptance-protocol (5-step protocol: design + 5 primitives + validate + cycle + notify)
- **M-n 30**: knowledge-context-trade-off (4-priority: knowledge 充足 > context 管理 > trade-off via 分层+类比 > 分层 自顶向下 分治 always)
- **M-n 31**: task-lifecycle (4-phase: init + execute + done-notify + retrospective)
- **M-n 32**: self-learning-guardrail (5 modification guardrails + auto-learning)
- **M-n 33**: narrative-as-spec (3-primitive: parse + structure + codify/execute)
- **M-n 34**: pre-task-scan (added 2026-07-16; per user message "自主阅读学习".
  4 sub-steps: Read AGENTS / Scan P-n+M-n / Apply 5 primitives
  / Document scan result.  Per `docs/M_PRE_TASK_SCAN_DETAIL.md`.)

## Cross-project sync

**SUA is a self-contained knowledge library**; sibling
repositories are maintained independently (standalone or
frozen) and are not downstream of SUA.

**L4 boundary revision**:

- (a) 1 line / typo / cross-ref = low-risk autonomous, skip 7-check
- (b) 1-2 files / 7-check needed = mid-risk, run 7-check + ask
- (c) 3+ files / vision-affecting = high-risk, always ask

(但 你 override: "如果你通过了原则确认没问题，就
直接进行，不用找我确认" — 主动 allowed per 你
directive.)

**Phrasing** (per M-n 12 + c95):

- "撞到一起" → "replan" (or "撞到一起" preserved
  in M-n 12 example text)
- "等下次 next trigger" → "我 [active plan]"

**Framework-agnostic** (per M-n 20):

- This project designed for Hermes / Codex / Claude
  Code / others.
- File names should avoid Hermes-specific terms.
- Future agents should be able to read this project
  without Hermes-specific knowledge.
(per OcCam).


## See also (project docs, conditional load)

These are **conditional** docs — load only when the task type
matches the trigger.  Default: don't load.
- `docs/RECURSIVE_DECOMPOSITION.md` — load when task is big
  (multi-file, multi-project, multi-step).  5-step loop.
- `docs/OPERATING_RULES.md` — load when ending task, switching
  task, unsure which tools to use, **or before declaring "all
  pass"**, **or after encountering any new rule/pattern**, **or
  when user input is messy**, **or at a decomposition
  integration point**, **or when context feels cluttered**.
  Also load **at the start of every user message** to check
  whether the message is a switch (per
  `docs/SWITCH_SIGNALS.md` "Switch action protocol");
  switching without loading is the most common fresh-agent
  miss.
  9 M-* rules: M-task-summary, M-must-read, M-context-snapshot,
  M-subtask-summary, M-intent-parsing, M-learn,
  M-add-then-reduce, M-self-audit, M-self-application.
- `docs/OPERATING_RULES_DETAIL.md` — load when implementing
  M-intent-parsing (full 3-action steps, anti-pattern) or
  M-learn (full dual-track triggers, 3 sub-actions, M-rule
  relationships).  Per P20 R5+R6: 7KB-summary / _DETAIL-split
  pattern; this is the L2 detail companion.
- `docs/M_SELF_AUDIT.md` — load before "all pass", before
  any Edit/Write on a previously-read file (per step 6
  "verify-before-edit"), or after big doc changes
  (fresh-agent discoverability check; 4 triggers,
  6-step audit checklist, anti-patterns).
- `docs/M_SELF_APPLICATION.md` — load when encountering any
  new rule or pattern, or when debugging "rule didn't apply"
  (4 levels: object / rule itself / memory / self behavior).
- `docs/SUMMARY_LIFECYCLE.md` — load when implementing a
  parent-level M-task-summary (M-task-summary child-summary
  destroy contract — pull, write, destroy in same commit).
- `docs/SWITCH_SIGNALS.md` — load when evaluating whether
  current context is a "switch" that needs M-context-snapshot
  (5 signal types, what goes in a snapshot, location).
- `docs/TODO_SESSION_PERSISTENCE.md` — proposal for formal
  snapshot/restore mechanism (format, location 2-tier,
  restore protocol, lifecycle per M-add-then-reduce).
  Implementation deferred (proposal-only).
- `docs/TODO_SESSION_PERSISTENCE_DETAIL.md` — L2 detail
  companion (per P20 R5 + R6: 7KB-summary / _DETAIL-split
  pattern; holds open questions + implementation steps).
  Load when: implementing the proposal or resolving the
  questions.
- `docs/ADD_THEN_REDUCE.md` — load when planning a multi-leaf
  task or applying M-learn (Add phase + Reduce phase, signal
  triggers, anti-patterns).
- `docs/COMMON_PITFALLS.md` — load when context-switching
  or about to start non-trivial work.  4 categories of clues
  fresh agents often miss.
- `docs/MEMORY_TOOLS.md` — load when unsure which memory
  tool to use.  Decision matrix.

**Before declaring any task "all pass"**: apply M-self-audit
(from `docs/M_SELF_AUDIT.md`).  Ask: "If a new agent
entered this project right now, could it read what it needs
to do the task?"  Per M82: verify before claiming.  Per P17:
never claim green when it is yellow.

**After encountering any new rule or pattern**: apply
M-self-application (from `docs/M_SELF_APPLICATION.md`).
Ask "does this rule apply at 4 levels — to current task,
to the rule itself, to memory / project structure, to my
own operating behavior?"  This is the most common class
of agent failure mode: knowing a rule but not self-applying
it.

## See also (project docs, always-load if relevant)

These are project-wide pointers; load if your task type matches.

- `docs/PRINCIPLES.md` — the principles themselves (P1-P29, 25 working).
  **Read FULLY before modifying any P-n / M-* rule** (per
  "P-n / M-* modification discipline" 段).
- `docs/INDEX.md` — orientation map.
- `docs/PROJECT_STATE.md` — current state (1-paragraph).
- `docs/PROJECT_STATE_DETAIL.md` — version history + vision.
- `docs/PRINCIPLES_DETAIL.md` — full text of each P-n.
- `docs/LITERATURE.md` + `docs/LITERATURE_DETAIL.md` — past
  research citations (per P2 搜资料 workflow).
- `DONE.md` — project log (use `search_files` to find
  specific items, don't load fully).
- `README.md`, `TODO.md` —
  root project docs (load when starting broad project work).
- `docs/CONSTRAINTS.md` + `docs/CONSTRAINTS_DETAIL.md` — hard
  must-not-violate rules (C1, C2...).

## See also (session-specific, conditional)

Load only when context has overflowed or task has switched.

- `C:\Users\LQ\AppData\Local\Temp\hermes-verify-sua-onboarding-20260713.py`
  — ad-hoc verify script for the 8-commit onboarding batch
  (30 checks; 30/30 PASS).
- `C:\Users\LQ\AppData\Local\Temp\hermes-snapshot-sua-onboarding-20260713.md`
  — session snapshot (recent commits, open todos, decisions).
  Load this on resume after context overflow.
