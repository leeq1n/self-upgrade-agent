# INDEX — full navigation map (rewritten 2026-07-16)

> L0: Real navigation index for all 88 docs in /docs/.  Per
> user message audit Phase 1-3 (2026-07-16) — AGENTS.md L0 surface
> only listed 8 docs; fresh agents could not find 79 others.
>
> How to use: browse the table below by domain, OR jump
> to L0 (entry doc) / L1 (architecture) / L2 (detail)
> reading order per your task.
>
> Each entry: doc (summary) + companion (DETAIL) + TL;DR.
> Read summary first; click through to detail only as needed.

## Reading order for a fresh agent (8 steps, ~35 min total)

1. **AGENTS.md** — 2 min (operating rules, L0 entry)
2. **PROJECT_STATE.md** — 5 min (current goal + next step)
3. **CONSTRAINTS.md** — 5 min (invariants the system must preserve)
4. **USER_INSIGHTS.md** (skim, focus on items dated 2026-07-08+) — 10 min
5. **LITERATURE.md** — 5 min (papers read + design constraints)
6. **PRINCIPLES.md** — 3 min (general working principles)
7. **OPERATING_RULES.md** — 5 min (M-n 1-34, per AGENTS.md Read first item 7)
8. **../TODO.md** to see pending work — 2 min

Total: ~35 min to full orientation.

## L0: Entry / orientation docs (5)

| Doc | Companion | TL;DR |
|---|---|---|
| [AGENTS.md](../AGENTS.md) | (none) | Operating rules for AI agents in this repo |
| [INDEX.md](INDEX.md) | (this file) | Full navigation map |
| [PROJECT_STATE.md](PROJECT_STATE.md) | [PROJECT_STATE_DETAIL.md](PROJECT_STATE_DETAIL.md) | Goal + current state + next step (1-paragraph snapshot) |
| [USER_INSIGHTS.md](USER_INSIGHTS.md) | [USER_INSIGHTS_DETAIL.md](USER_INSIGHTS_DETAIL.md) | Paraphrased user rules + verbatim quotes |
| [HOW_TO_READ_GRAPH.md](HOW_TO_READ_GRAPH.md) | (within file) | Read pattern for new agents (L0 → L1 → L2 traversal rules) |

## L1: Architecture / principles / rules (10)

| Doc | Companion | TL;DR |
|---|---|---|
| [PRINCIPLES.md](PRINCIPLES.md) | [PRINCIPLES_DETAIL.md](PRINCIPLES_DETAIL.md) | Working principles (L0+L1), per-P-n 实操 (L2); PRINCIPLES_FULL.md (35KB) has full text |
| [OPERATING_RULES.md](OPERATING_RULES.md) | [OPERATING_RULES_DETAIL.md](OPERATING_RULES_DETAIL.md) | M-n 1-34 operating rules (107KB) — operational discipline |
| [PRINCIPLES_FULL.md](PRINCIPLES_FULL.md) | (within file) | Full text of all 25 working P-n + lift history |
| [CONSTRAINTS.md](CONSTRAINTS.md) | [CONSTRAINTS_DETAIL.md](CONSTRAINTS_DETAIL.md) | Invariants the system must preserve |
| [RECURSIVE_DECOMPOSITION.md](RECURSIVE_DECOMPOSITION.md) | (within file) | Top-down decomposition rules (per c47a) |
| [SWITCH_SIGNALS.md](SWITCH_SIGNALS.md) | (within file) | Switch signals + action protocol before user messages |
| [KNOWLEDGE_ORG.md](KNOWLEDGE_ORG.md) | [KNOWLEDGE_ORG_DETAIL.md](KNOWLEDGE_ORG_DETAIL.md) | Knowledge organization (taxonomy) |
| [EXTENSIONS.md](EXTENSIONS.md) | [EXTENSIONS_DETAIL.md](EXTENSIONS_DETAIL.md) | Extension rules (L0/L1/L2 + extensions per M-n 13) |
| [SKILLS.md](SKILLS.md) | (within file) | Skill lifecycle / SkillOpt paper mapping |
| [TODO_KNOWLEDGE_LIFECYCLE.md](TODO_KNOWLEDGE_LIFECYCLE.md) | (within file) | Knowledge lifecycle state machine |

## L1: Operational patterns (8)

