# CHANGELOG — Self-Upgrade Agent (SUA)

> Canonical log of SUA releases and significant changes.
> Per P-14 docs current + P-17 no fabricate, this file documents
> the actual released state of the project on
> [github.com/leeq1n/self-upgrade-agent](https://github.com/leeq1n/self-upgrade-agent).

## 2026-07-30 — cross-repo enforcement

### v2.6.1 — CHANGELOG v2.6.0 entry (2026-07-30)

Commit: `0ad78e8`. Tag: `v2.6.1`.

**Doc-only PATCH.** Adds the v2.6.0 entry that the
`self_health_check` audit's `changelog_covers_recent_tags`
check flagged. This is the audit validating itself end-to-end:
v2.6.0 shipped the cross-repo audit, the audit caught the
missing changelog entry, v2.6.1 closes the gap.

No code or protocol changes. Behavior identical to v2.6.0.

### v2.6.0 — cross_repo_audit + tests (2026-07-30)

Commit: `60142e6`. Tag: `v2.6.0`.

**Feature MINOR.** Ships the cross-repo enforcement layer
per docs/PRINCIPLE_COLLAPSE_PREVENTION.md:

- `.hermes/scripts/cross_repo_audit.py` (8248 B) — audits
  sibling repos from upstream's perspective. Checks: Leaf-Only
  contract (adapter/ present), mirror pollution (top-level
  core-layer/ / docs/ / hooks/ / src/ / benchmarks/),
  self-contained AGENTS.md / README.md / TASK_HANDOVER.md
  (no per-user-message / R-number / c-number / hermes-root
  refs), submodule tag-pinning (prefer tag = over branch =).
- `tests/test_cross_repo_audit.py` (7085 B) — 15 unit tests
  covering all 4 check categories + CLI integration
  (advisory vs --strict exit codes).

**Audit run on real sibling (`../sua-start/self-upgrade-agent`)**:
7 failures detected (94 files in docs/, 117 in src/, internal
refs in AGENTS.md / README.md). The audit would have caught
those mirror problems before they shipped.

Advisory by default; `STRICT_EVAL=1` (or `--strict`) promotes
to nonzero exit. Hook integration point: `hooks/pre-commit` can
add a `cross_repo_audit` invocation in a follow-up commit.

**Decision artifact**: `docs/IMPLEMENTATION_PLAN_2026-07-30.md`
(v2.5.4) ranks 17 scenarios; v2.6.0 implements A2 (cross_repo_audit)
as the prerequisite for A4 (weekly cron).

## 2026-07-30 — self-audit integration

### v2.5.1 — M-n 34 pre-task vocabulary check (2026-07-30)

Commit: `bae820e`. Tag: `v2.5.1`.

**Feature PATCH.** Adds `.hermes/scripts/self_health_check.py`
(8.2 KB) — string-match audit surfacing commits that omit
M-n 34 pre-task vocabulary. Pre-commit hook calls it
fail-open by default; `STRICT_EVAL=1` promotes to block.

The audit covers three vocabulary signals derived from
early SUA protocol:

1. `changelog_covers_recent_tags` — latest tag has matching
   CHANGELOG entry.
2. `recent_commits_cite_tradeoff` — commits use Q1/Q2/Q3
   trade-off language.
3. `recent_commits_cite_mn34_pre_task` — commits cite M-n 34
   pre-task scan vocabulary.

**Audit run on the v2.5.1 commit itself** (per
self-consistency requirement): PASS for the commit body,
FAIL for older commits without tradeoff language — those
warnings are informational, not regressions.

### v2.5.0 — add self_health_check + pre-commit integration (2026-07-30)

Commit: `c063a36`. Tag: `v2.5.0`.

**Feature PATCH.** First real-ship of the self-audit
infrastructure. 1 file added (`.hermes/scripts/self_health_check.py`,
180 lines) + 21 lines added to `hooks/pre-commit`.

- P12 (knowledge in project): audit lives in `.hermes/scripts/`,
  not in memory.
- P14 (docs current): this entry follows the audit (the
  audit's own delivery is not wordy).
- P17 (no fabricate): script is string-match, not LLM-judgment.
- P9 (hard rules): same.
- P7 (Occam): the audit is one new check + one hook fragment.
  The cost is small; the gain is regression prevention on
  wordy-trap claims.

**Orphaned tag notice**: v2.4.3 tag points to commit
`01840dd`, not reachable from `main` HEAD (orphaned by the
v2.4.4 amend + force-push). Per P-17 honest reporting, the
orphan is recorded here so future readers do not chase it.

Commit: `231691f`. Tag: `v2.4.4`.

**Docs-only PATCH.** Removed the 'this repository is the
canonical source of truth' paragraph from `README.md` header.
The paragraph was self-referential agent noise with no terminal-user
value. The actual upstream URL stays in `CHANGELOG.md` (where it
matters for release traceability).

No code or protocol changes. Behavior identical to v2.4.3.

### v2.4.3 — post-release CHANGELOG + canonical pointer (2026-07-30)

Commit: `01840dd`. Tag: `v2.4.3`.

**Docs-only PATCH.** Two self-application fixes after
post-release audit:

1. CHANGELOG.md was missing the v2.4.2 entry that the v2.4.2
   release point `c26d042` had already shipped. Now added.
2. README.md header lacked an explicit canonical pointer.

Both reflect the kind of post-release catches R137 / R159
warn against: agent reports 'release done' without verifying
downstream artifacts agree.

No code or protocol changes. Behavior identical to v2.4.2.

### v2.4.2 — CHANGELOG.md update (2026-07-30)

Commit: `c26d042`. Tag: `v2.4.2`.

**Doc-only PATCH release** (per P-127 version policy). Documents
v2.3.0 / v2.3.1 / v2.4.0 / v2.4.1 in CHANGELOG so the canonical
release log matches what was actually shipped to GitHub.

Behavior is identical to v2.3.1. No code or protocol changes.

### v2.3.1 — self-contained mandate compliance (2026-07-30)

Commit: `4a5b76d`. Tag: `v2.3.1`.

**Doc-only release**. Removes internal cross-references
(sibling project paths, dev commit numbers, round numbers)
from user-facing files (`README.md`, `CONTRIBUTING.md`,
`RELEASE_NOTES_v2.3.0.md`). Public standards (Anthropic
Agent Skills, AAIF) and SUA's own protocol names are kept.

No code or protocol changes. All v2.3.1 behavior is
identical to v2.3.0.

### v2.3.0 — open-source compliance (2026-07-30)

Commit: `049e768`. Tag: `v2.3.0`.

First re-open-source release. Adds:

- **LICENSE** (MIT, 1061 B) — first time added
- **CONTRIBUTING.md** (3419 B) — contribution workflow and
  P-n commit-msg convention
- **CODE_OF_CONDUCT.md** (5485 B) — Contributor Covenant v2.1
- **docs/CROSS_RUNTIME_SKILL_BRIDGE.md** (4483 B) — Agent
  Skills open standard bridge for non-canonical runtimes
- **README badges** — MIT / PRs Welcome / AAIF / Agent Skills
- **README sections** — Changelog / Code of conduct / License
- Cleanup — removed 18.1 MB chromedriver artifact

No breaking changes.

### v2.4.1 — runtime artifact cleanup (2026-07-09)

Commit: `a5d3029`. Not officially tagged at the time.

Removes runtime artifacts (`upgrades/*.json`, `*.db`,
`*.jsonl`, `archive/*.json`) from git. Adds `upgrades/*`
catch-all to `.gitignore` (with `!.gitkeep` exception so
the directory stays tracked if needed). Files remain on
disk; only git tracking changed.

Verification: `git check-ignore` confirms runtime files
are ignored.

### v2.4.0 — unified CLI entry point (2026-07-08)

Commit: `2442d09`. Not officially tagged at the time.

Refactor merging v1.x's `run_1round.py` /
`run_3rounds_manual.py` / `run_stable.py` into a single
CLI entry. v1.x entry points remain in tree for
backward compatibility but are no longer the canonical
path.

### Earlier history

The following tags predate the re-open-source release and
remain on orphan commits in git history (preserved per
P-17, not reachable from `main`):

- `v1.6.0`, `v1.7.0`, `v1.7.1`, `v1.8.1-alpha`, `v1.8.2-alpha`
- `v2.0.0-critical-thinking-injection`, `v2.1.0-lifecycle-scripts`,
  `v2.2.0-session-final-2026-07-16`

For development-history context, see
[`docs/RETROSPECTIVE_2026-07-20.md`](docs/RETROSPECTIVE_2026-07-20.md).

## 2026-07-20 — major session

### Self-Upgrade Agent (SUA)

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
