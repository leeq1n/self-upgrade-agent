# AGENTS — Operating Rules for AI Agents in This Project
Last P20-verified: 2026-07-15

> L0: AI agents entering this repo MUST read `docs/PRINCIPLES.md`
> FIRST.  Treat each P-n as binding unless the user explicitly
> overrides it for a task.  Commits that ignore PRINCIPLES will
> be caught by the commit-msg hook (P-n cite required).

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

2. Include a **"Cold-start simulation"** section in the
   验收 report: list 3+ trigger points in the project
   + verify each is reachable from the entry doc by a
   fresh agent (per P25 step 7 + P26 fresh-agent simulation).

3. Cite the P-n / M-n that motivated each acceptance
   criterion (per commit-msg hook contract above).

**Anti-pattern**: skipping 5-step and going directly to
"完成" message — this is the exact failure mode 你 turn
flagged.  Per M-n 32 Guardrail #4 (pre-claim): NOT
allowed to claim PASS before 5-step is complete.

See:
- `docs/OPERATING_RULES.md` § M-acceptance-protocol (M-n 29
  trigger S1-S5, per L0.1 commit)
- `docs/OPERATING_RULES.md` § M-task-lifecycle (M-n 31 Phase 3
  pre-condition, per L0.2 commit)
- `docs/OPERATING_RULES.md` § M-self-learning-guardrail
  (M-n 32 Guardrail #4, per L0.3 commit)
- `.hermes/plans/2026-07-16_fix-m29-trigger-explicit.md`
  (full plan + 11-commit batch)

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

## Operating rules (M-n 12-33, per c95-c237)

**33 M-n** in `docs/OPERATING_RULES.md`:

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
