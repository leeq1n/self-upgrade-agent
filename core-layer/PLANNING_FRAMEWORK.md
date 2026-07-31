# Planning Capability Framework — 2026-07-30

> **Trigger**: User 2026-07-30 priority order:
> "首先把规划能力（思考能力的一部分）确定好没问题，然后是验收能力的修复，最后是具体任务".
>
> **Layer**: This doc lives in **核心层 (core layer)** per user intent
> "希望你底层自带" planning capability. Requires explicit user
> authorization per M-n 15 multi-session rule.
>
> **Purpose**: Codify HOW to plan before doing, so planning is
> structured rather than reactive.

## 1. Planning capability = thinking capability

Per user: "规划能力 (思考能力的一部分)". This means:

```
思考能力
├── 规划能力 (planning)
├── 验收能力 (verification)
└── 执行能力 (execution)
```

All three are layers of "thinking capability" but separable.

## 2. What "planning capability" means for an LLM agent

Per 真搜 (web_search "LLM agent planning"):

- **Andrew Ng**: Planning = LLM autonomously decides what steps to take
- **Pre-Act**: Multi-step planning BEFORE acting
- **Chain-of-Thought**: Plan out reasoning path before answering
- **Natural Plan benchmark**: LLM planning < 50% accuracy on real tasks

This means LLM agents (including me) are **systemically weak at planning**.
Mitigation = structured framework that forces planning steps.

## 3. The 4-phase framework (per ATDD)

```
Phase 1: ACCEPTANCE (define what success looks like)
   │
Phase 2: PLAN (design how to achieve it)
   │
Phase 3: SHIP (implement)
   │
Phase 4: VERIFY (compare actual vs acceptance)
   │
   └─→ back to Phase 1 if new acceptance criteria emerge
```

**Key principle**: Each phase produces a *single* artifact:
- Phase 1 → Acceptance criteria doc (acceptance/ACCEPTANCE_CRITERIA.md)
- Phase 2 → Plan doc (PLANS/PLAN_<DATE>.md)
- Phase 3 → Code/commits
- Phase 4 → Verification report

## 4. Planning template (per this framework)

Every PLAN_<DATE>.md MUST include these sections:

```markdown
# PLAN_<DATE>: <Title>

## 1. Goal
- What are we trying to achieve?
- Why does it matter?
- How will we know it's done?

## 2. Acceptance criteria
- Specific, testable, measurable
- Each criterion has a verification command
- Cannot change after Phase 2 (only with explicit re-plan)

## 3. Approach
- High-level strategy
- Alternative approaches considered + rejected (with reasons)

## 4. Trade-offs (per P-7 Occam)
- Pros of chosen approach
- Cons of chosen approach
- Why chosen approach is best
- Pre-judgment: 好 vs 坏 per aspect

## 5. Risks
- What could go wrong
- How to mitigate
- When to abort and replan

## 6. Tasks (subdivide for clarity)
- Task 1: ...
- Task 2: ...
- Each task has acceptance + verification

## 7. References
- ATDD, 3 Amigos, etc.
- tua-start protocols (P/M/R)
- Existing project docs
```

## 5. Planning anti-patterns (what NOT to do)

Per 真凭据 + 用户 catch:

| Anti-pattern | Example | Why bad |
|---|---|---|
| Ship-first | Write code, then plan | Modifications may be redundant |
| Plan-only | Plan without verify | Plan may not be implementable |
| Re-plan mid-ship | Change acceptance after ship | Wastes prior work |
| Skip pre-judgment | Ship without good/bad analysis | Misses trade-offs |
| Skip risk assessment | No abort criteria | Hard to backtrack |
| No references | Plan without grounding | Plagiarizes existing patterns |

## 6. Layer mapping (per user 哪层 question)

| Capability | Layer | File location | Why |
|---|---|---|---|
| **Planning framework** | **核心层** (this doc) | `core-layer/PLANNING_FRAMEWORK.md` | "底层自带" per user |
| Planning instances (per-task) | 项目层 | `docs/PLANS/PLAN_<DATE>.md` | Per-task plans |
| Planning runtime (per-turn) | 用户层 | in-memory + per-turn context | Ephemeral |
| Acceptance framework | 项目层 | `docs/ACCEPTANCE_PROTOCOL.md` | Per-project protocol |
| Acceptance scripts | 核心层 | `.hermes/scripts/*.py` | Enforced audit |
| Acceptance reports (per-state) | 用户层 | `~/.config/sua/acceptance/` | Per-state ephemeral |
| Specific tasks | 项目层 + 用户层 | Various | Not core |

## 7. How to use this framework (concretely)

When user gives a task:
1. **Phase 1**: Read task + extract acceptance criteria (ask user if unclear)
2. **Phase 2**: Write PLAN_<DATE>.md per template (§4)
3. **Get user OK** on plan (per "做好规划再行动")
4. **Phase 3**: Execute per plan, commit incrementally
5. **Phase 4**: Verify against acceptance criteria
6. **Update PLAN_<DATE>.md** with actual vs plan + lessons

## 8. Self-application (this framework applies to itself)

When updating this framework:
- Phase 1: Acceptance = "user can plan effectively per this framework"
- Phase 2: Plan = what changes to make
- Phase 3: Ship per plan
- Phase 4: Verify against acceptance

## 9. References

- ATDD (Acceptance Test-Driven Development) — Wikipedia + PMI
- 3 Amigos Sessions — joint criteria definition
- Andrew Ng on Planning — LLM agent design patterns
- Pre-Act: Multi-Step Planning and Reasoning (Tao An 2025)
- Natural Plan benchmark (Google DeepMind 2024)
- Chain-of-Thought (Wei et al. 2022)
- LangChain Planning for Agents
- tua-start AGENTS.md "Iterative thinking" protocol
- tua-start AGENTS.md "主动修改 skill" 3-layer policy
- M-n 15 multi-session rule (core-layer modification gate)
- M-n 32 Guardrail #1 (real verify before claim)
- P-7 Occam (smallest effective change)
- P-14 self-contained mandate (no internal refs)
- P-17 no fabricate (honest value assessment)