L0: Literature summary — 11 papers distilled to 1-line lessons each.
Last P20-verified: 2026-07-10

---
description: "Papers we've read + how they inform v2.x / v3.x design"
status: "summary"
---

# LITERATURE — brief

Papers read so far and how they constrain our design.  Each entry
includes TL;DR, what we use / don't use, and link to the long
form in `LITERATURE_DETAIL.md`.

| Paper | TL;DR | Use / Don't use |
| --- | --- | --- |
| **Reflexion** (Shinn 2023 NeurIPS) | Verbal self-reflection + episodic memory | DON'T (code refactor ≠ Leetcode; memory writes shouldn't mutate pipeline state) |
| **Self-Refine** (Madaan 2023 NeurIPS) | Generate → feedback → refine | DON'T for code gen (see "One Step Forward") |
| **One Step Forward, Two Steps Back** | Self-Refine regresses in code gen | DON'T trust self-refine loops for code |
| **Constitutional AI** (Anthropic 2022) | Principles-based training | DON'T (training-time not inference-time) |
| **Self-Harness** (2026) | Minimal harness iterative | USE: aligns with our v2 minimal agent |
| **Harness Engineering** (Lilian Weng 2026-07-04) | Harness > model for capability | USE: design and verify the harness rigorously |
| **Multi-Agent Failure** (UC Berkeley 2026) | 79% of multi-agent runs fail | DON'T multi-agent; single-agent + clear boundary |
| **HyperAgents** (Meta 2026) | Self-improvement cross-domain transfer | RESEARCH: inspiration for v3.x transfer |
| **The Agent Improvement Loop** (Substack 2026) | Production failure → regression test | **TOP PRIORITY** for next iteration |
| **SkillOpt** (Microsoft 2026) | Skills as trainable external state | FUTURE: explore in v3.x |
| **Factory Droid (signal-to-fix)** (2026) | Self-improvement in production | USE: telemetry → fix pattern |
| **Self-Evolving Agents Survey** (Gao 2025) | First systematic survey of self-evolving agents | USE: taxonomy + 你 idea (Recursive Self-Improvement section) |
| **Polaris: Gödel Agent Framework** (Kakade 2026) | Recursive self-improvement 4-step cycle | USE: 1:1 mapping to 你 idea (拆解+类比+自指) |
| **Geometric Dynamics of Agentic Loops** (Tacheny 2026) | Loops have predictable dynamics | RESEARCH: stability analysis for self-improve loop |
| **Agentic LLMs Survey** (Plaat 2025, JAI Research) | Reflection = transition to active agent | CONTEXT: field-level positioning |

For the long form (full TL;DR, key quotes, applicability analysis), see
[`LITERATURE_DETAIL.md`](LITERATURE_DETAIL.md).

## Key takeaways (3 bullet)

1. **Harness > model**: spend effort on the harness, not the prompt
   (Lilian Weng; also empirically observed in our session)
2. **Decision must be HARD RULE** (test pass/fail), not LLM-judged
   (avoids coherence trap; aligns with most production patterns)
3. **Failure → regression test**: every failure becomes a test, so the
   same failure never returns (Substack / HyperAgents / Factory Droid)

## References

- INDEX: [INDEX.md](INDEX.md)
- Project state: [PROJECT_STATE.md](PROJECT_STATE.md)
- Constraints: [CONSTRAINTS.md](CONSTRAINTS.md)
- Model strategy: [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- User intent: [USER_INSIGHTS.md](USER_INSIGHTS.md)
- Pending tasks: [../../TODO.md](../../TODO.md)
- Done tasks: [../../DONE.md](../../DONE.md)
- Full paper notes: [LITERATURE_DETAIL.md](LITERATURE_DETAIL.md)