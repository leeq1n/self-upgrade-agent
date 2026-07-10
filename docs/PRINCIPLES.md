---
description: "Working principles distilled from this project — portable across projects"
status: "summary"
---

# PRINCIPLES — Working principles (portable)
L0: The 23 working principles (P1-P23) of this project; P1-P21 in PRINCIPLES_DETAIL.md, P20+P21 + meta-rule pointers (P22, P23) here.
Last P20-verified: 2026-07-10

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
| R7 | Principles (P-n) are defined in EITHER `PRINCIPLES.md` (summary, brief) OR `PRINCIPLES_DETAIL.md` (full text), per the P11 split in commit `f753ec3`.  Any other `docs/*.md` may REFERENCE a P-n but must NOT redefine it.  Redefinition is a hard violation.  **Exception**: meta-rules (P22, P23) live in `_DETAIL.md` because their full text is in the same file as the P-n list. | Drift: parent says P7 is X, child says P7 is Y — system collapses. |
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

**P22 + P23 (meta-rules)** are listed in the L0 axiom table above
and the L1 children column.  See `PRINCIPLES_DETAIL.md` for full
text.  R12 in P20.细则 governs child-project sync.

## L2: 实操 (per P-n)

Each P-n has a 1-line "实操" describing how to actually follow the
principle.  See [PRINCIPLES_DETAIL.md](PRINCIPLES_DETAIL.md) for the
full list.  L2 is the third layer of progressive disclosure
(L0 = root axioms, L1 = principles, L2 = how to follow).

- Done tasks: [../../DONE.md](../../DONE.md)
