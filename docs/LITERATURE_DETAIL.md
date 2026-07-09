---
description: "Full notes on each paper we've read (long form)"
status: "reference"
---

# LITERATURE_DETAIL — paper notes

> Read [LITERATURE.md](LITERATURE.md) first for the table summary.
> This file expands each paper with full TL;DR, key quotes, and
> how it constrains our v2.x / v3.x design.

Each entry: TL;DR → Why we use / don't → Key evidence / quote.

---

## Reflexion — Shinn et al. 2023 (NeurIPS)

**TL;DR**: Agents reflect verbally on failure and store reflections
in episodic memory; future attempts reference the memory.

**Why we DON'T use it directly**: Our memory writes must NOT mutate
pipeline state.  Reflexion's pattern of "memory affects future
behavior" creates exactly the bug we hit in v1.8.x
(`state["scored_papers"] = []` after memory write silently broke
the pipeline).  See [PROJECT_STATE_DETAIL §Mistakes](PROJECT_STATE_DETAIL.md#mistakes-made-do-not-repeat) entry #4.

**Use it for**: inspiration on "remember what went wrong" —
but only as read-only feedback, never auto-applied.

---

## Self-Refine — Madaan et al. 2023 (NeurIPS)

**TL;DR**: Generate → feedback → refine, ~20% improvement on
some tasks.

**Why we DON'T use it**: Empirically regresses in code generation
(see "One Step Forward, Two Steps Back" below).  For our use case
(generating `def plan_task` for `core/planner.py`), an ungrounded
refine step risks "fixing" something that wasn't broken.

**Use it for**: inspiration on the prompt-critique structure, but
**always** behind a HARD-RULE gate (tests pass).

---

## One Step Forward, Two Steps Back (Gema et al. 2024)

**TL;DR**: Empirical study of Self-Refine in code generation;
finds it frequently regresses, especially for bugs that span
multiple functions.

**Why this is decisive**: If Self-Refine can corrupt working code,
we MUST NOT use it for self-improvement without an objective gate.
This justifies our hard decision (test pass/fail) in v2_round.

**Use it for**: The justification text in commit messages when
explaining why we don't have a self-refine loop.

---

## Constitutional AI — Anthropic 2022

**TL;DR**: Principles-based self-critique; the model rewrites
its own output to comply with a set of principles.

**Why we DON'T use it (inference-time)**: Constitutional AI is
training-time, not inference-time.  Applying principles as
prompt-time rules does not have the same effect as training-time
constitutional shaping.  We tried prompt-time variants in v1.8.x
and they were not effective.

**Use it for**: Nothing currently.  Mention as "considered and
rejected" in commit messages to prevent re-tries.

---

## Self-Harness (2026)

**TL;DR**: Minimal harness iterative, Terminal-Bench accuracy
40 → 62%.  Lesson: better harness + better prompt iteration
beats bigger model.

**Why we USE it**: Our v2 minimal agent (1 LLM call + 1 harness
test, no LangGraph, no multi-agent) is a direct application of
this lesson.

**Use it for**: Justifying the architecture choice in commit
messages; future iterations can iterate the harness without
changing the LLM call.

---

## Harness Engineering — Lilian Weng 2026-07-04

**TL;DR**: Harness (the system around the model) is now as
important as the model.  Spend engineering effort on the harness,
not on prompt engineering alone.

**Why we USE it**: Direct fit.  Our v2_round `run_project_tests`
is a real harness with a hard pass/fail criterion.  Spending
more time on it (failure → regression test pipeline) is
Lilian-Weng-aligned.

**Use it for**: Guiding our effort allocation.  Top priority for
v2.3: improve the harness (failure → regression test pipeline).

---

## Multi-Agent Failure (UC Berkeley 2026)

**TL;DR**: 79% of multi-agent runs fail, mostly due to spec
ambiguity and coordination overhead.

**Why we DON'T use multi-agent**: This is decisive evidence
against the "let agents collaborate" pattern.  We use single-agent
with clear interfaces.

**Use it for**: Justifying single-agent architecture choice;
rejecting LangGraph multi-node topologies.

---

## HyperAgents (Meta 2026)

**TL;DR**: Self-improvement strategies learned in robotics transfer
to novel domains like Olympiad math grading (imp@50 = 0.630).

**Why we DON'T use directly**: Their transfer-learning approach
requires training infrastructure we don't have.  We are
inference-only.

**Use it for**: Inspiration that cross-domain transfer is
possible in principle.  Future: maybe our RAG-based memory can
simulate lightweight transfer by retrieving successful patterns
from prior rounds.

---

## The Agent Improvement Loop — Substack 2026

**TL;DR**: "Reliable agent systems are not built by finding fewer
failures.  They are built by ensuring the same failure never
reaches production twice."  Every production failure becomes a
permanent regression test.

**Why this is TOP PRIORITY**: Our v2_round has a structured
`decision` field with KEPT / REVERTED / NO_PATCH / APPLY_FAILED.
We just need to persist these and turn them into test cases.

**Use it for**: Driving v2.3 design — failure → regression test
pipeline.  See [TODO.md top item](../../TODO.md).

---

## SkillOpt — Microsoft 2026

**TL;DR**: Skills are trainable external state.  +20 point accuracy
on multimodal tasks.  Skills transfer across model families
without retraining.

**Why we DON'T use directly (yet)**: Skills are essentially
structured prompt fragments.  We have `upgrades/learning.db`
which is similar but not yet treated as optimizable external
state.

**Use it for**: Future v3.x — treat `upgrades/` as skills and
iterate on them.  When/if we get a model-eval harness.

---

## Factory Droid — Signal-to-Fix Loop (2026)

**TL;DR**: Production telemetry → fix → regression test → merge.
Daily iteration in production.  Signal-to-fix is the canonical
production self-improvement pattern.

**Why we USE it**: This is exactly the pattern our v2_round is
aiming at, except we're in development rather than production.
Our RoundResult already has the right shape; we need to log it.

**Use it for**: Future v2.3 — persist RoundResults to a database
for analysis; future v3.x — telemetry → fix automation.

---

## Index of papers by applicability

**Top-applicable to our project**:
1. The Agent Improvement Loop (Substack)
2. Self-Harness
3. Harness Engineering (Lilian Weng)
4. Factory Droid signal-to-fix

**Confirmed don't-use**:
1. Reflexion (memory-mutation anti-pattern)
2. Self-Refine (code gen regression)
3. Multi-Agent (79% failure rate)
4. Constitutional AI (training-time only)

**Inspirational / future**:
1. HyperAgents (cross-domain transfer, training-only)
2. SkillOpt (skills as optimizable external state)

---

## What this list does NOT cover

We have NOT yet read:
- Multi-agent verification / consensus patterns (where it works)
- Memory-augmented transformers with explicit recurrence
- Bootstrap / Gödel-agent literature
- Recent model-context-protocol (MCP) design papers

When you read these, add them here with the same TL;DR +
applicability analysis.  Don't design without them.