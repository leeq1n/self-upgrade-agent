# EXTENSIONS
L0: Cross-project extensions this project references, as a 1-table pointer.
Last P20-verified: 2026-07-13

| ID | Name | Status | Location |
|----|------|--------|----------|
| X1 | Knowledge Graph | idea | `../knowledge-graph-seed/` |
| X2 | Agent-onboarding skill | active | agent-onboarding skill (Hermes global; see "Status" below) |

- Knowledge graph integration is in a separate project at
  `../knowledge-graph-seed/`.  Per P21 (cross-project independence):
  this project LINKS to it, does not duplicate.  Trigger fires
  when v3.0.2 stage gate closes (met 2026-07-11).  Spec lives
  in `../knowledge-graph-seed/SEED.md`.  First commit (minimal
  `src/kg.py` stub) made 2026-07-11 (commit `4c79bbb`).

- **X2 Agent-onboarding skill** is a Hermes global skill
  (currently located at `~/.hermes/skills/agent-onboarding/`
  in the Hermes install, not a sibling project).  It contains
  the canonical M-* rule family (9 rules), AGENTS.md
  onboarding template, commit-msg hook template, and the
  M_RULE_AUTHORING recipe.  This project (SUA) adopts M-*
  rules from there as project-specific extensions
  (M-intent-parsing, M-learn, M-add-then-reduce) and
  re-promotes the meta-rules (M-self-audit, M-self-application)
  when their 3-condition gate is met (per project 2026-07-13
  workflow-rules batch).  Per P21 cross-project independence:
  this project LINKS to the skill via "agent-onboarding skill"
  text reference, does not duplicate content.  Per R8: text
  reference (not absolute path), since the skill location is
  a Hermes install detail, not a sibling project path.  Future
  intent (per user 2026-07-13): the skill will become a
  separately-installable efficiency plugin for other projects.