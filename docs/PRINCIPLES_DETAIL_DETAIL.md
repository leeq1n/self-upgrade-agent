# PRINCIPLES_DETAIL — Detail (L2)

Last P20-verified: 2026-07-14 (split from summary per R5+R6)



> L0: L2 detail for PRINCIPLES_DETAIL.md.  Per P11 摘要+引用,

> the summary file is the L0/L1 layer (≤ 7KB); this file is

> the L2 layer (per-P-n full text).  Per R6, this detail

> file is referenced from the summary.



This file holds the per-P-n full text (P1-P18 + P22, P23,

excluding meta-rules P19, P20, P21, P24, P25, P26 which

live in PRINCIPLES.md per R7).  See `PRINCIPLES_DETAIL.md`

for the summary.



---



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



**L2 detail (per user 2026-07-13 'search-the-search' meta-ask)**:



When to trigger a search (the agent should auto-search, not wait

for user to say "search"):



1. **User asks "how does X work?" or "what is Y?"** — search first,

   then answer.  Per LITERATURE Seed: "don't optimize the proxy,

   optimize the thing" → search the *real* answer, not your prior.

2. **Designing a new feature** — read 5+ sources on the design

   space before settling on an approach.  Per LITERATURE SkillOpt

   (2026-03): "the design space matters more than the choice".

3. **User explicitly says "搜资料" / "look it up"** — search

   immediately.  The user has authorized the search.

