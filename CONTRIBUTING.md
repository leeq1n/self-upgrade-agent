# Contributing to Self-Upgrade Agent (SUA)

> L0: SUA welcomes contributions that strengthen the agent discipline
> knowledge library. All contributions are governed by the SUA
> operating rules (P-n + M-n, see AGENTS.md).

## Before you start

1. **Read** `AGENTS.md` and `core-layer/AGENTS_CORE.md` to understand
   the operating contract. SUA is a knowledge library for agent
   self-discipline; every contribution is evaluated against the
   existing P-n principles.
2. **Read** `core-layer/README.md` for the 3-layer governance model:
   - **Core layer** (`core-layer/` + `AGENTS.md` + `hooks/` + key
     docs) — modify rarely, with eval-before + verify-after gates.
   - **User layer** (user-facing memory + user-specific files) —
     modify when user habits emerge.
   - **Project layer** (project-specific docs) — modify as project
     evolves, but as a knowledge base (NOT a log).
3. **Read** `docs/SKILL_DESIGN.md` if you are designing or
   incubating a new skill.

## Workflow

1. **Branch** from `main`: `git checkout -b <type>/<scope>` where
   `<type>` is one of: `feat`, `fix`, `docs`, `test`, `refactor`.
2. **Cite a P-n** in every commit message body (the `commit-msg`
   hook enforces this; see `hooks/README.md`).
3. **Run tests** before commit: `pytest tests/` (when applicable).
4. **One concern per commit** (per P-11 摘要+引用). Small focused
   changes are easier to review.
5. **Update docs in the same commit** if you change behavior (per
   P-14 docs current).

## Commit message contract

Every commit message MUST cite at least one P-n in the body:

```
<type>(<scope>): <short description>

Cite P## here with a one-line reason. For example:
- P5  (test before commit)
- P11 (摘要+引用, no replicate)
- P14 (docs current)
- P17 (老实说, no fake green)
- P20 (README ≤ 7KB)
- P22 (when stuck, plan)
```

Allowed P-n values: P1-P29 (minus P6/P15/P16/P24, demoted
during early project consolidation). See `docs/PRINCIPLES.md`
for the complete list.

## Self-Contained Mandate (per P-14)

User-facing docs and chat output use **canonical names**, not
internal identifiers:

- ✅ Reference public standards (AAIF, Linux Foundation, Anthropic,
  OpenAI, GitHub, etc.)
- ❌ Do NOT reference internal sibling project paths
  (e.g., `../sibling-name/`) in user-facing files
- ❌ Do NOT reference internal chat / session identifiers
- ❌ Do NOT reference round numbers (internal session history)
- ❌ Do NOT include dev-session retrospectives in user docs

## Review process

1. Open a pull request against `main`.
2. The `commit-msg` hook validates P-n cite locally.
3. CI runs `pytest tests/ --ignore=tests/test_e2e.py` (per
   the test suite baseline).
4. Maintainer reviews against:
   - P-n alignment (does the change follow existing principles?)
   - 3-layer policy (is the right layer being modified?)
   - Mirror-not-replicate (per P-11, are changes adding value or
     duplicating existing content?)
5. At least one approval + green CI = merge eligible.

## Code of conduct

- Be precise. Cite the principle, the section, the file path.
- Be honest. If verification failed, say so (per P-17).
- Be minimal. Small, focused changes (per P-7 Occam + M-n 18
  destruction).

## See also

- `README.md` — project orientation
- `AGENTS.md` — operating rules
- `core-layer/AGENTS_CORE.md` — always-loaded subset
- `docs/OPERATING_RULES.md` — M-n 1-27 operating rules
- `docs/PRINCIPLES.md` — P-n 1-29 principles
