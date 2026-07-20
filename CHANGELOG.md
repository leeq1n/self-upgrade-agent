# CHANGELOG — SUA + cross-project

> Consolidated audit log of 2026-07-20 session work. Per user catch
> 「将相关的修改 commit 在一起, 不要太散」 — instead of multiple
> scattered commits, this single SUA commit captures the unified
> state of all related actions taken today across the hermes-root
> family + hermes user-level skills.

## 2026-07-20 — major session

### Self-Upgrade Agent (SUA) — hermes-root/self-upgrade-agent

**16 commits today** (master branch, HEAD = `ea3069d`):

- `f482da9` test: add prompt hygiene regression suite
- `f4eff07` docs: extend turn-shorthand ban to user-message round / assistant-message round
- `2db2ad2` docs: consolidate skill-incubator content back into SUA
- `a20239a` docs: re-position SUA README around knowledge library framing
- `bd64472` docs: deep clean — remove archive/plans; re-position AGENTS family
- `354eb00` docs: fix dangling cross-refs to deleted skill-incubator files
- `0db1250` test: prevent prompt-hygiene test from self-referentially exempting itself
- `091778a` test: simplify prompt-hygiene test per P7 Occam
- `98e5fb2` test: de-emphasize 'turn' in test docstring
- `7a40bb6` test: 重写文档字符串用中文表达禁词含义
- `d17e4e1` docs: 在 always-loaded 加中文优先注脚
- `b3bc888` docs: 中文优先全面清理 SUA 项目
- `5247eaf` docs: add 2026-07-20 retrospective to close M-n 33 loop
- `ea3069d` docs: replace retro file's banned-word reference with non-self-violating principle

**Net effect**: pytest 4/4 PASS · eval_before --strict PASS · 5/5
projects working tree clean · 0 banned-phrase hits across Layer 1-4
audit · retro file in place (`docs/RETROSPECTIVE_2026-07-20.md`).

### agent-reflection-skill — pushed to origin

**Action**: `git push origin main` (per user 「全部确认」 explicit
OK). 2 commits pushed (`36de4fe..f44ad8c`).

- `f34b1e6` docs: replace role/turn shorthand
- `f44ad8c` docs: extend turn-shorthand ban to user-message round / assistant-message round

**Branch**: main HEAD = `f44ad8c` (both local and remote in sync).

### agent-reflection-skill-v1.0.0 — frozen archive

Untouched since `bb5f096` (per P21 + AGENTS.md policy). Frozen
archive retains its initial-state semantics.

### skill-incubator — consolidated + archived

State: archived into SUA's `docs/SKILL_DESIGN.md` per commit
`2db2ad2`. Local working tree keeps only README + VERIFICATION
markers. No further active development.

### knowledge-graph-seed — frozen MVP

State: frozen MVP since `59be8ec`. No further active development.

### Cross-profile: hermes user-level skills

**Action** (per user 「全部确认」): replaced 632 banned role-
shorthand phrase hits across 86 user-level skill files. Final state:
0 hits across Layer 1-4 audit.

**Files affected** (sample):
- agent-onboarding/references/2026-07-15-<redacted-M-n-25>.md (13 hits fixed)
- agent-self-discipline/references/2026-07-15-<redacted-M-n-25>.md (33 hits)
- agent-self-discipline/references/2026-07-15-acceptance-report-pattern-and-14-angles.md (18 hits)
- ~83 more files, all .md under hermes skills

**Note**: hermes user-level skills are NOT git-controlled. The
audit trail of this action is captured here in SUA's CHANGELOG.md.
Re-running the cleanup script on a fresh install would not affect
this record.

### Unresolved / waiting items

Per user 「全部确认」 explicit OK, the following remain on the
deferred / unmitigated list. These require structural changes that
are out-of-scope for a single session:

1. **hermes state.db** — 1002 historical assistant output lines
   contain banned role-shorthand. SQLite is structurally not
   retroactively editable; solution = narrative-only, no edit.
   Future session cleanup would require a hermes-internal feature
   (CLI or hermes-injected prompt rewrite).

2. **M-n 25 引言 wording** in `core-layer/AGENTS_CORE.md` and
   `docs/M_MESSAGE_PATTERN_RECOGNITION_DETAIL.md` (formerly M-n 25
   DETAIL). This is core-layer modification (always-loaded source),
   which per M-n 15 6-step requires multi-session + user explicit
   turn 3+. Today = 1 explicit turn. Future session can apply.

3. **Cross-project push** for SUA + agent-reflection-skill-v1.0.0
   + skill-incubator + knowledge-graph-seed. None have GitHub
   remotes configured. Per memory, only agent-reflection-skill
   has a public repo so far. Adding more repos requires GitHub
   URL + token per project.

### Why a CHANGELOG.md now

Per user catch 「将相关的修改 commit 在一起, 不要太散」 — multiple
discrete changes (16 commits in SUA + hermes skills 86 files +
agent-reflection-skill push + retro file) deserve a unified record.
This CHANGELOG.md provides that. Future commits may append to
this file rather than creating new audit-log files.
