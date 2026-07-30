# AGENTS Core (always-loaded)

> **LAYER**: 核心 (L0 cache-stable — always-loaded, M-n 15 modification rule)
>
> L0: Always-loaded subset of SUA's AGENTS.md
> for cache-stable prefix + minimal input tokens.
>
> Per cache optimization protocol (per docs/PRINCIPLES.md
> + docs/OPERATING_RULES.md): this file = ~6.4K chars
> (100% cache hit when stable).  Per-task 段s are in
> `AGENTS.md` as references (per P11 摘要+引用).
>
> **2026-07-20 architecture note**: SUA is the knowledge
> library for the hermes-root family; siblings are
> standalone (agent-reflection-skill) or frozen
> (knowledge-graph-seed MVP).  skill-incubator was
> archived; its content consolidated into SUA's
> `docs/SKILL_DESIGN.md`.  Cross-ref details in
> AGENTS.md "Recent cross-project sync"段.
>
> Cross-ref: full content here.  AGENTS.md has
> references, not duplicates.

## What's here vs full AGENTS.md

| Here (always-loaded) | AGENTS.md (per-task) |
|---|---|
| Pre-task scan (M-n 34) | (P11 ref) |
| Read first (in order) | (P11 ref) |
| Hard rules (top 6 from PRINCIPLES.md, binding) | (P11 ref) |
| What NOT TO DO | (P11 ref) |
| Commit message contract | (P11 ref) |
| When in doubt | (P11 ref) |
| (P11 ref) | "继续" protocol |
| (P11 ref) | "学习一下" protocol |
| (P11 ref) | "主动修改 skill" protocol |
| (P11 ref) | Iterative thinking protocol |
| (P11 ref) | Recursive test-verify protocol |
| (P11 ref) | Skill context cleanliness |
| (P11 ref) | Multi-perspective audit angles |
| (P11 ref) | Task-done-notify reminder |
| (P11 ref) | Post-completion verification suggestion |
| (P11 ref) | Operating rules (M-n 1-34) |
| (P11 ref) | Recent cross-project sync |
| (P11 ref) | Detail (L2) |

## Sections (always-loaded content follows)

## Pre-task scan (M-n 34)

**Per "自主阅读学习" protocol + M_RULE_AUTHORING
3-condition gate**: before any user message response, before any
commit, before any "task done" message — agent MUST run
**M-n 34 pre-task scan** (4 sub-steps per
`docs/OPERATING_RULES.md` § M-pre-task-scan):

1. Read this `AGENTS.md` (you are here — L0 entry doc).
2. Scan `docs/PRINCIPLES.md` L0 axioms + `docs/OPERATING_RULES.md`
   all M-n.  Mark YES / NO / MAYBE for current task.
3. Apply 5 primitives (Analyze / Reason / 联想 / 归纳 / 总结).
4. Document scan result in plan / commit message (3-5
   most relevant P-n / M-n + 1-line reason each).

**Reasoning checklists are internal by default.** Run the scan and the
5 constructive / 4 critical primitives internally. Do not print the
full checklist, quote the user's message repeatedly, or narrate every
reasoning stage unless the user asks for that trace. A normal reply
should lead with the conclusion and the evidence needed to act.

**Response readability gate:** before sending any reply, scan the draft
for repeated role labels, repeated short phrases, unfinished equations,
or templated sections that no longer carry meaning. If any appear,
discard the draft and rewrite it once in plain language. Do not diagnose
a malformed draft inside that same draft.

**Why this section is BEFORE "Read first"**: per M-n 13
layer-extension, L0 surface must expose M-pre-task-scan
so fresh agents pick it up **without** external instruction
(per P7 Occam — avoid repetition in working memory).

**Trigger** (per M-n 34): any user message (including "fix
this" / "explain" / "commit" / "task done" / "verify") OR
new session start.  Per AGENTS.md "Read first" 段 below
+ M-n 31 Phase 1 task-init + M-n 16 stage 1-2 观察+归纳.

**Anti-pattern** (per M-n 32 self-learning-guardrail):
skip the scan, rely on memory alone,
be told by external instruction what to read.  This is the **exact**
failure mode M-n 34 is designed to prevent.


## Read first (in order)

1. `docs/PRINCIPLES.md` — operating principles (P1-P29, 25 working
   per docs/OPERATING_RULES.md version notes — see lift/demote history
   in PRINCIPLES_DETAIL.md).  Read the FULL file (~11 KB).
   Do not skim.
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
   agents (per 3-step pattern: L0 → L1 → L2,
   with cross-ref traversal rules + 5 essence families
   + 7-check self-org).  Read when entering the project
   or when stuck on graph traversal.
7. `docs/OPERATING_RULES.md` — M-n 1-34 operating rules
   (per M-n 34 pre-task scan: scan this file for M-n
   applicable to your current task).  Read when task
   needs M-rule application OR per M-n 34 step 2.
8. `core-layer/README.md` — L0 marker for the **3-layer
   governance**.  Read when
   modifying AGENTS.md / hooks/ / .hermes/scripts/ /
   OPERATING_RULES.md — these are the 核心 layer (agent
   self-edit only, with eval-before + verify-after gate).
   See `core-layer/governance-template.md` for the gate
   template.
9. `docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md` — L2
   detail for the **4 critical-thinking primitives**
   (质疑/逆向/预演失败/对立论证).  Read alongside items 1-5
   primitives.  Constructive thinking (5 primitives)
   + adversarial thinking (4 critical primitives) = full
   thinking pair (per M-n 14 two-track).
10. `docs/M_PRE_RELEASE_AUDIT_DETAIL.md` — L2 detail
    for **release preparation** (M-n 36).  Read when tagging x.0.0
    release, pushing to github, publishing to package
    manager, or distributing zip.  Contains 5 checks
    (commit cleanliness / tag at HEAD / CHANGELOG /
    artifact / docs) to prevent "github commit
    confusion" pattern.

**Note**: items 5-7 added per M-n 34 so fresh agents can find
all rules, not just P-n.  Per P21 cross-project, this list
stays SUA-specific (sibling repos have their own entry docs).

Item 8 added per 3-layer architecture — the core-layer/ directory
has its own governance template separate from docs/ because
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
- When describing a banned word or workaround, **prefer
  Chinese over English indirection** (per 2026-07-20
  directive "用中文, 而不是那个英文词").  Three-paragraph
  English circumlocutions ("an English noun", "that noun",
  "round-based reasoning") violate P7 Occam — they re-
  introduce the mental model the ban was meant to prevent,
  and they are unreadable.  Direct Chinese phrasing
  ("那个会引发解码循环的英文单词", "回合制推理") is shorter,
  clearer, and avoids re-priming the decoder.  This note
  is what makes the rule durable for new agents entering
  this codebase.


## Commit message contract

Every commit message MUST contain at least one `P##` reference
(one of P1-P29) explaining which principle motivated the
change.  The `commit-msg` hook enforces this.

**Hook install** (one-time per clone):

```bash
cp hooks/commit-msg .git/hooks/commit-msg
chmod +x hooks/commit-msg
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
P15 (demoted to P5 实操), P16 (demoted to P5 实操),
P24 (merged into P3), P25, P26, P27, P28, P29
(lifted per docs/OPERATING_RULES.md version notes).
See PRINCIPLES.md / PRINCIPLES_DETAIL.md for the complete
list.


## When in doubt

State the ambiguity, list the options you considered, pick one,
apply, and cite the principle in your commit message.  Same as
if you were the maintainer reading your PR.