| Doc | Companion | TL;DR |
|---|---|---|
| [COMMON_PITFALLS.md](COMMON_PITFALLS.md) | (within file) | Common pitfalls observed in project history |
| [MCP_TOOLS.md](MCP_TOOLS.md) | (within file) | MCP tool ecosystem + which tools to use when |
| [MEMORY_TOOLS.md](MEMORY_TOOLS.md) | (within file) | Memory system usage patterns |
| [MODEL_STRATEGY.md](MODEL_STRATEGY.md) | [MODEL_STRATEGY_DETAIL.md](MODEL_STRATEGY_DETAIL.md) | Which LLM, why, deployment notes |
| [LITERATURE.md](LITERATURE.md) | [LITERATURE_DETAIL.md](LITERATURE_DETAIL.md) | Papers read + how they constrain design |
| [HANDOFF.md](HANDOFF.md) | [HANDOFF_DETAIL.md](HANDOFF_DETAIL.md) | Project handoff template (per user message) |
| [AUDIT_PHASE_1_2_3_2026_07_16.md](AUDIT_PHASE_1_2_3_2026_07_16.md) | (within file) | Phase 1-3 audit (reachability, M-n coverage, doc gaps) — this session |
| [OBSERVATIONS.md](OBSERVATIONS.md) | [OBSERVATIONS_DETAIL.md](OBSERVATIONS_DETAIL.md) | Accumulated observations / behavioral patterns (73KB) |

## L2: M-n detail files (22 of 34, per `M_*_DETAIL.md` files)

> Per AGENTS.md "Operating rules (M-n 12-33)" — 22 M-n listed.
> M-n 1-11 not yet in AGENTS.md "Operating rules"段 (Phase 6 work).
> M-n 34 (M-pre-task-scan) added 2026-07-16 (this session).

| M-n | Doc | TL;DR |
|---|---|---|
| M-n 3 | [M_3W1H_THINK_FIRST_DETAIL.md](M_3W1H_THINK_FIRST_DETAIL.md) | 3W1H analysis before top-down |
| M-n 13 | [M_LAYER_EXTENSION.md](M_LAYER_EXTENSION.md) | L0/L1/L2 + extensions rules |
| M-n 14 | [M_TWO_TRACK_REASONING_DETAIL.md](M_TWO_TRACK_REASONING_DETAIL.md) | 类比+逻辑, 6-stage distribution |
| M-n 15 | [M_PRINCIPLE_REORDERING_DETAIL.md](M_PRINCIPLE_REORDERING_DETAIL.md) | 6-step after 原则 混乱 |
| M-n 16 | [M_OBSERVE_THINK_EXECUTE_DETAIL.md](M_OBSERVE_THINK_EXECUTE_DETAIL.md) | 6-stage + top-down 分治 |
| M-n 17 | [M_CONTEXT_FRESHNESS_CHECK_DETAIL.md](M_CONTEXT_FRESHNESS_CHECK_DETAIL.md) | Intra-agent + inter-domain freshness |
| M-n 18 | [M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md](M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md) | 6 sub-steps + 节点 生命周期 |
| M-n 19 | [M_FILE_NAMING_CONVENTION_DETAIL.md](M_FILE_NAMING_CONVENTION_DETAIL.md) | File naming conventions |
| M-n 20 | [M_AGENT_DISCOVERABILITY_CHECK_DETAIL.md](M_AGENT_DISCOVERABILITY_CHECK_DETAIL.md) | Cross-framework discoverability |
| M-n 21 | [M_ASK_OR_INFER_MARK_GUESS_DETAIL.md](M_ASK_OR_INFER_MARK_GUESS_DETAIL.md) | 3 sub-steps + top-down default |
| M-n 22 | [M_3W1H_THINK_FIRST_DETAIL.md](M_3W1H_THINK_FIRST_DETAIL.md) | (alias) |
| M-n 25 | [M_TURN_PATTERN_RECOGNITION_DETAIL.md](M_TURN_PATTERN_RECOGNITION_DETAIL.md) | Parse user message + 5 patterns + M-n self-application |
| M-n 26 | [M_CONTEXT_DECAY_MANAGEMENT_DETAIL.md](M_CONTEXT_DECAY_MANAGEMENT_DETAIL.md) | Detection + classification + compression |
| M-n 27 | [M_KNOWLEDGE_LAYER_ARCHITECTURE_DETAIL.md](M_KNOWLEDGE_LAYER_ARCHITECTURE_DETAIL.md) | 3-layer core/knowledge/project taxonomy |
| M-n 28 | [M_PLAN_CONDITIONAL_DETAIL.md](M_PLAN_CONDITIONAL_DETAIL.md) | 4-condition check (uncertain→plan, clear→continue) |
| M-n 29 | [M_ACCEPTANCE_PROTOCOL_DETAIL.md](M_ACCEPTANCE_PROTOCOL_DETAIL.md) | 5-step protocol + cold-start sim |
| M-n 30 | [M_KNOWLEDGE_CONTEXT_TRADE_OFF_DETAIL.md](M_KNOWLEDGE_CONTEXT_TRADE_OFF_DETAIL.md) | 4-priority: knowledge 充足 > ... |
| M-n 31 | [M_TASK_LIFECYCLE_DETAIL.md](M_TASK_LIFECYCLE_DETAIL.md) | 4-phase: init + execute + done-notify + retrospective |
| M-n 32 | [M_SELF_LEARNING_GUARDRAIL_DETAIL.md](M_SELF_LEARNING_GUARDRAIL_DETAIL.md) | 5 modification guardrails + auto-learning |
| M-n 33 | [M_NARRATIVE_AS_SPEC_DETAIL.md](M_NARRATIVE_AS_SPEC_DETAIL.md) | 3-primitive: parse + structure + codify |
| M-n 11 | [M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md](M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md) | Sub-project experimental pattern |
| M-n 12 | [M_TERMINOLOGY_CLARITY_DETAIL.md](M_TERMINOLOGY_CLARITY_DETAIL.md) | Terminology refinement rules |
| M-n 35 | [M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md](M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md) | 4 adversarial primitives (质疑/逆向/预演失败/对立论证) — added 2026-07-16 |

