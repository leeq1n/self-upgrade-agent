---
description: "Working principles distilled from this project — portable across projects"
status: "summary"
---

# PRINCIPLES — Working principles (portable)

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
- Done tasks: [../../DONE.md](../../DONE.md)