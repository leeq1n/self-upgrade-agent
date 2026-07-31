# Hooks inventory

> L0: Living inventory of hooks/ in SUA. Updated 2026-07-30 after
> v2.7.0 (cross_repo_audit integration) + v2.14.1 (LF normalization).

## Current hooks (3 files)

| File | Purpose | Installed at | Trigger |
|---|---|---|---|
| `commit-msg` | Validate commit message has P1-P29 cite (via hook_principles.json loader) | `.git/hooks/commit-msg` | every commit |
| `pre-commit` | Run 6 audit gates (eval_before + self_health_check + cross_repo_audit) | `.git/hooks/pre-commit` | every commit |
| `prepare-commit-msg` | Append M-n 29 5-step trailer when "task done" / "完成" / "PASS" detected | `.git/hooks/prepare-commit-msg` | every commit prep |

## Why 3 hooks (not 1 or 2)

Per P7 奥卡姆 + M-n 18 destruction:
- **commit-msg** = hard validator (rejects if no P## cite)
- **pre-commit** = multi-gate audit (cross_repo_audit + self_health_check + eval_before)
- **prepare-commit-msg** = soft reminder (appends trailer if missing)
- Each hook has single responsibility
- Combined = hard validation + audit + soft reminder = complete mechanical layer

## Install (after clone)

```bash
# Copy hooks to .git/hooks/ (NOT auto-installed by design)
cp hooks/commit-msg .git/hooks/commit-msg
cp hooks/pre-commit .git/hooks/pre-commit
cp hooks/prepare-commit-msg .git/hooks/prepare-commit-msg
chmod +x .git/hooks/commit-msg .git/hooks/pre-commit .git/hooks/prepare-commit-msg
```

On Windows (MSYS / git-bash), line endings must be LF (not CRLF).
The repo `.gitattributes` enforces this for `*.sh` and `hooks/*`.
If you see `bash: syntax error: unexpected end of file`, run:

```bash
dos2unix hooks/* .hermes/scripts/*.sh
```

## Uninstall

```bash
bash .hermes/scripts/uninstall.sh          # remove hooks only
bash .hermes/scripts/uninstall.sh --full   # remove everything
bash .hermes/scripts/uninstall.sh --dry-run # preview
```

## P-n / M-n cited

P5 (tests pass — hooks installable + testable), P11
(摘要+引用), P14 (docs stay current), P17 (老实说),
P25 (post-modify re-apply), P29 (recursion).

M-n 18 (destruction — record inventory before
over-engineering), M-n 32 (self-learning-guardrail
Guardrail #1+5).

## Cross-references

- `core-layer/governance-template.md` — eval-before +
  verify-after gate template
- `core-layer/phase-A-9-primitives-record.md` — 9
  primitives integration record
- `AGENTS.md` "Commit message contract"段 — hook contract
- `docs/OPERATING_RULES.md` § M-self-learning-guardrail —
  M-n 32 detail
- `.hermes/hook_principles.json` — single source of truth
  for P-n whitelist (used by commit-msg hook via loader)
