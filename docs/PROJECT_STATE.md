---
description: "Project goal, status, constraints, next step"
status: "summary"
---
# PROJECT_STATE — brief
> L0: Current project state (1-paragraph).  Load when: need snapshot of current goal/version/next step.

## Goal

**SUA is an agent-discipline knowledge library.**  It packages agent
behavior rules (P-n working principles + M-n operating rules),
reasoning primitives, and operating conventions that any agent
runtime can carry into a project.  The repo is self-contained and
does not depend on sibling repositories.

## What the repo holds

| Area | Location | Purpose |
|---|---|---|
| Operating contract | `core-layer/AGENTS_CORE.md` + `AGENTS.md` | always-loaded rules + per-task 段s (P11 split) |
| Knowledge library | `docs/` | principles, operating rules, design, conventions |
| Governance | `core-layer/` | 3-layer policy (核心/用户/项目) + modification gates |
| Commit gates | `hooks/` + `agent-tools/scripts/` | commit-msg / pre-commit / pre-push / prepare-commit-msg |
| Legacy runtime | `core/` + `src/` + `self_upgrade/` | v1.x-v3.x self-improving agent (documented legacy, functional) |

## Current version

Latest CHANGELOG entry: **v2.22.x** (see `CHANGELOG.md`).  Release
history is documented there; `README_DETAIL.md` covers the legacy
code (v1.x-v3.x), which is kept because tests and CLI scripts
exercise `src/` (removing it would break CI).

## Tests

`pytest tests/` collects ~875 tests.  Environment-dependent failures:
- LLM / network tests skip when no API key or `SUA_SKIP_NETWORK=1`.
- `core/planner.py` is LLM/user-modified (a known open decision —
  keep or revert, see `test_core_planner_md5_matches_head` which is
  deselected).  Harness tests that depend on planner.py's pre-modification
  shape fail until that decision is made.

## Constraints

See `docs/CONSTRAINTS.md` for the full list (奥卡姆, fail-OPEN,
atomic, user-edits-keys-never-agent, etc.).  Project constraints
change rarely; that file is the source of truth.

## Next step

See `docs/PLANS/PLAN_2026-07-30.md` for the active work plan
(`TODO.md` is a stub that points there).

## References

- INDEX: [INDEX.md](INDEX.md)
- Working principles: [PRINCIPLES.md](PRINCIPLES.md)
- Operating rules: [OPERATING_RULES.md](OPERATING_RULES.md)
- User intent: [USER_INSIGHTS.md](USER_INSIGHTS.md)
- Hard rules: [CONSTRAINTS.md](CONSTRAINTS.md)
- Pending tasks: [../TODO.md](../TODO.md)
- Done tasks: [../DONE.md](../DONE.md)
