# Self-Upgrade Agent (SUA)

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)](CONTRIBUTING.md)
[![AAIF Compatible](https://img.shields.io/badge/AAIF-AGENTS.md%20compatible-blueviolet)](AGENTS.md)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-open%20standard%202025--12--18-success)](docs/CROSS_RUNTIME_SKILL_BRIDGE.md)

> L0: SUA project README — orientation, current state.
> SUA is an **agent discipline knowledge library** — agent
> behavior rules, reasoning primitives, and operating principles
> that you can carry into any agent runtime.

## What is SUA?

SUA packages three categories of agent knowledge:

1. **Agent behavior rules** — working principles and operational
   rules that any agent on this contract should follow.
2. **Reasoning primitives** — critical/constructive thinking
   primitives used to evaluate and build.
3. **Operating conventions** — how a new agent onboards, how
   commits are structured, how rules evolve.

The agent reads these on session start and uses them to constrain
its behavior.

## Quick start (new agent)

1. Read `AGENTS.md` (operating rules)
2. Read `docs/HOW_TO_READ_GRAPH.md` (3-step read pattern)
3. Read `docs/HANDOFF.md` (project-specific onboarding)
4. Read `docs/PROJECT_STATE.md` Goal section (current state)
5. Read `docs/PRINCIPLES.md` (L0 + L1 layer only)
6. Optional: `docs/SKILL_DESIGN.md` (if designing or
   incubating a new skill)

Total: ~30 min onboarding.

**For non-canonical runtimes** (Cursor / Codex / Antigravity
that prefer the Agent Skills `SKILL.md` format, or stateless
sessions that need a one-line entry point), see
[`docs/CROSS_RUNTIME_SKILL_BRIDGE.md`](docs/CROSS_RUNTIME_SKILL_BRIDGE.md).
The bridge is a convenience layer; the 6-step workflow above is
the canonical SUA onboarding.

### What the agent gets

- `AGENTS.md` — operating rules (always-loaded contract)
- `core-layer/AGENTS_CORE.md` — cache-stable subset (~10 KB)
- `core/AGENTS_L0.md` — L0 contract that ships to runtime

The agent reads these on session start. You only need to point
it at the directory once.

## Working principles (P-n) + workflow (M-n)

See `docs/PRINCIPLES.md` (25 P-n working, P1-P29 minus 4
demoted). The commit-message hook enforces P-n cite in commit
messages.

See `docs/OPERATING_RULES.md` (M-n 1-27).

## Contributing

Contributions should follow the operating rules in `AGENTS.md`.
The commit-message hook enforces that every commit message
follows the contract.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the contribution
workflow and acceptance protocol.

## Detailed content (L2)

For full project history, CLI documentation, code architecture,
version history, and other L2 detail, see
[`README_DETAIL.md`](README_DETAIL.md). Per the R6 split rule,
this companion is required when the README exceeds 7 KB.

## Code legacy

This project was originally a self-improving agent that modifies
`core/planner.py`. The code still exists and is functional, but
is no longer the project's focus. For code documentation and CLI
usage, see `README_DETAIL.md` § Code legacy.

## Changelog

For the full history of SUA development, see
[`CHANGELOG.md`](CHANGELOG.md).

## Code of conduct

Participation in this project is governed by the
[Contributor Covenant](CODE_OF_CONDUCT.md), version 2.1.

## License

This project is licensed under the [MIT License](LICENSE)
(c) 2026 LiQin.

## Status

This repo is the default direct-use path: clone it into your
project, point your agent at `AGENTS.md`, and the agent absorbs
the operating contract on session start.
