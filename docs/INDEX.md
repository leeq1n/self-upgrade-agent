# INDEX — full navigation map

> L0: Navigation index for the docs in `/docs/`.  Each entry:
> doc (summary) + companion (DETAIL) + TL;DR.  Read summary
> first; click through to detail only as needed.
> When any file in /docs/ is added/removed/renamed, update this
> index (per P14 docs stay current).

## Reading order for a fresh agent

1. **AGENTS.md** (root) — operating rules, L0 entry
2. **PROJECT_STATE.md** — current goal + next step
3. **HOW_TO_READ_GRAPH.md** — 3-step read pattern
4. **PRINCIPLES.md** — working principles (L0 + L1 layer)
5. **OPERATING_RULES.md** — M-n operating rules
6. **../TODO.md** — pending work (stub → `PLANS/`)

## L0: Entry / orientation

| Doc | Companion | TL;DR |
|---|---|---|
| [../AGENTS.md](../AGENTS.md) | [../AGENTS_DETAIL.md](../AGENTS_DETAIL.md) | Operating rules for AI agents in this repo |
| [INDEX.md](INDEX.md) | (this file) | Full navigation map |
| [PROJECT_STATE.md](PROJECT_STATE.md) | [PROJECT_STATE_DETAIL.md](PROJECT_STATE_DETAIL.md) | Goal + current state + next step |
| [CONSTRAINTS.md](CONSTRAINTS.md) | [CONSTRAINTS_DETAIL.md](CONSTRAINTS_DETAIL.md) | Invariants the system must preserve |
| [USER_INSIGHTS.md](USER_INSIGHTS.md) | [USER_INSIGHTS_DETAIL.md](USER_INSIGHTS_DETAIL.md) | Paraphrased user rules + verbatim quotes |
| [HOW_TO_READ_GRAPH.md](HOW_TO_READ_GRAPH.md) | (within file) | Read pattern for new agents (L0 → L1 → L2) |
| [SWITCH_SIGNALS.md](SWITCH_SIGNALS.md) | (within file) | Switch signals + action protocol |

## L1: Principles / rules

| Doc | Companion | TL;DR |
|---|---|---|
| [PRINCIPLES.md](PRINCIPLES.md) | [PRINCIPLES_FULL.md](PRINCIPLES_FULL.md) | Working principles (L0/L1) + per-P-n 实操 (L2) |
| [PRINCIPLES_DETAIL.md](PRINCIPLES_DETAIL.md) | [PRINCIPLES_DETAIL_DETAIL.md](PRINCIPLES_DETAIL_DETAIL.md) | Per-P-n full text (L2) |
| [OPERATING_RULES.md](OPERATING_RULES.md) | [OPERATING_RULES_DETAIL.md](OPERATING_RULES_DETAIL.md) | M-n operating rules (workflow discipline) |
| [EXTENSIONS.md](EXTENSIONS.md) | [EXTENSIONS_DETAIL.md](EXTENSIONS_DETAIL.md) | Extension rules (L0/L1/L2 + extensions) |
| [RECURSIVE_DECOMPOSITION.md](RECURSIVE_DECOMPOSITION.md) | (within file) | Top-down decomposition rules |
| [RECURSIVE_QUALITY.md](RECURSIVE_QUALITY.md) | (within file) | Recursive quality loop (拆解+类比+自指) |
| [ADD_THEN_REDUCE.md](ADD_THEN_REDUCE.md) | (within file) | Add-then-reduce operational pattern |
| [SUMMARY_LIFECYCLE.md](SUMMARY_LIFECYCLE.md) | (within file) | Summary lifecycle (destroy contract) |
| [PRINCIPLE_COLLAPSE_PREVENTION.md](PRINCIPLE_COLLAPSE_PREVENTION.md) | (within file) | 原则防崩塌 guardrails |
| [SELF_ORG.md](SELF_ORG.md) | (within file) | Self-organization patterns (P27) |
| [COMMON_PITFALLS.md](COMMON_PITFALLS.md) | (within file) | Common pitfalls observed in project history |

## L2: M-n detail files

Per `OPERATING_RULES.md` M-n numbering.  Load the relevant file when
applying that M-rule.  (M-n 1-10 are concept/principle-layer, no L1
file.)

