# EXTENSIONS_DETAIL — Detail (L2)
Last P20-verified: 2026-07-14 (split from EXTENSIONS.md per R4+R6)

> L0: L2 detail for EXTENSIONS.md.  Per R4 (EXTENSIONS.md is
> table-only pointer), this file holds prose detail.  Per R6,
> this detail file is referenced from EXTENSIONS.md.

## X1: Knowledge Graph (idea)

Knowledge graph integration is in a separate project at
`../knowledge-graph-seed/`.  Per P21 (cross-project independence):
this project LINKS to it, does not duplicate.

**Trigger**: v3.0.2 stage gate closes (met 2026-07-11).

**Spec**: lives in `../knowledge-graph-seed/SEED.md`.

**First commit**: minimal `src/kg.py` stub, 2026-07-11
(commit `4c79bbb`).

## X2: Agent-onboarding skill (active)

**Location**: Hermes global, `~/agent-tools/skills/agent-onboarding/`
(not a sibling project; Hermes install detail).

**Contents**: canonical M-* rule family (9 rules), AGENTS.md
onboarding template, commit-msg hook template, M_RULE_AUTHORING
recipe.

**Adoption**: this project (SUA) adopts M-* rules from there as
project-specific extensions:

- **M-intent-parsing** (paraphrase + steps + ask)
- **M-learn** (observe pattern + codify)
- **M-add-then-reduce** (add phase + reduce phase)
- **M-self-audit** (re-promoted when 3-condition gate met,
  per project 2026-07-13 workflow-rules batch)
- **M-self-application** (re-promoted same batch)

**Per P21**: cross-project independence.  This project LINKS to
the skill via "agent-onboarding skill" text reference, does not
duplicate content.

**Per R8**: text reference (not absolute path), since the skill
location is a Hermes install detail, not a sibling project path.

**Future intent (per user 2026-07-13)**: the skill will become
a separately-installable efficiency plugin for other projects.
This project will LINK to it (not duplicate it).

