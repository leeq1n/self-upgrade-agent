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

## Operating rules (M-n 12-31, per c95-c228)

**31 M-n** in `docs/OPERATING_RULES.md`:

- **M-n 12**: terminology-clarity (refine "撞到一起" → "replan")
- **M-n 13**: layer-extension (L0/L1/L2 + extensions)
- **M-n 14**: two-track-reasoning (类比+逻辑, 6-stage distribution)
- **M-n 15**: principle-reordering (6-step after 原则 混乱)
- **M-n 16**: observe-think-execute (6-stage + top-down 分治)
- **M-n 17**: context-freshness-check (intra-agent + inter-domain)
- **M-n 18**: recursive-summary-protocol (6 sub-steps + 节点 生命周期)
- **M-n 19**: file-naming-convention (PLAN dir + name + L2 companion)
- **M-n 20**: agent-discoverability-check (cross-framework + naming + discoverability + memory persistence)
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
- **M-n 31**: task-lifecycle (4-phase: task-init + task-execute + task-done-notify + task-retrospective, per 你 turn directive "中优先级 567 处理" item 6 + 7)

## Recent cross-project sync (per 你 turn 2026-07-15)

Per M-n 30 + 你 turn verification directive:
- SUA → skill-incubator: README.md c215
- SUA → skill: SKILL_DETAIL.md c219
- SUA → KG: AGENTS.md c217

**All 3 sibling projects now have explicit
Reading order + SUA P-n/M-n cross-ref.**


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
