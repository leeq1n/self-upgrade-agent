L0: Per-paper notes — abstract, key claims, our takeaway, citations.
Last P20-verified: 2026-07-13

---
description: "Full notes on each paper we've read (long form)"
status: "reference"
---

# LITERATURE_DETAIL — paper notes
> L0: Full text of past research citations.  Companion to LITERATURE.md.  Load when: need full citation.

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
pipeline.  See [TODO.md top item](../TODO.md).

---

## SkillOpt — Microsoft 2026 {#skillopt-paper}

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



---

## Pattern: prompt-as-interface (project rule, not a paper)

Per user feedback 2026-07-08 ("启动 prompt 越少越好, 实体承担重要作用"):

- Static prompts (system + the always-on user message) live in
  `src/prompts.py` as named constants.
- Each prompt is < 500 tokens.
- Harness-implementation details belong to the entity (e.g.
  v2_agent._PRELUDE for typing imports), NOT the prompt.
- The entity consumes the prompt by role name, so a new role
  is "add a constant + reference" — same as adding a virtual
  method to an abstract base.

This is the OOP "abstract method" pattern applied to LLM prompts.

Why it matters:
- Prompt changes are 1 file, reviewable
- Entity behavior (typing injection, sandbox setup, etc.)
  doesn't depend on LLM cooperation
- Test coverage on entity is independent of LLM

## What this list does NOT cover

We have NOT yet read:
- Multi-agent verification / consensus patterns (where it works)
- Memory-augmented transformers with explicit recurrence
- Bootstrap / Gödel-agent literature
- Recent model-context-protocol (MCP) design papers

When you read these, add them here with the same TL;DR +
applicability analysis.  Don't design without them.


## SkillOpt paper (skill lifecycle)

When the LLM agent makes enough successful patches (auto-commit
KEPT, tests pass), the patches become **reusable skills**.  SkillOpt
paper proposes:
- candidate → active → archived lifecycle
- promote on: applied_count ≥ threshold AND success_rate ≥ 0.6
- archive on: success_rate < 0.3 over last N applies

In our context (commit 747d96e / 96ae18e):
- Each auto-commit writes `upgrades/auto-patches/<date>-<hash>.meta.json`
- Meta contains: `commit_hash, target_module, paper_id, tests_passed,
  bundle_path, timestamp, status, applied_count, success_count`
- Lifecycle state machine lives in `docs/SKILLS.md`
- Future: `promote_skill()` scans candidates, applies promotion rules

Per P23 (doc > script): skill framework exists as doc-first
specification.  Implementation is per-skill metadata initially,
full lifecycle in v3.2.0.

See:
- [docs/SKILLS.md](SKILLS.md) — L0 + L1 framework
- [src/v3_auto_commit.py `write_skill_meta`](../src/v3_auto_commit.py) — implementation
- [tests/test_v2_cli.py `TestV3AutoCommitSkillMeta`](../tests/test_v2_cli.py) — regression tests


## Self-Evolving Agents Survey — Gao et al. 2025 (arXiv)

**TL;DR**: First systematic survey of self-evolving agents, organized
around "what, when, how, where to evolve" dimensions. Covers
mechanisms (model/memory/tools/architecture), stages (intra/inter
test-time), and design (rewards, feedback, multi-agent).

**Why we use it**: Provides the field-level taxonomy for 你 idea
("loop = decomposition + analogy + self-reference"). Sub-section
"Recursive Self-Improvement" cites Qu et al. 2024 and frames the
problem exactly as 你 did (agent improves own improvement logic).

**Key evidence**: "agents become increasingly skilled at
self-diagnosis and self-correction" (per recursive self-improvement
section). 

**Use for**: framework for our RECURSIVE_QUALITY.md design —
especially sub-task 4 (self-reference step on improvement logic itself).

---

## Polaris: Gödel Agent Framework — Kakade et al. 2026 (arXiv, May)

**TL;DR**: Gödel agent (self-referential) that performs policy repair
via experience abstraction. 4-step cycle: analysis → strategy
formation → abstraction → minimal code patch repair.

**Why we use it**: **1:1 mapping to 你 idea**:
1. Decomposition (你的 "拆分"): analysis step
2. Analogy (你的 "类比"): strategy formation (uses past patterns)
3. Self-reference (你的 "自指"): abstraction = distills failures
   into reusable strategies

**Key evidence**: "7B model equipped with Polaris achieves
consistent gains over baseline" on 4 benchmarks (MGSM, DROP, GPQA,
LitBench). Empirically validates recursive self-improvement at
small scale.

**Use for**: design pattern for our sub-task 1 (reflection step
follows the same 4-step structure).

---

## Geometric Dynamics of Agentic Loops — Tacheny 2026 (arXiv, Jan)

**TL;DR**: Agentic loops have predictable dynamics — contractive
(converge to attractor), oscillatory (cycle), exploratory (diverge).
Prompt design controls which regime.

**Why we use it**: Stability analysis for our self-improve loop.
Currently broken (0/10 KEPT) — possibly in exploratory regime.
Need to design prompt for contractive regime.

**Key evidence**: "iterative LLM dynamics are predictable and
controllable" — same model, different prompts → different regimes.

**Use for**: will inform future debugging when self-evolve loop
fails repeatedly (need to check if in contractive or exploratory
regime).

---

## Agentic LLMs Survey — Plaat et al. 2025 (JAI Research)

**TL;DR**: Taxonomy of agentic LLMs around 3 axes: reason, act,
interact. Reflection = reason axis.

**Why we use it**: Field-level context. Reflection is a "transition
from passive model to active agent" — aligns with 你 vision of
真 agent product.

**Key evidence**: "external algorithm uses the LLM to assess its
own predictions, creates a new prompt" — matches our plan for
sub-task 1 (reflection step).

**Use for**: position our project in current literature landscape.
