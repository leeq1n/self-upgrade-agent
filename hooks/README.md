# Hooks inventory (per 你 turn 2026-07-16 + M-n 18 destruction)

> L0: Living inventory of hooks/ in SUA.  Updated 2026-07-16
> after Phase A (commit `80cad53`) added 4 critical-thinking
> keyword check.

## Current hooks (2 files)

| File | Purpose | Installed at | Trigger |
|---|---|---|---|
| `commit-msg` | Validate commit message has P1-P29 cite | `.git/hooks/commit-msg` | every commit |
| `prepare-commit-msg` | Append M-n 29 5-step trailer when "task done" / "完成" / "PASS" detected; Phase A addition: also detects 4 critical-thinking keywords (质疑/逆向/预演失败/对立论证) for dedup | `.git/hooks/prepare-commit-msg` | every commit prep |

## Why 2 hooks (not 1 or 3)

Per P7 奥卡姆 + M-n 18 destruction:
- **commit-msg** = hard validator (rejects if no P## cite)
- **prepare-commit-msg** = soft reminder (appends trailer if missing)
- Each hook has single responsibility
- Combined = hard validation + soft reminder = complete mechanical layer

## P-n / M-n cited

P5 (tests pass — hooks installable + testable), P11
(摘要+引用), P14 (docs stay current), P17 (老实说),
P25 (post-modify re-apply), P29 (recursion).

M-n 18 (destruction — record inventory before
over-engineering), M-n 32 (self-learning-guardrail
Guardrail #1+5), M-n 35 (critical-thinking primitives
integration per Phase A).

## Cross-references

- `core-layer/governance-template.md` — eval-before +
  verify-after gate template
- `core-layer/phase-A-9-primitives-record.md` — 9
  primitives integration record
- `AGENTS.md` "Commit message contract"段 — hook contract
- `docs/OPERATING_RULES.md` § M-self-learning-guardrail —
  M-n 32 detail
