---
description: "Working principles distilled from this project — portable across projects"
status: "summary"
---

# PRINCIPLES — Working principles (portable)
L0: The 21 working principles (P1-P21) of this project, with concrete sub-rules for P20.
Last P20-verified: 2026-07-10

> Distilled from working on this project (2026-07-08 session).
> These are project-agnostic — copy them to any future project.
> Each rule has a 1-line WHY and a HOW.

## Workflow principles

### P1. 整理 → 思考 → 行动
Clean the workspace first, then think, then act.  Don't think while
cluttered (you'll lose the thread).  Don't act while undecided
(you'll re-do).

### P2. 搜资料, 不拍脑门
Before designing a feature, read 5+ relevant sources (papers,
production write-ups, prior art).  Cite them in commit messages.

### P3. 单元 → 联合 → 集成
Tests form a pyramid:
- **Unit**: one mechanism in isolation (atomic, fast)
- **Joint**: multiple modules together (the contract)
- **Integration**: real run with real inputs (the truth)

Skip integration = "passing tests but broken in production".

### P4. 1 commit = 1 logical feature
Multi-file is fine if they form one feature.  Atomic-per-file is
not the goal.  The goal is **per-feature commit** with **all
3 layers of testing green before commit**.

### P5. 测通再 commit
"测通" = unit + joint + integration.  Not "I ran a test".
Especially: integration tests catch bugs the unit tests can't
(no mocking, real env).

### P6. 真跑再 commit, 不猜
If the user has a real-world run they care about, simulate it
yourself before commit.  Don't assume "if it parses, it works".

## Design principles

### P7. 奥卡姆剃刀
Don't add rules until you have 3 concrete failures that demand
them.  Defaults: minimal API surface, no abstraction layers until
needed, no framework until you've used it for real.

### P8. Fail-OPEN by default
Don't pre-filter / pre-judge.  Let the LLM (or the next layer)
make the call.  Pre-filters are anti-patterns unless backed by
hard data.

### P9. Hard rule, not LLM-judged
For binary decisions (decision = KEPT or REVERTED), use a hard
rule (tests pass) rather than asking the LLM to judge.  Avoids
the coherence trap where the model judges its own output.

### P10. Entity behavior > prompt instruction
Harness-implementation details (typing imports, sandbox setup,
file paths) belong to **entity code**, not the prompt.  The
prompt carries the task; the entity enforces the rules.
OOP-style: abstract method describes what, entity implements how.

## Documentation principles

### P11. 摘要 + 引用 structure
Every doc has two parts: a summary (1 paragraph + bullets, < 60
lines) and a `_DETAIL.md` companion (long form).  Reading the
summary should orient; clicking into detail should be optional.

### P12. Knowledge in project, not agent memory
Paper notes, design decisions, working principles — put them in
the project's `docs/`.  Agent memory is volatile; project docs
are durable.  Future agents start with the docs, not with memory.

### P13. No orphan nodes
Every 1st-level entry should link to its 2nd-level details.
Check programmatically: for every summary, verify a link to its
_DETAIL companion or to another doc exists.

### P14. Documents stay current
After every stage gate (every commit that closes a TODO), update
the docs.  Stale docs are worse than missing docs (they mislead).

## Process principles

### P15. Stage gate + cleanup
After every stage gate (close a TODO, hit a milestone):
1. Move item from TODO.md to DONE.md
2. Update PROJECT_STATE.md (one paragraph)
3. Verify docs have no orphans (programmatic check)
4. Commit doc updates as part of the stage gate

### P16. Ad-hoc verify, then commit
Before each commit:
1. Run the unit + joint tests (fast)
2. Run an integration trace if it's a structural change
3. Save the verifier script as `hermes-verify-N.py` in temp dir
4. Run the verifier, log the result
5. Delete the verifier script
6. Now commit

The verifier is **for one-time use** — it documents what you
checked, then it goes away.

### P17. Honest reporting
- Don't claim green when it's yellow
- Don't claim yellow when it's red
- "测通了" = unit + joint + integration all green
- "测了" = some tests run
- "跑了" = ran the user's actual workflow

### P18. Failure → regression test
Every failure mode (a test that failed, an LLM output that
crashed, a config that broke) becomes a permanent regression
test.  Production-grade systems are built on this rule.

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

## Meta principles

### P20. 渐进式披露 (progressive disclosure)

Documents should expose content in layers, each layer addressing a
different consumer question.  The default reader is an agent that
DOES NOT know the project's full context — it should be able to
read **only the layers it needs** and stop.

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
> contract.  Each rule is mechanically checkable by
> `scripts/check_docs.py` — a violation is a verify FAIL, not
> a judgment call.  Per the user's 2026-07-10 framing:
> "原则 (P20) = 抽象类, 细则 = 具体实现".

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
| R10 | Every `docs/*.md` must end with a `Last P20-verified: YYYY-MM-DD` line, updated whenever the doc passes `scripts/check_docs.py`. | Stale doc — the L0/L1/L2 contract was true on date X but may have rotted. |
| R11 | Any newly-added `docs/*.md` file must pass `scripts/check_docs.py` BEFORE commit.  The commit message must include the verify output (e.g. "P20 verify: 12/12 PASS"). | New doc slipped in without verify, rotting the layer contract. |
| R12 | When `PRINCIPLES.md` is modified, every child project's `docs/PHILOSOPHY.md` (if it exists) must be re-synced in the SAME commit.  Per P21. | Parent-child drift: parent adds P22, child doesn't know, child cites "P1-P21" forever. |

How to use this list:
1. Before any `docs/*.md` change, mentally check R1-R12.
2. Before commit, run `python scripts/check_docs.py` — it
   mechanically checks all 12.
3. If any rule fails, fix the doc; do not weaken the rule.

If a rule is too strict in practice (e.g. R5's 7KB threshold
turns out to be wrong for some doc type), the fix is to update
the rule AND the verify script — not to skip the rule.

### P21. Independent projects (cross-project boundaries)

When a project is referenced from another project's docs, the
referencing project should **link to a location, not duplicate
content**.  The referenced project should be **readable on its
own** (or have a single, clearly-stated "this is incomplete,
read the parent" disclaimer).

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