---
description: "Onboarding doc for any new agent entering this project. Read this FIRST (after AGENTS.md), then follow the next-steps tree."
status: "active"
last_updated: "2026-07-14"
---

# HANDOFF — Onboard a new agent into SUA

> L0: Orientation for any new agent taking over this project.
> Read this file first (after `AGENTS.md`), then follow the
> next-steps tree at the bottom.

## What this project IS (per c73 vision sync + c52 SELF_ORG + c57 read pattern)

`self-upgrade-agent` (SUA) is a **project that constrains
agent behavior by its own documentation**, so an agent that
follows the project's rules can operate correctly **without
depending on the Hermes runtime**.

**Three deliverable layers** (per user meta-rule 2026-07-14 + c89 M-n 11):

1. **Operational rules**: 25 P-n (P1-P29
   minus P6 + P15 + P16 + P24) + 24 M-n
   (M-task-summary through M-pace-continuity,
   per c95-c134)
2. **Self-organization**: the project itself follows its own
   rules (per P27 + 7-check pattern; documented in
   `docs/HOW_TO_READ_GRAPH.md`)
3. **Reusable reasoning patterns**: SUA is the *origin*
   (孵化器, hatching machine) for the `agent-reflection-skill`
   at `../agent-reflection-skill/`.  Patterns first appear in
   SUA, then get extracted into the skill when reusable.

**Why this matters for you (the new agent)**: this is a
**meta-rules project**.  The rules document themselves are
the contract.  Reading and applying them IS the work.

## Quick orientation — what to read first

| Order | Doc | What it gives you |
|---|---|---|
| 1 | `AGENTS.md` | Operating rules for agents (project entry) |
| 2 | `docs/HOW_TO_READ_GRAPH.md` | 3-step read pattern (L0→L1→L2) |
| 3 | `docs/PROJECT_STATE.md` | Current goal + last commits + next step |
| 4 | `docs/PRINCIPLES.md` (top) | The 4 root axioms + 5-family framework |
| 5 | `docs/OPERATING_RULES.md` | 9 M-* rules (workflow patterns) |
| 6 | Below in this HANDOFF.md | Where to start working |

**Don't read**: the `_DETAIL.md` companion files unless you
need L2 depth on a specific doc.  They're reference, not
orientation.

## Current state (per HEAD = commit 1f1d205, c78 = 47b)

- **Commits**: 319 in mainline
- **Last commit**: c78 = P3+P24 merge (47b, c47 plan)
- **P-n count**: P1-P29 minus P6 + P15 + P16 + P24 = 25 working principles (post c47a + c78 + c79 + c80 + c96 P28 lift + c167 P29 lift)
- **R-n compliance**: R5 compliant (0 violations);
  R4/R6 conflict resolved (c75); R12 still has 1 violation
  (knowledge-graph-seed PHILOSOPHY.md stale, sibling project)
- **M-n status**: 21 operator rules (M-n 1-21; M-n 1-9 = M-task-summary, M-must-read, etc. from c18 + c37; M-n 10-21 = c83 M-skill-synchronize, c89 M-experiment-in-subproject, c92 M-terminology-clarity, c95 修订 L4 boundary, c97 M-layer-extension, c98 M-two-track-reasoning, c99 M-principle-reordering, c100 M-observe-think-execute, c106 M-context-freshness-check, c111 M-recursive-summary-protocol, c115 M-file-naming-convention, c116 M-agent-discoverability-check, c118 M-ask-or-infer-mark-guess) (M-task-summary, M-must-read,
  M-context-snapshot, M-subtask-summary, M-intent-parsing,
  M-learn, M-add-then-reduce, M-self-audit, M-self-application)
- **MCP tools**: 5 tools available (chrome_devtools, llm_wiki,
  zotero, sciverse, mineru) — see `docs/MCP_TOOLS.md`
- **Skill relationship**: SUA is upstream; skill is downstream
  — see "Sibling projects" below

## Active plan (next ~10 commits)