## L1: Process / lifecycle patterns (8)

| Doc | Companion | TL;DR |
|---|---|---|
| [SELF_AUDIT_P20.md](SELF_AUDIT_P20.md) | [SELF_AUDIT_P20_DETAIL.md](SELF_AUDIT_P20_DETAIL.md) | Self-audit protocol per P20 |
| [SELF_ORG.md](SELF_ORG.md) | (within file) | Self-organization patterns |
| [M_SELF_AUDIT.md](M_SELF_AUDIT.md) | (within file) | M-self-audit operational rules |
| [M_SELF_APPLICATION.md](M_SELF_APPLICATION.md) | (within file) | M-self-application patterns |
| [M_SKILL_SYNCHRONIZE.md](M_SKILL_SYNCHRONIZE.md) | (within file) | Skill synchronization |
| [M_LAYER_EXTENSION.md](M_LAYER_EXTENSION.md) | (within file) | Layer extension rules |
| [SKILL_GENERATION.md](SKILL_GENERATION.md) | (within file) | Skill generation guide |
| [RECURSIVE_QUALITY.md](RECURSIVE_QUALITY.md) | (within file) | Recursive quality loop (拆解+类比+自指) |

## L2: Project audit / decisions / plans (10)

| Doc | Companion | TL;DR |
|---|---|---|
| [MERGE_EVAL.md](MERGE_EVAL.md) | [MERGE_EVAL_DETAIL.md](MERGE_EVAL_DETAIL.md) | Merge evaluation framework |
| [PLAN_TOPDOWN_REORG.md](PLAN_TOPDOWN_REORG.md) | [PLAN_TOPDOWN_REORG_DETAIL.md](PLAN_TOPDOWN_REORG_DETAIL.md) | Top-down reorg plan |
| [PROJECT_TOPDOWN_AUDIT.md](PROJECT_TOPDOWN_AUDIT.md) | [PROJECT_TOPDOWN_AUDIT_DETAIL.md](PROJECT_TOPDOWN_AUDIT_DETAIL.md) | Project top-down audit |
| [ANALYSIS_PARENT_VERIFY.md](ANALYSIS_PARENT_VERIFY.md) | [ANALYSIS_PARENT_VERIFY_DETAIL.md](ANALYSIS_PARENT_VERIFY_DETAIL.md) | Parent verification analysis |
| [GRAPH_TO_SKILL_DESIGN.md](GRAPH_TO_SKILL_DESIGN.md) | [GRAPH_TO_SKILL_DESIGN_DETAIL.md](GRAPH_TO_SKILL_DESIGN_DETAIL.md) | Graph → skill design |
| [GRAPH_TO_SKILL_ANALYSIS.md](GRAPH_TO_SKILL_ANALYSIS.md) | [GRAPH_TO_SKILL_ANALYSIS_DETAIL.md](GRAPH_TO_SKILL_ANALYSIS_DETAIL.md) | Graph → skill analysis |
| [SUMMARY_LIFECYCLE.md](SUMMARY_LIFECYCLE.md) | (within file) | Summary lifecycle |
| [TODO_KNOWLEDGE_GRAPH.md](TODO_KNOWLEDGE_GRAPH.md) | (within file) | KG linker / cross-project todos |
| [TODO_SESSION_PERSISTENCE.md](TODO_SESSION_PERSISTENCE.md) | [TODO_SESSION_PERSISTENCE_DETAIL.md](TODO_SESSION_PERSISTENCE_DETAIL.md) | Session persistence pattern |
| [DECISIONS_2026_07_11_12.md](DECISIONS_2026_07_11_12.md) | (within file) | Decision log (2026-07-11/12) |

## L2: Operational rules (4)