| M-n | Doc | TL;DR |
|---|---|---|
| M-n 11 | [M_EXPERIMENT_IN_SUBPROJECT.md](M_EXPERIMENT_IN_SUBPROJECT.md) (+ [DETAIL](M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md)) | Sub-project experimental pattern |
| M-n 12 | [M_TERMINOLOGY_CLARITY.md](M_TERMINOLOGY_CLARITY.md) (+ [DETAIL](M_TERMINOLOGY_CLARITY_DETAIL.md)) | Terminology refinement rules |
| M-n 13 | [M_LAYER_EXTENSION.md](M_LAYER_EXTENSION.md) | L0/L1/L2 + extensions rules |
| M-n 14 | [M_TWO_TRACK_REASONING_DETAIL.md](M_TWO_TRACK_REASONING_DETAIL.md) | 类比+逻辑, 6-stage distribution |
| M-n 15 | [M_PRINCIPLE_REORDERING_DETAIL.md](M_PRINCIPLE_REORDERING_DETAIL.md) | 6-step after 原则 混乱 |
| M-n 16 | [M_OBSERVE_THINK_EXECUTE_DETAIL.md](M_OBSERVE_THINK_EXECUTE_DETAIL.md) | 6-stage + top-down 分治 |
| M-n 17 | [M_CONTEXT_FRESHNESS_CHECK_DETAIL.md](M_CONTEXT_FRESHNESS_CHECK_DETAIL.md) | Intra-agent + inter-domain freshness |
| M-n 18 | [M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md](M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md) | 6 sub-steps + 节点 生命周期 |
| M-n 19 | [M_FILE_NAMING_CONVENTION_DETAIL.md](M_FILE_NAMING_CONVENTION_DETAIL.md) | File naming conventions |
| M-n 20 | [M_AGENT_DISCOVERABILITY_CHECK_DETAIL.md](M_AGENT_DISCOVERABILITY_CHECK_DETAIL.md) | Cross-framework discoverability |
| M-n 21 | [M_ASK_OR_INFER_MARK_GUESS_DETAIL.md](M_ASK_OR_INFER_MARK_GUESS_DETAIL.md) | 3 sub-steps + top-down default |
| M-n 22 | [M_3W1H_THINK_FIRST_DETAIL.md](M_3W1H_THINK_FIRST_DETAIL.md) | 3W1H 分析法 BEFORE top-down |
| M-n 23 | [M_PERIODIC_RE_ANALYSIS_DETAIL.md](M_PERIODIC_RE_ANALYSIS_DETAIL.md) | re-分析 at 最终目标 |
| M-n 24 | [M_PACE_CONTINUITY_DETAIL.md](M_PACE_CONTINUITY_DETAIL.md) | commit + continue, no verbose ending |
| M-n 25 | [M_MESSAGE_PATTERN_RECOGNITION_DETAIL.md](M_MESSAGE_PATTERN_RECOGNITION_DETAIL.md) | Parse user message + patterns |
| M-n 26 | [M_CONTEXT_DECAY_MANAGEMENT_DETAIL.md](M_CONTEXT_DECAY_MANAGEMENT_DETAIL.md) | Detection + classification + compression |
| M-n 27 | [M_KNOWLEDGE_LAYER_ARCHITECTURE_DETAIL.md](M_KNOWLEDGE_LAYER_ARCHITECTURE_DETAIL.md) | 3-layer core/knowledge/project taxonomy |
| M-n 28 | [M_PLAN_CONDITIONAL_DETAIL.md](M_PLAN_CONDITIONAL_DETAIL.md) | 4-condition check (uncertain→plan, clear→continue) |
| M-n 29 | [M_ACCEPTANCE_PROTOCOL_DETAIL.md](M_ACCEPTANCE_PROTOCOL_DETAIL.md) | 5-step protocol + cold-start sim |
| M-n 30 | [M_KNOWLEDGE_CONTEXT_TRADE_OFF_DETAIL.md](M_KNOWLEDGE_CONTEXT_TRADE_OFF_DETAIL.md) | 4-priority: knowledge 充足 > ... |
| M-n 31 | [M_TASK_LIFECYCLE_DETAIL.md](M_TASK_LIFECYCLE_DETAIL.md) | 4-phase: init + execute + done-notify + retrospective |
| M-n 32 | [M_SELF_LEARNING_GUARDRAIL_DETAIL.md](M_SELF_LEARNING_GUARDRAIL_DETAIL.md) | 5 modification guardrails + auto-learning |
| M-n 33 | [M_NARRATIVE_AS_SPEC_DETAIL.md](M_NARRATIVE_AS_SPEC_DETAIL.md) | 3-primitive: parse + structure + codify |
| M-n 34 | [M_PRE_TASK_SCAN_DETAIL.md](M_PRE_TASK_SCAN_DETAIL.md) | Pre-task scan (4 sub-steps) |
| M-n 35 | [M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md](M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md) | 4 adversarial primitives (质疑/逆向/预演失败/对立论证) |
| M-n 36 | [M_PRE_RELEASE_AUDIT_DETAIL.md](M_PRE_RELEASE_AUDIT_DETAIL.md) | Release prep (5 checks) |