| # | Commit | Action | Source |
|---|---|---|---|
| c79 | 47c | demote P15 (stage gate) to P5 实操 | `docs/MERGE_EVAL.md` (c47 4 candidates, 2 done so far) |
| c80 | 47d | demote P16 (ad-hoc verify) to P5 实操 | same |
| c81 | knowledge_org 信息拓扑段 | codify 方案 C (graph index + flat content) per user audit | this turn's plan + `docs/KNOWLEDGE_ORG.md` |
| c82 | README vision sync (R5-safe) | sync vision to 4th doc (still stale per c73 follow-up) | README.md |
| c83 | parent verify batch | verify c73-c82 per SUMMARY_LIFECYCLE | plan |
| -- (hermes-root project, separate repo) -- |
| skill | process triggers | `docs/process/when-to-reflect.md` with trigger phrases | `agent-reflection-skill/SKILL.md` reference |
| skill | case studies | 1 case study each: analogy/induction/reflection/abduction | skill project plan step 3 |
| skill | port-test | verify works in 2+ agent frameworks | plan step 5 |

**Why SUA is the priority, not skill**: SUA is the source of
patterns (per user meta-rule 2026-07-14 + c53 KNOWLEDGE_ORG).
Skill is downstream — extracting patterns only works after
SUA stabilizes them.  Skill can wait until SUA's 47c/47d are
done (so P-n reduction is final), then skill extraction
follows.

## Sibling projects

| Project | Path | Role | Status |
|---|---|---|---|
| `self-upgrade-agent` | this project | origin (rules + patterns + 7-check) | active, 319 commits |
| `agent-reflection-skill` | `../agent-reflection-skill/` | downstream (skill for any agent) | early scaffold (2 commits), see plan above |
| `knowledge-graph-seed` | `../knowledge-graph-seed/` | sibling (kg graph backend) | R12 stale, out of SUA scope |

For the skill project: read `../agent-reflection-skill/README.md`
for its scope, then `SKILL.md` for invocation contract.

## Key files at a glance

| Layer | Doc |
|---|---|
| **L0** (entry) | `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/HOW_TO_READ_GRAPH.md` |
| **L1** (operational) | `docs/PRINCIPLES.md`, `docs/OPERATING_RULES.md` |
| **L2** (detail) | `docs/PRINCIPLES_FULL.md`, `docs/PRINCIPLES_DETAIL_DETAIL.md`, `docs/PRINCIPLES_DETAIL.md` (root axioms), `docs/OPERATING_RULES_DETAIL.md` |
| **Audit / plan** | `docs/PROJECT_TOPDOWN_AUDIT.md` (last full audit, c50), `docs/PLAN_TOPDOWN_REORG.md`, `docs/MERGE_EVAL.md` (c47 4 candidates) |
| **Contracts** | `docs/SUMMARY_LIFECYCLE.md` (recursive destroy contract, c62), `docs/MCP_TOOLS.md`, `docs/EXTENSIONS.md` (+ `_DETAIL.md`) |
| **Self-ref** | `docs/SELF_ORG.md` (P27 candidate, c52), `docs/HOW_TO_READ_GRAPH.md` (3-step pattern, c57) |

## 3-project arch (per c83 + c85 + round 82)

SUA is part of a 3-project architecture:

- **SUA** (`self-upgrade-agent/`) = 原则库
  (24 P-n + 21 M-n + 8 L2 companions + HANDOFF)
- **skill-incubator** (`../skill-incubator/`) =
  skill 孵化器 (designs + incubates skills)
- **agent-reflection-skill** (`../agent-reflection-skill/`) =
  自我改进 skill (6 reasoning primitives + recursion)

## Framework-agnostic (per M-n 20)

This project is designed for:
- **Hermes** (current)
- **Codex** (per user message)
- **Claude Code** (per user message)
- **Others** (auto-detected via AGENTS.md)

File names avoid Hermes-specific terms (per M-n
19).  Future agents should be able to read this
project without Hermes-specific knowledge.

## Detail (L2)

For operational defaults, anti-patterns, health-check, and see-also cross-references, see [`HANDOFF_DETAIL.md`](HANDOFF_DETAIL.md).  Per R6, this companion is required when the summary exceeds 7 KB.