| Doc | TL;DR |
|---|---|
| [ADD_THEN_REDUCE.md](ADD_THEN_REDUCE.md) | Add-then-reduce operational pattern |
| [REFLECTION_STEP_BACK.md](REFLECTION_STEP_BACK.md) | [REFLECTION_STEP_BACK_DETAIL.md](REFLECTION_STEP_BACK_DETAIL.md) — reflection + step-back |
| [_REGRESSION_NOTES.md](_REGRESSION_NOTES.md) | Regression notes (low-level) |
| [HANDOFF.md](HANDOFF.md) | (above) — already listed in L1 |

## Domain-specific / utility (12)

| Doc | TL;DR |
|---|---|
| [PRINCIPLES_DETAIL_DETAIL.md](PRINCIPLES_DETAIL_DETAIL.md) | Per-P-n detail (L2 deep) |
| [OBSERVATIONS_DETAIL.md](OBSERVATIONS_DETAIL.md) | Observations (L2 deep, 73KB) |
| [CONSTRAINTS_DETAIL.md](CONSTRAINTS_DETAIL.md) | Constraints (L2 deep) |
| [EXTENSIONS_DETAIL.md](EXTENSIONS_DETAIL.md) | Extensions (L2 deep) |
| [HANDOFF_DETAIL.md](HANDOFF_DETAIL.md) | Handoff (L2 deep) |
| [KNOWLEDGE_ORG_DETAIL.md](KNOWLEDGE_ORG_DETAIL.md) | Knowledge org (L2 deep) |
| [LITERATURE_DETAIL.md](LITERATURE_DETAIL.md) | Literature (L2 deep) |
| [MERGE_EVAL_DETAIL.md](MERGE_EVAL_DETAIL.md) | Merge eval (L2 deep) |
| [M_EXPERIMENT_IN_SUBPROJECT.md](M_EXPERIMENT_IN_SUBPROJECT.md) | Sub-project experiment |
| [M_TERMINOLOGY_CLARITY.md](M_TERMINOLOGY_CLARITY.md) | Terminology clarity (top-level) |
| [M_FILE_NAMING_CONVENTION_DETAIL.md](M_FILE_NAMING_CONVENTION_DETAIL.md) | (alias) |
| [PRINCIPLES_FULL.md](PRINCIPLES_FULL.md) | (above) — already in L1 |

## Conditional loads (stealth docs, per P20)

These don't have summaries — read only if relevant to your task:

- **trigger: cross-project work** → [EXTENSIONS.md](EXTENSIONS.md) + consider
  `../skill-incubator/`, `../agent-reflection-skill/`, `../knowledge-graph-seed/`
- **trigger: skill lifecycle planning** → [SKILLS.md](SKILLS.md) + SkillOpt paper
- **trigger: knowledge graph / Q&A** → `../knowledge-graph-seed/SEED.md` +
  [TODO_KNOWLEDGE_GRAPH.md](TODO_KNOWLEDGE_GRAPH.md) (linker)
- **trigger: 3-layer architecture** (per user message 2026-07-16) → see
  [AUDIT_PHASE_1_2_3_2026_07_16.md](AUDIT_PHASE_1_2_3_2026_07_16.md)
  + Plan: `hermes-plan-3-layer-architecture-2026-07-16.md`
  + SUA `[../core-layer/README.md](../core-layer/README.md)`
    (L0 marker, modified 2026-07-16 per commit `a447b0b`)
  + SUA `[../core-layer/governance-template.md](../core-layer/governance-template.md)`
    (L1: eval-before + verify-after gate template)
  + Phase 4 retrospective: `[../.hermes/notes/phase4_c1_failure.md](../.hermes/notes/phase4_c1_failure.md)`
    (e7c9072 → c681e0b revert + a447b0b redo)
- **trigger: cold-start simulation** → [M_PRE_TASK_SCAN_DETAIL.md](M_PRE_TASK_SCAN_DETAIL.md)
  + [M_ACCEPTANCE_PROTOCOL_DETAIL.md](M_ACCEPTANCE_PROTOCOL_DETAIL.md)

## How to update this index

When any file in /docs/ added/removed/renamed, update this index per
P14 (docs stay current).  Phase 1-3 audit (2026-07-16) flagged
that **AGENTS.md L0 surface** still only references 8 docs —
this INDEX.md expansion is the 2026-07-16 fix to close that gap.

## See also

- **AGENTS.md** (L0 entry doc) — list this INDEX.md in your cold-start
- **AUDIT_PHASE_1_2_3_2026_07_16.md** — Phase 1-3 audit findings
- **Plan**: `hermes-plan-3-layer-architecture-2026-07-16.md` —
  3-layer refactor plan (not yet executed, awaiting 你 approval)
