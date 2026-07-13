# AGENTS — Operating Rules for AI Agents in This Project

> L0: AI agents entering this repo MUST read `docs/PRINCIPLES.md`
> FIRST.  Treat each P-n as binding unless the user explicitly
> overrides it for a task.  Commits that ignore this rule will
> be caught by the `commit-msg` hook (it requires a `P##`
> reference in the commit message, per "Commit message contract"
> below).

## Read first (in order)

1. **`docs/PRINCIPLES.md`** — operating principles (P1-P24).
   Read the FULL file (~10 KB).  Do not skim.  The principles
   are the project's operating contract; they override your
   default behavior.
2. **`docs/INDEX.md`** — orientation map (8-step reading order
   + conditional stealth loads).  Follow the numbered steps
   until you have a project overview.
3. **`docs/PROJECT_STATE.md`** — current goal, version, next
   step (1-paragraph snapshot).
4. **`docs/PRINCIPLES_DETAIL.md`** — full text of each P-n (L2
   detail).  Read when you need the rationale behind a rule.

For specific subsystems, follow INDEX.md's "Conditional loads":

- **`docs/LITERATURE.md`** — only if designing a feature or
  evaluating a research idea (P2 — read sources before designing).
- **`docs/OBSERVATIONS.md`** — only if you need empirical context
  from past LLM runs (latency, KEPT ratios, anomalies).
- **`docs/USER_INSIGHTS.md`** — only if confused about user
  intent or paraphrasing rules from past sessions.
- **`docs/EXTENSIONS.md`** — only if work crosses project
  boundaries (e.g. integrating with the knowledge-graph seed).
- **`docs/CONSTRAINTS.md`** — only if you're about to do
  something that might violate a must-not-violate rule (C1, C2...).

## Hard rules (top 6 from PRINCIPLES.md, binding)

If you violate these, the `commit-msg` hook will reject your
commit (it scans for the `P##` reference; the rule cited should
be the one that motivated the change).

- **P1** — 整理→思考→行动.  Don't jump straight to code.
  Look at project state + plan first.
- **P2** — 搜资料, 不拍脑门.  Before designing a feature,
  read 5+ sources.  Open `LITERATURE.md` first; if a relevant
  paper exists, cite it.  If not, `web_search` + add 1-line to
  LITERATURE.
- **P5** — 测通再 commit.  Tests must pass before commit; never
  commit broken tests to a passing baseline.
- **P14** — if you change code that drifts a doc, update the
  doc in the same commit.  Docs must stay current.
- **P17** — never claim green when it is yellow.  If you cannot
  verify a claim, say so explicitly or read the file first.
- **P22** — when stuck, STOP.  Look at the project state, then
  write a plan.  Do not brute-force past a wrong assumption.

## What NOT to do

- Do **not** create parallel doc structures (M33).  If
  PRINCIPLES.md covers it, point to it; do not restate.
- Do **not** commit to the `knowledge-graph-seed/` repo from
  this project (P21 — cross-project independence).  This
  project's scope is self-upgrade-agent only; KG-side work
  lives in its own repo.
- Do **not** invent features you have not verified (M79 / M82).
  "Yellow claimed as green" is the textbook failure mode.
- Do **not** `git add -A` (M25) except when explicitly doing a
  squashed initial commit (the user must authorize that
  exception in advance).
- Do **not** skip the "Read first" order.  PRINCIPLES.md is the
  project's operating contract; it must come before any code
  change.

## Commit message contract

Every commit message MUST contain at least one `P##` reference
(one of P1-P24) explaining which principle motivated the change.
The `commit-msg` hook enforces this.

**Hook install** (one-time per clone):

```bash
cp hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

The template lives at `hooks/commit-msg` (in this repo, tracked).
After install, git will run it automatically on every commit.

Format:

```
<type>(<scope>): <short description> [P##]

[Detailed body, optionally citing more P-n values.]

[Cite one of P1-P24 here, e.g.:
 - P1  — "made a plan before coding"
 - P2  — "searched literature first"
 - P5  — "added tests before commit"
 - P14 — "fixed doc drift to match code"
 - P17 — "documented what is NOT shipped"
 - P22 — "stopped and planned when stuck"]
```

Allowed `P##` values: P1, P2, P3, P4, P5, P6, P7, P8, P9, P10,
P11, P12, P13, P14, P15, P16, P17, P18, P19, P20, P21, P22, P23,
P24.  See PRINCIPLES.md / PRINCIPLES_DETAIL.md for the complete
list.

## When in doubt

State the ambiguity, list the options you considered, pick one,
apply, and cite the principle in your commit message.  Same as
if you were the maintainer reading your PR.

## See also

- `docs/PRINCIPLES.md` — the principles themselves (P1-P24)
- `docs/INDEX.md` — orientation map
- `docs/PROJECT_STATE.md` — current state (1-paragraph)
- `docs/PROJECT_STATE_DETAIL.md` — version history + vision
- `docs/PRINCIPLES_DETAIL.md` — full text of each P-n
- `docs/OBSERVATIONS.md` — empirical context from past runs