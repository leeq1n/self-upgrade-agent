# Hooks inventory

> L0: Living inventory of hooks/ in SUA. Updated 2026-07-31 after
> v2.22.7 (install-hooks.sh one-click installer + Windows cygpath
> path handling).

## Current hooks (4 files)

| File | Purpose | Installed at | Trigger |
|---|---|---|---|
| `commit-msg` | Validate commit message has P1-P29 cite (via hook_principles.json loader) | `.git/hooks/commit-msg` | every commit |
| `pre-commit` | Run 4 audit gates (eval_before + self_health_check + cross_repo_audit + validate_links) | `.git/hooks/pre-commit` | every commit |
| `prepare-commit-msg` | Append M-n 29 5-step trailer when "task done" / "完成" / "PASS" detected | `.git/hooks/prepare-commit-msg` | every commit prep |
| `pre-push` | BLOCKER-only ship gate (self_health_check + validate_links) | `.git/hooks/pre-push` | every push |

## Why 4 hooks (not 1 or 2)

Per P7 奥卡姆 + M-n 18 destruction:
- **commit-msg** = hard validator (rejects if no P## cite)
- **pre-commit** = multi-gate audit (eval_before + self_health_check + cross_repo_audit + validate_links)
- **prepare-commit-msg** = soft reminder (appends trailer if missing)
- **pre-push** = proactive ship gate (BLOCKER-only blocking, per RCA)
- Each hook has single responsibility
- Combined = hard validation + audit + soft reminder + ship gate

## Install (after clone) — one command

```bash
# From the TARGET project (SUA cloned at .sua/):
bash .sua/install-hooks.sh

# Overwrite existing hooks:
bash .sua/install-hooks.sh --force

# Explicit SUA source:
SUA_DIR=/path/to/.sua bash .sua/install-hooks.sh
```

**Design note (v2.22.7)**: install-hooks.sh rewrites hook script
paths to point INSIDE the SUA clone (`<sua>/.hermes/scripts/`).
The target project gets ONLY `.git/hooks/` entries — no `.hermes/`
directory, no script copies. This keeps target projects clean and
agent-agnostic (codex / claude / hermes all fine).

**Windows**: hooks use `cygpath -w` to convert MSYS paths (`/c/...`)
to native Windows paths before calling python. Requires git-for-windows
(which ships cygpath) — standard on Windows.

## Uninstall

```bash
# Remove hooks only (target project has no .hermes/ to clean)
rm .git/hooks/commit-msg .git/hooks/pre-commit .git/hooks/prepare-commit-msg .git/hooks/pre-push
```

## Notes

- Hooks are NOT auto-installed by design (users opt in).
- Python must be on PATH for hooks to run.
- pre-commit is fail-open (warnings, exit 0) unless STRICT_EVAL=1.
- pre-push blocks only on BLOCKER-level findings.
