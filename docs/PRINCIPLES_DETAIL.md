L0: Per-P-n 实操 (L2 details) — how to actually follow each principle.  Main file is PRINCIPLES.md (L0+L1).
Last P20-verified: 2026-07-10

# PRINCIPLES_DETAIL — per-P-n 实操 (L2)

This file holds the L2 实操 details for each P-n principle.  The main
`docs/PRINCIPLES.md` holds L0 (4 root axioms) + L1 (the 23 principles).
Read main first; read this when you need to know "how to actually
follow" a specific principle.

Per P20 progressive disclosure: L1 in main, L2 in this detail file.
Per P11 摘要+引用: main = summary, detail = reference.

---

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

**Auto-commit boundary (per user 2026-07-10)**: test pass ≠
acceptable if production breaks.  When auto-committing patches,
callers of the modified module must still resolve.  Per
OBSERVATIONS.md 2026-07-10 entry: LLM rename of plan_task
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

