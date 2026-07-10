---
description: "Working principles distilled from this project — portable across projects"
status: "summary"
---

# PRINCIPLES — Working principles (portable)
L0: The 21 working principles (P1-P21) of this project, with concrete sub-rules for P20.
Last P20-verified: 2026-07-10
L0: Root principles (奥卡姆 + workflow + test-pyramid + doc-structure) → L1 (P1-P23) → L2 (实操).

> Distilled from working on this project (2026-07-08 session).
> These are project-agnostic — copy them to any future project.
> Each rule has a 1-line WHY and a HOW.

## L0: Root principles (the 4 axioms)

Every P-n in L1 is a child of one of these 4 root axioms.  When
a new principle seems needed, it must (a) descend from a root
axiom, (b) not duplicate an existing L1 principle, (c) clear
P7 奥卡姆 — earn its place.

| # | Root axiom | L1 children | WHY |
|---|---|---|---|
| 奥卡姆 | P7, P9, P13, P23 | Minimum API, no rule until 3+ failures, no orphan nodes, doc > script (with nuance) |
| Workflow | P1, P2, P4, P5, P6, P15, P22, P23 | 整理→思考→行动, plan, test pyramid, 1 commit = 1 feature, stage gate, meta-rules |
| Test | P3, P5, P6, P16, P18, P19 | Unit → joint → integration, 真跑再 commit, ad-hoc verify, failure → regression test, data-flow observability |
| Doc | P10, P11, P12, P14, P17, P20, P21 | Entity > prompt, 摘要+引用, knowledge in project, docs current, honest reporting, progressive disclosure, cross-project boundaries |

When updating this doc, **check which root axiom** the change
descends from.  Per P22 步骤 3: 找 rule 之间的共性.

## L2: 实操 (per P-n, how to implement)

Each L1 principle (P-n) has a 1-line "实操" — how to actually
follow the principle.  The实操 references its root axiom (L0)
and any sibling L1 principles.  Per P7 奥卡姆: keep short.

## Workflow principles