4. **User asks a meta-question about search itself** (e.g. "when

   to trigger search?", "how do we search?") — search the

   *meta-question* (e.g. agent self-search patterns, Moltbook

   2026 on hard vs soft constraints), then update this spec.

   This is the **search-the-search** pattern: when asked about

   search, agent searches the meta and updates this very doc.



Where to search (per user query type):



- **Academic / scientific** → `mcp__sciverse__semantic_search`

  (citation-grade academic retrieval, fulltext snippets).

- **General / latest** → `web_search` (broad, less rigorous).

- **Local project context** → `search_files` (ripgrep inside repo)

  or `mcp__llm_wiki__*` (knowledge graph across projects).

- **Papers** → `mcp__zotero__*` (user's curated library).

- **ArXiv preprints** → `mcp__arxiv__*` or web arxiv search.

- **Doc extraction** → `web_extract` (URL → markdown).



How to search (pattern):



1. Read `LITERATURE.md` first (local prior art — fastest, no cost).

2. If not found, `web_search` for breadth or `sciverse` for depth.

3. Add 1-line summary to `LITERATURE.md` for future reuse.

4. Cite the source in commit message.



**Search results → spec update (per user 2026-07-13)**:



When search reveals project-relevant new info, agent should NOT

just consume the result — agent should also check whether the

project's docs should be updated based on what was found.  E.g.:



- Search reveals a new framework (e.g. "agents.md spec") → check

  if `AGENTS.md` should reference it; if so, update.

- Search reveals an obsolete pattern (e.g. "P5 should include

  ad-hoc verify") → check if `PRINCIPLES.md` P5 reflects this.

- Search reveals project-relevant new tool (e.g. "sciverse for

  academic search") → check if `AGENTS.md` "Read first" lists it.



This is the **search-then-update** contract: every search should

leave the project docs slightly more current than before.  Per

P14 (docs stay current) — search is one of the discovery

mechanisms that triggers doc updates.





### P3. Test pyramid — unit + joint + integration + chain test (per c47 MERGE_EVAL + commit 78)

P24 ("Sequential chain test") was merged into P3 per

P7 奥卡姆 (P24 was a specific case of P3 — chain test

arrangement for sequential functions).  After merge:

P-n count reduces 26 → 25 (per c47 plan).



Tests form a pyramid:

- **Unit**: one mechanism in isolation (atomic, fast)

- **Joint**: multiple modules together (the contract)

- **Integration**: real run with real inputs (the truth)

- **Chain**: sequential functions tested by passing

  intermediate state through the chain (per P19, P24

  merged in here)



Skip integration = "passing tests but broken in production".



**实操 (L2)**: per new feature, write unit (fast) + joint (mock)

+ integration (real LLM if applicable) + chain test (if

sequential function chain per P19) tests before commit.

Per Test root.  (合并前 P3 实操 + P24 实操).





### P4. 1 commit = 1 logical feature

Multi-file is fine if they form one feature.  Atomic-per-file is

not the goal.  The goal is **per-feature commit** with **all

3 layers of testing green before commit**.



**实操 (L2)**: commit message starts with `feat:` / `fix:` /

`docs:` / `chore:` + 1-line WHY.  Per Workflow root.





### P5. Verify before commit (per c47 MERGE_EVAL + commit 77, + commit 79, + commit 80)

P6 ("真跑再 commit"), P15 ("stage gate + cleanup"), and P16

("ad-hoc verify, then commit") were merged into P5 per

P7 奥卡姆:

- P6 = specific case of P5 [verify before commit]

- P15 = stage-boundary variant of P5 [verify at stage

  boundary instead of per-commit]

- P16 = ad-hoc variant of P5 [verify via temp script when

  full suite is uncertain]

After these merges: P-n count reduces 27 → 25 → 24 → 23

(per c47 plan, 4 candidates: P5+P6 done in c77, P3+P24

done in c78, P15 done in c79, P16 done in c80).



"测通" = unit + joint + integration + **real-world run**

+ **stage gate** + **ad-hoc verify** + **cleanup**.  Not

"I ran a test".  Especially: integration tests catch bugs

the unit tests can't (no mocking, real env); real-world run

catches bugs integration tests can't (real inputs, real

env, user-meaningful); stage gate catches per-stage boundary

issues; ad-hoc verify (small temp script when uncertain) is

a fallback when full suite is impractical; cleanup prevents

working-tree rot.



**实操 (L2)**: before `git commit`, run full suite (with

`SUA_FAST=1`) + 1 integration smoke + 1 real-world run

(if user gave a real cmd).  Per major stage, also run

4-item stage gate (tests, docs, working tree, no tempfiles).

When correctness is uncertain, write minimal

`sua-verify-*.py` in Temp, run, summarize, then commit

(clean up after).  Per Test + Doc roots.  (合并前 P5 实操

+ P6 实操 + P15 实操 + P16 实操).







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



**Auto-commit boundary (per user 2026-07-10)**: test pass ≠

acceptable if production breaks.  When auto-committing patches,

callers of the modified module must still resolve.  Per

broke 24 tests because production callers (core/agent.py,

core/__init__.py, src/patchgen.py) still referenced the old

name.  Auto-commit now runs caller validation before commit

(via src/v3_auto_commit.py check_callers).





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



**Boundary: auto vs manual (per user 2026-07-10)**:

KEPT patches come in two flavors:

- Manual commits (user runs `git commit`): the source of truth for

  human-curated changes

- Auto commits (daily-loop / improve with `--auto-commit`): KEPT

  patches committed by the agent itself, distinguishable by:

  - Author: `Auto Upgrade <auto@self-upgrade.local>` (never the user)

  - Prefix: `[auto]` in commit message

  - Bundle: also written to `upgrades/auto-patches/<date>-<hash>.patch`

    for human review, selective apply, or rejection

- `git log --author="Auto"` filters auto commits in 1 step

- Default behavior (no `--auto-commit`): KEPT files stay in working

  tree (or auto-revert per existing logic).  User stays in control.





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







---



**Note (per commit 42, 2026-07-14)**: P-n sections

reordered from insertion-order (P1-P6, then P22-P23,

then P7-P18) to numerical order (P1-P18, P22, P23).

This eliminates the entropy caused by mixed-order

listing (per user meta-rule 2026-07-14: "原则顺序

不是一成不变的。如果原则顺序会导致熵增，那应该

整理顺序，使项目整洁，这样能方便新agent的阅读").



P19 (data flow observability), P20 (progressive

disclosure), P20.细则 (R1-R12), P21 (independent

projects), P24 (sequential chain test), P25

(principle modification discipline), P26 (user-

acceptance fresh-agent check) are defined in

`docs/PRINCIPLES.md` per R7.  Cross-refs from this

file (where applicable) should be added in future

commits.

