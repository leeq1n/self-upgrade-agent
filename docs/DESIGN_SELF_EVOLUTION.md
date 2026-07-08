# v1.8.4 Design: Self-Evolution via Reflexion + Constitutional AI

**Status**: design draft (v1.8.4 branch, NOT implemented yet)

**Why this rewrite**: I (the agent) had 30+ fix-commit pile-up,
all "hardcode rules" approach.  This is anti-agent.  This doc
redesigns the system around three real patterns from literature:

  1. **Reflexion** (Shinn et al., NeurIPS 2023)
     - Actor + self-reflection model + episodic memory buffer
     - On failure: reflect verbally → store → next trial better
     - https://arxiv.org/abs/2303.11366

  2. **Self-Refine** (Madaan et al., NeurIPS 2023)
     - generate → feedback → refine, single LLM all roles
     - ~20% improvement on 7 tasks
     - https://selfrefine.info

  3. **Constitutional AI** (Anthropic, 2022)
     - LLM critiques own output against natural-language principles
     - Scales beyond human-labeled feedback (RLHF)
     - https://www.anthropic.com/constitutional-ai

---

## §1. Why current design fails

**Current state** (v1.8.1, v1.8.2, v1.8.3):
  - 30+ commits, mostly hardcode fixes
  - `_REJECT_TITLE_PATTERNS` = 10 hardcoded substrings
  - `_REJECT_CATEGORY_PATTERNS` = 5 hardcoded substrings
  - `_paper_is_obviously_unrelated` = 8 hardcoded keywords
  - Pre-filter runs BEFORE LLM ever sees the paper

**User feedback (2026-07-08)**:
  > "如果写的论文相关,但摘要刚好没这些词,那就被过滤掉了"
  > "下次你写代码之前的思考里,可以考虑下这类边界条件"

**Failure mode**: A paper that's actually relevant but uses
non-standard terminology gets rejected at the gate.  Hardcode
rules = brittle.  This is the **opposite** of an agent — an agent
should be flexible, not rule-bound.

---

## §2. Three patterns, mapped to our pipeline

### §2.1 Constitutional AI → replaces hardcode rules

**Old** (hardcode):
```python
_REJECT_TITLE_PATTERNS = [
    "song generation", "music generation", ...
]
_REJECT_CATEGORY_PATTERNS = ["q-bio", "stat.AP", ...]

def _paper_is_obviously_unrelated(paper):
    # check 13 patterns, return True if any matches
    ...
```

**New** (principles + LLM judge):
```python
CONSTITUTION = [
    "Reject only papers that are clearly outside LLM/agent scope "
    "(e.g. pure biology, classical music theory, image segmentation). "
    "Default-OPEN: when in doubt, let the LLM-as-judge decide.",

    "Prefer primary research over benchmarks. A benchmark paper "
    "may be referenced but not directly applicable to code changes.",

    "Prefer papers with concrete methods/algorithms over pure "
    "surveys or position papers.",
]

def relevance_judge(paper, constitution=CONSTITUTION):
    """LLM-as-judge using natural language constitution."""
    prompt = build_judge_prompt(paper, constitution)
    return chat_judge(prompt)  # returns True/False
```

**Why better**:
- Principles are **natural language** → auditable, easy to modify
- LLM judge uses **understanding**, not substring match
- Default-OPEN → "when in doubt, let it through"
- New edge cases handled by LLM (no code change)

### §2.2 Self-Refine → post-LLM guardrail loop

**Pipeline becomes**:
```
paper → relevance_judge() → LLM patchgen → patch
  ↓ (if harness fails)
  reflection_prompt = (
    f"Patch failed harness: {harness_output}. "
    f"Here is the patch: {patch}. "
    f"Here is the failure: {error}. "
    f"Self-critique: what went wrong? How to fix?"
  )
  reflection = llm(reflection_prompt)
  patch = patchgen(paper, ..., previous_reflection=reflection)
  ↓ (repeat up to N times)
  → final patch
```

**Why better**:
- Each iteration learns from specific failure
- LLM critiques own output against actual evidence (harness)
- Replaces the current `node_reflect` (which exists but is shallow)

### §2.3 Reflexion → persistent memory across rounds

**Old**: decisions logged to `decision_log` table, but never
read by future rounds.