Unnumbered M-* docs (self-contained detail): [M_SELF_AUDIT.md](M_SELF_AUDIT.md),
[M_SELF_APPLICATION.md](M_SELF_APPLICATION.md),
[M_SKILL_SYNCHRONIZE.md](M_SKILL_SYNCHRONIZE.md),
[M_TURN_PATTERN_RECOGNITION_DETAIL.md](M_TURN_PATTERN_RECOGNITION_DETAIL.md) (stub; real content under M-n 25).

## L1: Operational patterns / knowledge

| Doc | Companion | TL;DR |
|---|---|---|
| [KNOWLEDGE_ORG.md](KNOWLEDGE_ORG.md) | [KNOWLEDGE_ORG_DETAIL.md](KNOWLEDGE_ORG_DETAIL.md) | Knowledge organization (taxonomy) |
| [MODEL_STRATEGY.md](MODEL_STRATEGY.md) | [MODEL_STRATEGY_DETAIL.md](MODEL_STRATEGY_DETAIL.md) | Which LLM, why, deployment notes |
| [LITERATURE.md](LITERATURE.md) | [LITERATURE_DETAIL.md](LITERATURE_DETAIL.md) | Papers read + how they constrain design |
| [MCP_TOOLS.md](MCP_TOOLS.md) | (within file) | MCP tool ecosystem + which tools to use when |
| [MEMORY_TOOLS.md](MEMORY_TOOLS.md) | (within file) | Memory system usage patterns |
| [SKILLS.md](SKILLS.md) | (within file) | Skill lifecycle / SkillOpt paper mapping |
| [SKILL_DESIGN.md](SKILL_DESIGN.md) | [SKILL_DESIGN_DETAIL.md](SKILL_DESIGN_DETAIL.md) | Skill design + incubation framework |
| [CROSS_RUNTIME_SKILL_BRIDGE.md](CROSS_RUNTIME_SKILL_BRIDGE.md) | (within file) | Agent Skills SKILL.md bridge for non-canonical runtimes |
| [RESEARCH_USAGE.md](RESEARCH_USAGE.md) | (within file) | 科研项目适配器模式 + 工作流 |
| [HANDOFF.md](HANDOFF.md) | [HANDOFF_DETAIL.md](HANDOFF_DETAIL.md) | Project handoff template |
| [ACCEPTANCE_PROTOCOL.md](ACCEPTANCE_PROTOCOL.md) | (within file) | Acceptance protocol |
| [ANALYSIS_PARENT_VERIFY.md](ANALYSIS_PARENT_VERIFY.md) | [ANALYSIS_PARENT_VERIFY_DETAIL.md](ANALYSIS_PARENT_VERIFY_DETAIL.md) | Parent verification analysis |
| [TODO_SESSION_PERSISTENCE.md](TODO_SESSION_PERSISTENCE.md) | [TODO_SESSION_PERSISTENCE_DETAIL.md](TODO_SESSION_PERSISTENCE_DETAIL.md) | Session persistence proposal (M-context-snapshot design) |

## Domain-specific / utility

| Doc | TL;DR |
|---|---|
| [PRINCIPLES_DETAIL_DETAIL.md](PRINCIPLES_DETAIL_DETAIL.md) | Per-P-n detail (L2 deep) |
| [CONSTRAINTS_DETAIL.md](CONSTRAINTS_DETAIL.md) | Constraints (L2 deep) |
| [EXTENSIONS_DETAIL.md](EXTENSIONS_DETAIL.md) | Extensions (L2 deep) |
| [HANDOFF_DETAIL.md](HANDOFF_DETAIL.md) | Handoff (L2 deep) |
| [KNOWLEDGE_ORG_DETAIL.md](KNOWLEDGE_ORG_DETAIL.md) | Knowledge org (L2 deep) |
| [LITERATURE_DETAIL.md](LITERATURE_DETAIL.md) | Literature (L2 deep) |
| [MODEL_STRATEGY_DETAIL.md](MODEL_STRATEGY_DETAIL.md) | Model strategy (L2 deep) |
| [USER_INSIGHTS_DETAIL.md](USER_INSIGHTS_DETAIL.md) | User insights (L2 deep) |
| [SKILL_DESIGN_DETAIL.md](SKILL_DESIGN_DETAIL.md) | Skill design (L2 deep) |
| [M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md](M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md) | Sub-project experiment (L2 deep) |
| [M_TERMINOLOGY_CLARITY_DETAIL.md](M_TERMINOLOGY_CLARITY_DETAIL.md) | Terminology clarity (L2 deep) |

## Plans

| Doc | TL;DR |
|---|---|
| [PLANS/PLAN_2026-07-30.md](PLANS/PLAN_2026-07-30.md) | Active work plan (ATDD: plan → ship → accept → fix) |

## See also

- **AGENTS.md** (root L0 entry doc)
- **core-layer/README.md** — 3-layer governance (核心/用户/项目)
- **core-layer/AGENTS_CORE.md** — always-loaded contract
