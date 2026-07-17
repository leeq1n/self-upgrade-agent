# AGENTS — Operating Rules for AI Agents in This Project
Last P20-verified: 2026-07-15

> L0: AI agents entering this repo MUST read `docs/PRINCIPLES.md`
> FIRST.  Treat each P-n as binding unless the user explicitly
> overrides it for a task.  Commits that ignore PRINCIPLES will
> be caught by the commit-msg hook (P-n cite required).

## Pre-task scan (M-n 34, added 2026-07-16)

**Per 你 turn 2026-07-16 "自主阅读学习" + M_RULE_AUTHORING
3-condition gate**: before any 你 turn response, before any
commit, before any "task done" message — agent MUST run
**M-n 34 pre-task scan** (4 sub-steps per
`docs/OPERATING_RULES.md` § M-pre-task-scan):

1. Read this `AGENTS.md` (you are here — L0 entry doc).
2. Scan `docs/PRINCIPLES.md` L0 axioms + `docs/OPERATING_RULES.md`
   all M-n.  Mark YES / NO / MAYBE for current task.
3. Apply 5 primitives (Analyze / Reason / 联想 / 归纳 / 总结).
4. Document scan result in plan / commit message (3-5
   most relevant P-n / M-n + 1-line reason each).

**Why this 段 is BEFORE "Read first"**: per M-n 13
layer-extension, L0 surface must expose M-pre-task-scan
so fresh agents pick it up **without** 你 turn having to
point it out (per 你 turn "我跟你说问题的时候，你需要
找办法，避免下一次还出现一样的/相似的问题").

**Trigger** (per M-n 34): any 你 turn (including "fix
this" / "explain" / "commit" / "task done" / "verify") OR
new session start.  Per AGENTS.md "Read first" 段 below
+ M-n 31 Phase 1 task-init + M-n 16 stage 1-2 观察+归纳.

**Anti-pattern** (per M-n 32 self-learning-guardrail +
你 turn 2026-07-16): skip the scan, rely on memory alone,
be told by 你 turn what to read.  This is the **exact**
failure mode M-n 34 is designed to prevent.

## "继续" protocol (per 你 turn 2026-07-16)

Per 你 turn "我说继续的时候, 一般都和我之前说的
那段是一个意思":

When 你 turn says "继续", agent MUST interpret it as:
**推进任务 (考虑之前说的那些思考方法, 考虑是否
重新做规划等, 考虑自顶向下等原则)**, NOT as a
generic continuation.

**Two cases**:

| Case | 你 turn signal | Agent action |
|---|---|---|
| **任务未完成** | 你 turn 你 turn implicit (e.g., previous turn left tasks undone) | Continue: apply thinking methods (5 primitives + 4 critical-thinking + 自顶向下分治); replan if撞到一起 (per M-n 12 + M-n 28 4-condition); keep committing |
| **任务完成** | 你 turn 你 turn "验收" / "完成了" / explicit done | Apply M-n 29 5-step acceptance protocol: design 验收 角度, execute 5 primitives + 4 critical-thinking, validate all PASS, cycle if FAIL, **明确告知** (per 你 turn "完成了的时候跟我明确说明情况") |

**Anti-patterns**:

- DON'T stop mid-task and ask "next" (per
  PITFALL 39 batch rule).
- DON'T ignore thinking methods when continuing.
- DON'T skip 验收 when task is done.
- DON'T claim "task done" without M-n 29 5-step
  (per M-n 32 Guardrail #4).

## "学习一下" protocol (per 你 turn 2026-07-16)

Per 你 turn "我说学习一下的时候, 指的是不仅仅
是hermes学习, 也是这几个项目里 agent 的核心层
/ 用户层需要学习, 需要在迁移到其他用户之后还能
有充足的这类知识":

"学习" = **cross-project learning**, NOT single-
hermes learning.

**Three layers of learning**:

| Layer | Where | What | Persistence |
|---|---|---|---|
| **核心** | `core-layer/` + `AGENTS.md` + `hooks/` + `.hermes/scripts/` + `OPERATING_RULES.md` | Agent behavior rules | Cross-project, cross-user (migrates to other users' machines via skill) |
| **用户** | `memory/` system + user-specific files | User habits / preferences | Cross-session (per user) |
| **项目** | `docs/PRINCIPLES.md` + `docs/PROJECT_STATE.md` + project docs | Project-specific knowledge | Per project (NOT cross-project) |

**Cross-project requirement**: per 你 turn
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

## "主动修改 skill" (per 你 turn 2026-07-16)

Per 你 turn "我希望这skill在别人电脑上还会主动
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

## Iterative thinking (per 你 turn 2026-07-16)

Per 你 turn "有的时候, 一层思考不够充分, 执行
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
2. **Termination by user signal**: 你 turn
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

## Skill context cleanliness (per 你 turn 2026-07-16)

Per 你 turn "skill 库是最终面向用户的库, 需要
为新agent保持项目上下文干净":

When working on skills (or any user-facing
artifact):

- **NO dev-session references** in skill content
  (e.g., "per 你 turn 2026-07-16 retrospective" =
  dev history; not user-facing).
- **NO SUA-specific examples** in skill content
  (e.g., "in SUA, we have Y" = project-specific;
  not portable).
- **YES generic patterns** (e.g., "When user
  shows consistent preference" = universal; user-
  facing).

**Audit checklist** before declaring skill ready:

1. Search skill for "per 你 turn <date>" → should
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

## Read first (in order)

1. `docs/PRINCIPLES.md` — operating principles (P1-P29, 25 working per c47a/c78/c79/c80 + c96 P28 lift + c167 P29 lift).  Read
   the FULL file (~11 KB).  Do not skim.
2. `docs/INDEX.md` — orientation map (8-step reading order
   + conditional stealth loads).  Follow the numbered steps
   until you have a project overview.
3. `docs/PROJECT_STATE.md` — current goal, version, next
   step (1-paragraph snapshot).
4. `docs/PRINCIPLES_DETAIL.md` — full text of each P-n (L2
   detail).  Read when you need the rationale behind a rule.
5. `docs/SWITCH_SIGNALS.md` — switch signals + action
   protocol (consulted before every user-message response;
   see conditional load below for trigger reminder).
6. `docs/HOW_TO_READ_GRAPH.md` — read pattern for new
   agents (per c57, the 3-step pattern: L0 → L1 → L2,
   with cross-ref traversal rules + 5 essence families
   + 7-check self-org).  Read when entering the project
   or when stuck on graph traversal.
7. `docs/OPERATING_RULES.md` — M-n 1-34 operating rules
   (per M-n 34 pre-task scan: scan this file for M-n
   applicable to your current task).  Read when task
   needs M-rule application OR per M-n 34 step 2.
8. `core-layer/README.md` — L0 marker for the **3-layer
   governance** (per 你 turn 2026-07-16).  Read when
   modifying AGENTS.md / hooks/ / .hermes/scripts/ /
   OPERATING_RULES.md — these are the 核心 layer (agent
   self-edit only, with eval-before + verify-after gate).
   See `core-layer/governance-template.md` for the gate
   template.
9. `docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md` — L2
   detail for the **4 critical-thinking primitives**
   (质疑/逆向/预演失败/对立论证 — per 你 turn 2026-07-16).
   Read alongside items 1-5 primitives.  Constructive
   thinking (5 primitives) + adversarial thinking
   (4 critical primitives) = full thinking pair (per
   M-n 14 two-track).
10. `docs/M_PRE_RELEASE_AUDIT_DETAIL.md` — L2 detail
    for **release preparation** (M-n 36, per 你 turn
    2026-07-16 retrospective).  Read when tagging x.0.0
    release, pushing to github, publishing to package
    manager, or distributing zip.  Contains 5 checks
    (commit cleanliness / tag at HEAD / CHANGELOG /
    artifact / docs) to prevent "github commit
    confusion" pattern.

**Note**: items 5-7 are added per M-n 34 (2026-07-16) so
fresh agents can find all rules, not just P-n.  Per
P21 cross-project, this list stays SUA-specific
(sibling repos have their own entry docs).

Item 8 added per 3-layer architecture (你 turn
2026-07-16) — the core-layer/ directory has its own
governance template separate from docs/ because
modification rules differ (核心 = agent-only).

## Hard rules (top 6 from PRINCIPLES.md, binding)

If you violate these, your commit is rejected by the commit-msg
hook (it scans for the `P##` reference; the rule cited is the one
that motivated the change).

- **P5** — measure twice, commit once.  Tests must pass before
  commit.
- **P11** — write the summary BEFORE the detail; do not
  duplicate.
- **P14** — if you change code that drifts a doc, update the
  doc in the same commit.
- **P17** — never claim green when it is yellow.  If you
  cannot verify, say so explicitly.
- **P20** — every doc must have an L0 line (≤ 120 chars).
  Prefer existing file; split if a doc does two jobs.
- **P22** — when stuck, STOP.  Look at the project state, then
  write a plan.  Do not brute-force past a wrong assumption.

## What NOT to do

- Do not create parallel doc structures (M33).  If PRINCIPLES.md
  covers it, point to it; do not restate.
- Do not commit to `../knowledge-graph-seed/` from this project
  (P21).  Cross-project links use relative paths.
- Do not invent features you have not verified (M79 — test
  before claiming; M82 — commit gate before declaration).
- Do not stuff conditional content into always-read files
  (per "storage layered / read flat" principle — see
  `docs/RECURSIVE_DECOMPOSITION.md`).

## Task-done-notify reminder (per 你 turn 2026-07-16)

Per 你 turn "我之前说过，skill 最后的时候要验收，你验收
了吗？你不知道要验收这件事" + 你 turn 2026-07-16
"很多地方说的思考都需要用原则里的思考方法。在工作
的时候你经常想不到用这思考方法，你得问问自己为什么"
+ L0.1-L0.3 commits in `fix/m29-trigger-explicit` branch:

**Before any commit / before sending "task done" message**,
agent MUST apply **5 primitives** (per M-n 16 stage 1-2
+ M-n 14 two-track + M-n 25 turn-pattern + M-n 26
context-decay; codified in M-n 29 Step 2):

**Per 你 turn 2026-07-16 + M-n 14 two-track**: complete
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
   (per R11) + components / files / commits involved?
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

2. **Hard external trigger**: per 你 turn 2026-07-16
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
"完成" message — this is the exact failure mode 你 turn
flagged.  Per M-n 32 Guardrail #4 (pre-claim): NOT
allowed to claim PASS before 5-step is complete.

**Per retrospective (2026-07-16, your turn)**: previous
session claimed "✅ Task DONE" multiple times without
applying M-n 29 5-step.  This external trigger script +
AGENTS.md reminder段 are the structural fix.

See:
- `docs/OPERATING_RULES.md` § M-acceptance-protocol (M-n 29
  trigger S1-S5, per L0.1 commit)
- `docs/OPERATING_RULES.md` § M-task-lifecycle (M-n 31 Phase 3
  pre-condition, per L0.2 commit)
- `docs/OPERATING_RULES.md` § M-self-learning-guardrail
  (M-n 32 Guardrail #4, per L0.3 commit)
- `.hermes/plans/2026-07-16_fix-m29-trigger-explicit.md`
  (full plan + 11-commit batch)
- `.hermes/scripts/m_n29_5step.py` (mechanical external
  trigger, per retrospective fix)

## Commit message contract

Every commit message MUST contain at least one `P##` reference
(one of P1-P29) explaining which principle motivated the
change.  The `commit-msg` hook enforces this.

**Hook install** (one-time per clone):

```bash
cp hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

The hook template is tracked in this repo at `hooks/commit-msg`.
After install, git runs it automatically on every commit.

Format:

```
<type>(<scope>): <short description>

Cite one of P1-P29 here, e.g.:
- P5 — "added tests before commit"
- P11 — "rewrote L0/L1 boundary"
- P17 — "documented what is NOT shipped"

Detailed body.
```

Allowed `P##` values: P1, P2, P3, P4, P5, P7, P8, P9, P10,
P11, P12, P13, P14, P17, P18, P19, P20, P21, P22, P23,
P15 (demoted to P5 实操 per c79), P16 (demoted to P5 实操 per c80),
P24 (merged into P3 per c78), P25, P26, P27, P28, P29
(lifted per c167).  See PRINCIPLES.md / PRINCIPLES_DETAIL.md for the complete
list.

## Operating rules (M-n 1-34, per c95-c237 + M-pre-task-scan)

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
- **M-n 25**: turn-pattern-recognition (parse 你 turn + 5 patterns + M-n self-application 4 levels)
- **M-n 26**: context-decay-management (detection + classification + compression + refresh)
- **M-n 27**: knowledge-layer-architecture (3-layer core/knowledge/project + 3 sources hermes/SUA/skill + single-skill fallback)
- **M-n 28**: plan-conditional (4-condition check: uncertain → plan; clear → continue)
- **M-n 29**: acceptance-protocol (5-step protocol: design + 5 primitives + validate + cycle + notify)
- **M-n 30**: knowledge-context-trade-off (4-priority: knowledge 充足 > context 管理 > trade-off via 分层+类比 > 分层 自顶向下 分治 always)
- **M-n 31**: task-lifecycle (4-phase: init + execute + done-notify + retrospective)
- **M-n 32**: self-learning-guardrail (5 modification guardrails + auto-learning)
- **M-n 33**: narrative-as-spec (3-primitive: parse + structure + codify/execute)
- **M-n 34**: pre-task-scan (added 2026-07-16; per 你 turn "自主阅读学习".
  4 sub-steps: Read AGENTS / Scan P-n+M-n / Apply 5 primitives
  / Document scan result.  Per `docs/M_PRE_TASK_SCAN_DETAIL.md`.)

## Recent cross-project sync (per 你 turn 2026-07-15)

Per M-n 30 Priority 5: SUA → skill-incubator (c215) → skill (c219) → KG (c217). All 3 sibling projects have Reading order + SUA cross-ref + Update order rule + "NOT in chain"段 (KG, c232).


**修订 L4 boundary (per c95 + memory 7)**:

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

**Framework-agnostic** (per M-n 20 + 你 turn 2026-
07-15):

- This project designed for Hermes / Codex / Claude
  Code / others.
- File names should avoid Hermes-specific terms.
- Future agents should be able to read this project
  without Hermes-specific knowledge.

## When in doubt

State the ambiguity, list the options you considered, pick one,
apply, and cite the principle in your commit message.  Same as
if you were the maintainer reading your PR.

## Detail (L2)

For "## See also" section (long, conditional load docs), see
[`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).
Per R6, this companion is required when the
summary exceeds 7 KB.