**New**: each round's reflection stored in memory MCP server.
Next round's filter/evaluate gets:
  - Last 3 reflections (this paper, similar papers)
  - Last 3 successes (what worked)
  - Last 3 failures (what didn't)

```python
memory_search(
    query=f"reflection on {paper.arxiv_id} OR similar",
    kind_filter=["reflection", "outcome"],
    top_k=3,
)
```

**Why better**:
- Real learning across rounds (was zero learning)
- Replaces the decision_log-as-no-op pattern

---

## §3. Concrete changes (proposed)

### §3.1 Delete

- `src/patchgen.py:_REJECT_TITLE_PATTERNS` (10 patterns)
- `src/patchgen.py:_REJECT_CATEGORY_PATTERNS` (5 patterns)
- `src/patchgen.py:_paper_is_obviously_unrelated` (40 LOC of hardcode)

### §3.2 Add

- `src/constitution.py` (~30 LOC): natural-language principles
- `src/judges.py` (~100 LOC): LLM-as-judge functions
  - `relevance_judge(paper)` — uses constitution
  - `methodology_judge(paper)` — "does it have a method we can lift?"
- `src/reflection.py` (~80 LOC): self-critique loop
  - `critique(patch, harness_output)` — produce reflection
  - `refine_patch(paper, patch, reflection)` — re-patchgen
- `tests/test_judges.py`: harness test for judge correctness
- `tests/test_reflection.py`: harness test for refine loop

### §3.3 Modify

- `src/pipeline_lg.py`:
  - `node_filter`: replace hardcode pre-filter with `relevance_judge`
  - `node_generate_patch`: on harness fail, call `refine_patch`
  - `node_decide`: write reflection to memory (kind=reflection)
- `src/memory_server.py`: add `kind="reflection"` (already supported,
  just need to use it)

---

## §4. Anti-patterns to avoid

❌ Adding more hardcode rules (we just deleted them)
❌ Constitutional AI with 50+ principles (use 5-10 focused ones)
❌ Self-Refine without grounded feedback (harness output, not vibes)
❌ Reflexion without persistent memory (just session-level)
❌ LLM-as-judge without sanity test (could silently regress)

---

## §5. Self-critique log (commit 0)

What I (the agent) might over-engineer:
  - 50+ principles → resist, keep 5-10
  - Complex reflection chain → resist, single reflection per round
  - 5-stage pipeline → resist, augment current 8-node pipeline
  - Multi-agent debate → resist, single agent (we don't have multi)

What I might under-engineer:
  - Test coverage for judges → 5 tests minimum
  - Backward compat for hardcode pre-filter → remove cleanly
  - Memory write frequency → 1 reflection per round, not per paper

---

## §6. Migration plan

Phase 1 (one commit):
  - Add `src/constitution.py` + `src/judges.py` + tests
  - Pre-filter kept as a SECONDARY check, not primary gate

Phase 2 (one commit):
  - Add `src/reflection.py` + `node_reflect` augmented
  - Harness output → LLM critique → re-patchgen

Phase 3 (one commit):
  - `node_decide` writes reflection to memory
  - `node_filter` queries memory for past reflections

Phase 4 (one commit):
  - Delete hardcode pre-filter
  - `constitution` is the only gate

Each phase: hermes-verify, full test suite, no regression.

---

## §7. Success metric

**Constitutional AI** doesn't have a clear "convergence" metric.
We need one.  Proposal:

  - **Round N**: pipeline generates a patch
  - **Round N+1**: pipeline consults memory for "reflections on
    similar papers", uses them in the prompt
  - **Metric**: consecutive KEPT rounds (existing) +
    consecutive rounds where the LLM-judge approved a paper
    that the old hardcode would have rejected (regression test)

This is the real "self-evolution" the user asked for.

---

## §8. NOT in this design

- Full pipeline rewrite to StateGraph (separate work)
- Memory search embedding (numpy + cosine, already done)
- 5+ agent multi-agent (no need)
- Constitutional training (training-time, not inference-time)

---

## §9. References (read all before commit)

1. Shinn et al., "Reflexion: Language Agents with Verbal
   Reinforcement Learning", NeurIPS 2023.
   https://arxiv.org/abs/2303.11366

2. Madaan et al., "Self-Refine: Iterative Refinement with
   Self-Feedback", NeurIPS 2023.
   https://selfrefine.info

3. Bai et al., "Constitutional AI: Harmlessness from AI Feedback",
   Anthropic 2022.
   https://www.anthropic.com/constitutional-ai

4. arthur.ai "Best Practices for Building Agents: Guardrails"
   https://www.arthur.ai/blog/best-practices-for-building-agents-guardrails

5. Taskade "Self-Improving AI Agents: The Reflection Loop (2026)"
   https://www.taskade.com/blog/self-improving-ai-agents-reflection

Key insight from all: **grounded reflection (harness output,
test results, real evidence) > intrinsic self-critique (LLM vibes)**.
The "coherence trap" is the failure mode to avoid.