### P1. 整理 → 思考 → 行动
Clean the workspace first, then think, then act.  Don't think while
cluttered (you'll lose the thread).  Don't act while undecided
(you'll re-do).

**实操 (L2)**: before any non-trivial work, run `git status` + read
TODO + read recent commits.  Per Workflow root + P22 (stuck→plan).

### P2. 搜资料, 不拍脑门
Before designing a feature, read 5+ relevant sources (papers,
production write-ups, prior art).  Cite them in commit messages.

**实操 (L2)**: open `docs/LITERATURE.md` first; if a relevant paper
exists, cite it.  If not, do `web_search` + add 1-line to
LITERATURE.  Per Workflow + Test roots.

### P3. 单元 → 联合 → 集成
Tests form a pyramid:
- **Unit**: one mechanism in isolation (atomic, fast)
- **Joint**: multiple modules together (the contract)
- **Integration**: real run with real inputs (the truth)

Skip integration = "passing tests but broken in production".

**实操 (L2)**: per new feature, write unit (fast) + joint (mock)
+ integration (real LLM if applicable) tests before commit.  Per
Test root.

### P4. 1 commit = 1 logical feature
Multi-file is fine if they form one feature.  Atomic-per-file is
not the goal.  The goal is **per-feature commit** with **all
3 layers of testing green before commit**.

**实操 (L2)**: commit message starts with `feat:` / `fix:` /
`docs:` / `chore:` + 1-line WHY.  Per Workflow root.

### P5. 测通再 commit
"测通" = unit + joint + integration.  Not "I ran a test".
Especially: integration tests catch bugs the unit tests can't
(no mocking, real env).

**实操 (L2)**: before `git commit`, run full suite (with
`HERMES_FAST=1`) + 1 integration smoke.  Per Test root.

### P6. 真跑再 commit, 不猜
If the user has a real-world run they care about, simulate it
yourself before commit.  Don't assume "if it parses, it works".

**实操 (L2)**: if user gave a real cmd, run it (or a smoke-test
mock) and include the output in commit.  Per Test root.

### P22. Stuck → plan + update docs (meta-rule)
When a big task starts and thinking is fuzzy, **stop and look at
project state** (working tree, recent commits, current docs, test
status), then **write a plan down** before continuing.

Three actions, in order:
1. **Check state**: `git status`, `git log --oneline -10`, list
   `docs/`, count tests, identify which docs are stale (per P14).
2. **Write plan**: goal, current state, next steps, risk.  Not
   "thinking out loud" — a written plan is reviewable, mutable,
   and survives the next context window.
3. **Update docs**: for any new meta-rule discovered, find which
   existing principle (P1-P21) is most related.  Look for
   **commonalities** (P22 + P1 share "先思考再行动").  Add
   cross-references rather than redefining.  Per P20 progressive
   disclosure: L0 summary, L1 detail, L2 deep — pick the right
   layer.  Per P7 奥卡姆: don't duplicate; reference.

This rule applies recursively: when planning the docs update,
itself trigger P22 ("which doc layer? which existing rule?").

**实操 (L2)**: when stuck, write 3 lines (state, plan, risk) to
chat before continuing.  Update PRINCIPLES.md as needed.  Per
Workflow + Doc roots.

### P23. Doc > script, with nuance
Per user 2026-07-10 '不需脚本, 文档就能规范 agent 行为':
**a well-written doc IS the contract**.  Don't write a script
to mechanically enforce a doc rule until the doc rule has been
broken 3+ times (per P7 奥卡姆 — earn the script).

Nuance: script is **allowed** (not banned), but only after the
doc has been clearly stated AND violated enough times to justify
the maintenance cost.  Pattern: doc-first → violations → script.
**Script is the SECOND step, never the first.**

Related: P20 progressive disclosure (doc structure) and
`scripts/check_docs.py` was deleted in 9d75533 because the doc
contract (P20.细则 R1-R12) was still being internalized — too
early for mechanical enforcement.  Re-introduce only when
violations become a real cost.

This rule clarifies the original "doc > script" 哲学:
"doc > script" means "doc first, script after — not script never".

**实操 (L2)**: when tempted to write a check script, first write
or update the doc rule, run for a few cycles, then decide if the
script is needed.  Per Doc + 奥卡姆 roots.

## Design principles

### P7. 奥卡姆剃刀
Don't add rules until you have 3 concrete failures that demand
them.  Defaults: minimal API surface, no abstraction layers until
needed, no framework until you've used it for real.

**实操 (L2)**: before adding a new module/flag/principle, ask "is
this the 3rd time we need it?"  If no, defer.  Per 奥卡姆 root.

### P8. Fail-OPEN by default
When uncertain, **let the LLM decide**, don't pre-filter.  Soft
gates (logs, warnings) are fine; hard gates (rejections) require
justification.

**实操 (L2)**: when designing a check, default to warning + log,
not raise.  Per 奥卡姆 root.

### P9. Hard rule, not LLM-judged
Some rules must NOT be LLM-judged.  Determinism over flexibility.
Examples: P20 doc structure, P11 摘要+引用, file naming.

**实操 (L2)**: per "doc structure", `INDEX.md` order, file naming,
test naming — all mechanical, not LLM-judged.  Per 奥卡姆 root.

### P10. Entity behavior > prompt instruction
Prefer creating a new entity (class, module) with explicit
behavior over relying on a prompt to instruct the LLM.  Prompts
are mutable; code is reviewable.

**实操 (L2)**: when tempted to "add to the prompt", first ask
"can this be a function or class?"  Per Doc + 奥卡姆 roots.

### P11. 摘要 + 引用 structure
Each doc file has a 1-paragraph summary + pointer to detail.
LL0 reader = summary only.  L1 = summary + first 3 paragraphs.
L2 = full doc.

**实操 (L2)**: every `docs/*.md` ends with "Read if…" pointer.
Long docs have `_DETAIL.md` companion.  Per Doc + P20 roots.

### P12. Knowledge in project, not agent memory
Anything important must be in a file, not in the agent's
context window.  Files survive context loss; context doesn't.

**实操 (L2)**: before saying "remember this", write to
`docs/` or `TODO.md` or `DONE.md`.  Per Doc root.

### P13. No orphan nodes
Every doc has a parent (INDEX, README, or another doc).  Every
code file has an import.  Every principle has a WHY.

**实操 (L2)**: when adding a new file, add it to INDEX or a
parent.  Per 奥卡姆 root.

### P14. Documents stay current
After any code change that affects docs, update docs in the
**same commit**.  Stale docs are worse than no docs (they lie).

**实操 (L2)**: per commit, if docs/*.md or README change → same
commit.  Per Doc root.

### P15. Stage gate + cleanup
After each significant stage, run a gate check (tests, docs,
working tree, no tempfiles) before moving on.  Clean as you go.

**实操 (L2)**: per major commit, add a "DONE.md stage gate" line.
Per Workflow + Doc roots.

### P16. Ad-hoc verify, then commit
When correctness is uncertain, write a small `hermes-verify-*.py`
in Temp, run it, summarize the result, then commit.  Clean up the
script after.

**实操 (L2)**: when 3+ unit tests pass but integration is
uncertain, write minimal ad-hoc verify.  Per Test root.

### P17. Honest reporting
Report actual results, not aspirational results.  "ad-hoc
verified, not fully verified" beats "fully verified" when the
former is the truth.

**实操 (L2)**: in commit messages + chat replies, distinguish
"测过 (ad-hoc)" from "fully verified (full suite + integration)".
Per Doc root.

### P18. Failure → regression test
Every failure mode (a test that failed, an LLM output that
crashed, a config that broke) becomes a permanent regression
test.  Production-grade systems are built on this rule.

**实操 (L2)**: when a real failure is observed, add a test that
reproduces it before fixing.  Per Test root.

## References

- INDEX: [INDEX.md](INDEX.md)
- Project state: [PROJECT_STATE.md](PROJECT_STATE.md)
- User intent: [USER_INSIGHTS.md](USER_INSIGHTS.md)
- Constraints: [CONSTRAINTS.md](CONSTRAINTS.md)
- LLM choice: [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- Literature: [LITERATURE.md](LITERATURE.md)
- Pending tasks: [../../TODO.md](../../TODO.md)


## Data Flow (P19)

**P19: Data flow observability**

When functions execute sequentially (A → B → C), persist A's
output to disk so B can read it without re-running A.  This:
  - Makes the data flow observable (`cat upgrades/foo.jsonl`)
  - Lets us replay a step without redoing prior steps
  - Lets us debug which input led to which output
  - Survives crashes (we can pick up where we left off)

Per user insight 2026-07-09: '如果有几个功能是顺序执行,
你可以先把前面的输出存下来, 作为下一个功能的输入'.

Concrete pattern in v3.0.1:
  - `read_papers()` -> `save_summaries()` (JSONL overwrite)
  - `read_summaries()` -> `select_best()` -> `save_decision()` (JSONL append)

Format: JSONL (one record per line).  Append-only for events,
single-snapshot for state.

**实操 (L2)**: per sequential function chain, write `save_X()` +
`read_X()` to `upgrades/X.jsonl`.  Per Test + Doc roots.

## Meta principles

### P20. 渐进式披露 (progressive disclosure)

Documents should expose content in layers, each layer addressing a
different consumer question.  The default reader is an agent that
DOES NOT know the project's full context — it should be able to
read **only the layers it needs** and stop.

**实操 (L2)**: every new doc starts with L0 (1-line header) +
L1 (1-3 paragraphs).  L2 is the rest.  Per Doc root.

Three layers, in order of increasing cost:

| Layer | Question it answers | When to write | When the agent reads it |
|---|---|---|---|
| L0 — Pointer | "Where do I look?" | Always (header line) | Default (always read) |
| L1 — Summary | "What is this in 30 seconds?" | Always (1-3 paragraphs) | When L0 matches a need |
| L2 — Detail | "Give me the full story" | Optional, by file size | When L1 prompts a question |

Rules:
- A document with no L1 is **stealth** — only the agent that
  actively searches for it finds it.  Use for cross-project
  pointers (e.g. `docs/EXTENSIONS.md`) and ideas-not-yet-projects.
- A document's L1 must be readable in < 2 min (target ≤ 2KB).
  A document's L2 is for the consumer who already knows they
  need the full story (target ≤ 7KB).  If longer, the document
  is doing two jobs and should be split (P11 applies).
- L0 must be a single line (or short table cell).  No prose.
- P20 is recursive: this principle's own definition follows P20.
  L0 = the section header, L1 = this paragraph, L2 = the table.

Failure mode P20 guards against:
- An agent that "doesn't know there's an EXTENSIONS.md" loads
  every file referenced in INDEX.md.  That defeats the purpose
  of having a per-doc L0.
- An agent that "knows" a doc exists, reads all of it, including
  the parts not relevant to its task.  P20 layers let the agent
  stop after L0 or L1.

### P20.细则 (concrete rules — mechanical, not interpreted)

> P20 is the principle (abstract); this list is the binding
> contract.  Each rule is doc-level (mentally checked by future
> agents per P20 self-discipline).  Per the user's 2026-07-10
> framing: "原则 (P20) = 抽象类, 细则 = 具体实现".

| # | Rule | Failure mode it catches |
|---|---|---|
| R1 | `INDEX.md` must contain exactly two top-level sections after the intro: "Reading order for a new agent" and "Conditional loads".  No third category. | A new doc created and added to INDEX as "Helpful resources" or "Other" — bypasses the layer contract. |
| R2 | The "Reading order" section must number its links 1..N contiguously (no gaps, no duplicates). | Renumbering accident or skipped step that confuses the reader. |
| R3 | Every link in "Conditional loads" must have a `trigger:` annotation (one line, ≥ 5 words) describing when to read it. | Stealth doc with no clear "when to read" — defeats the purpose of being conditional. |
| R4 | `EXTENSIONS.md` must be ≤ 500 bytes AND contain only a table (no prose paragraphs before/after). | The pointer file becomes a narrative — now the agent reads it to "understand" instead of to "look up". |
| R5 | Every `docs/*.md` file ≤ 7KB is "self-contained summary".  Every file > 7KB must have a `*_DETAIL.md` companion whose name starts with the summary's filename minus `.md`. | A long doc that doesn't split — agent reads 12KB to get the 2KB it needed. |
| R6 | `_DETAIL.md` companions must be referenced (linked) from their summary file.  A `_DETAIL.md` with no inbound link is an "orphan detail" and must be deleted or referenced. | Dead file that future agents trip over. |
| R7 | Principles (P-n) are defined ONLY in `PRINCIPLES.md` (this file).  Any other `docs/*.md` may REFERENCE a P-n but must NOT redefine it.  Redefinition is a hard violation. | Drift: parent says P7 is X, child says P7 is Y — system collapses. |
| R8 | Cross-project links use relative paths (`../other-project/...`).  Absolute paths or `https://` (except for external sources) are not allowed in `docs/`. | A doc breaks when the project is moved or cloned. |
| R9 | Every `docs/*.md` must begin with a single-line `L0:` frontmatter (≤ 120 chars) describing what the file is, in plain language.  This line is the L0 layer; the rest is L1+. | Doc with no L0 = not findable by the L0-only reader. |
| R10 | Every `docs/*.md` should end with a `Last P20-verified: YYYY-MM-DD` line, updated whenever the doc is meaningfully changed. | Stale doc — the L0/L1/L2 contract was true on date X but may have rotted. |
| R11 | Before commit, mentally check R1-R10 against any changed/new `docs/*.md` file. | New doc slipped in without verify, rotting the layer contract. |
| R12 | When `PRINCIPLES.md` is modified, every child project's `docs/PHILOSOPHY.md` (if it exists) must be re-synced in the SAME commit.  Per P21. | Parent-child drift: parent adds P22, child doesn't know, child cites "P1-P21" forever. |

How to use this list (per user 2026-07-10 'doc > script' 哲学):
1. Before any `docs/*.md` change, mentally check R1-R12.
2. No mechanical script — doc-level self-discipline.
3. If a rule is too strict in practice, update the rule — don't
   skip or weaken it.

### P21. Independent projects (cross-project boundaries)

When a project is referenced from another project's docs, the
referencing project should **link to a location, not duplicate
content**.  The referenced project should be **readable on its
own** (or have a single, clearly-stated "this is incomplete,
read the parent" disclaimer).

**实操 (L2)**: when referencing another project, link to a path,
not copy content.  Use EXTENSIONS.md as pointer file.  Per Doc
root.

Rules:
- Each project has its own `docs/` tree, its own PRINCIPLES,
  its own PHILOSOPHY (when relevant).  No "main project owns
  the truth" assumption.
- Cross-project links use relative paths (`../other-project/...`),
  not absolute paths or doc IDs.
- A project's PHILOSOPHY may inherit principles from another
  project **only if** the inherited text is reproduced in full
  (no "see P7 in parent" shortcuts).  Add a `synced from
  <parent> as of <date>` marker so drift is detectable.
- A principle that is "new" to a child project must be
  **proposed in the parent first**, then the child can reference
  it.  A child cannot mint new principles the parent doesn't have.

This is the formal statement of the philosophy behind
`docs/EXTENSIONS.md` (parent) and `docs/PHILOSOPHY.md` (children).

- Done tasks: [../../DONE.md](../../DONE.md)