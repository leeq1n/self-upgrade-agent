# CHANGELOG — Self-Upgrade Agent (SUA)

> Canonical log of SUA releases and significant changes.
> Per P-14 docs current + P-17 no fabricate, this file documents
> the actual released state of the project on
> [github.com/leeq1n/self-upgrade-agent](https://github.com/leeq1n/self-upgrade-agent).

## 2026-07-31 — capability frameworks + protocol additions

### v2.21.3 — v2.20.1 + v2.21.2 CHANGELOG entries (2026-07-31)

Commit: `264932c`. Tag: `v2.21.3`.

**PATCH: CHANGELOG currency (top 5 tags).** Per self_health_check
真 finding: top 5 tags missing v2.20.1 + v2.21.2 entries
(P-14 docs-current).

Trade-off: docs-only release. Cost: 1 commit. Gain: all top 5
tags 真 in CHANGELOG.

Pre-task scan (M-n 34): per docs/AGENTS.md Read first item 3,
this commit was preceded by真 state check (self_health_check
FAIL, runtime audit PASS) and真 problem identification
(2 missing CHANGELOG entries).

### v2.21.2 — v2.21.1 CHANGELOG entry + tradeoff recap for v2.18.0/v2.19.0 (2026-07-31)

Commit: `73dbb4e`. Tag: `v2.21.2`.

**PATCH: CHANGELOG currency + tradeoff recap (no amend).**

Per user catch "重复任务" + self_health_check advisory:
- Added v2.21.1 entry (was missing in CHANGELOG)
- Added v2.21.0 entry (was missing in CHANGELOG)
- Tradeoff recap for v2.18.0 + v2.19.0 in CHANGELOG
  (no amend per 字面 trap 反复 risk)

Trade-off: docs-only release, no code changes. Cost: 1
commit spent on CHANGELOG hygiene. Gain: clean state for
"一遍过" claim.

Caveats: self_health_check.recent_commits_cite_tradeoff
advisory still flags v2.18.0/v2.19.0 in git history (per
self_health_check looks at git log not CHANGELOG). 0 BLOCKER
advisory only.

### v2.20.1 — final acceptance report (2026-07-31)

Commit: `3a57808`. Tag: `v2.20.1`.

**PATCH: project-level acceptance report.** Per user "至少一轮
验收" ask, this commit ships `docs/FINAL_ACCEPTANCE_2026-07-31.md`
documenting the verify round 1 results + 5 deferred issues.

Trade-off: docs-only release, no code changes.

### v2.21.1 — retroactive CHANGELOG entries + P-14 cleanup (2026-07-31)

Commit: `40a8aaa`. Tag: `v2.21.1`.

**PATCH: CHANGELOG currency + 3 new P-14 violations closed.**

Per runtime audit re-verify round (v2.21.0 ship):
- Top 5 tags missing `v2.21.1` entry in CHANGELOG (P-14 docs-current)
- Caught 3 new P-14 violations from my own v2.20.0/v2.21.0
  description (CHANGELOG L53, AGENTS_DETAIL.md L405 + L415)

Trade-off: descriptive commit messages that mentioned the fix
themselves contained the violation pattern (字面 trap 反复 =
字面 "我 fixed X" but the description contained X). Per P-17
no fabricate, all entries reflect真 git history.

Caveats: self_health_check.recent_commits_cite_tradeoff still
1 advisory failure (v2.18.0 + v2.19.0 commits lack tradeoff
language).留 amend cycle (per docs/OPERATING_RULES.md
wordy-trap defense rule).

### v2.21.0 — P-14 in core-layer + split OPERATING_RULES + 22 broken refs (2026-07-31)

Commit: `4bb81b6`. Tag: `v2.21.0`.

**MINOR: batch fix per user catch "重复任务" (re-verify round 2).**

Per user 2026-07-31 catch "既然没有一遍过，那就重复任务",
this commit batch-fixes 5 remaining真 issues found in v2.20.0
FINAL_ACCEPTANCE report:

- P-14 closure in core-layer: 3 new locations found
  (core-layer/README.md, governance-template.md, CHANGELOG.md)
- 22 broken markdown refs真 closed (per BROKEN_REFS_AUDIT):
  5 stub files created, 15 file refs updated, 3 anchors added
- OPERATING_RULES.md split: 109KB → 8.9KB main + 104KB _DETAIL
- validate_links.py 真 ship (per system hermes-verify- pattern)
- runtime audit C7 (self_health_check exit code) 真 fixed

Trade-off: 5 stub files真 ship with explicit "Status: Stub"
header (truthful per P-17, redirects to existing docs).

Caveats: self_health_check still has 2 advisory failures
(CHANGELOG currency + commit tradeoff). 0 BLOCKER.

### v2.20.0 — P-14 in hooks + 5 CHANGELOG entries (2026-07-31)

Commit: `5297fb8`. Tag: `v2.20.0`.

**PATCH: P-14 closure in core layer hooks + CHANGELOG currency.**

Per user final ask "最后确认一遍... clean-sua 都能一遍过" + runtime
audit 真 catches:

- `hooks/pre-commit` L4: removed `user message 2026-07-16` ref →
  `docs/OPERATING_RULES.md (修改时需要评估，修改后需要验收)`
- `hooks/pre-commit` L44: removed internal round-number ref →
  docs/OPERATING_RULES.md wordy-trap defense rule
- `CHANGELOG.md`: added 5 entries for v2.15.0-v2.19.0 (previously
  missing per self_health_check 真 finding)

Trade-off: retrospective CHANGELOG entries (5 commits already
shipped before their CHANGELOG entries existed). Per P-17 no
fabricate, all entries document actual git commits, not future plans.

Caveats (per ATDD Phase 4 = next verify round):
- 22 broken markdown refs in docs/ (per BROKEN_REFS_AUDIT)
- OPERATING_RULES.md 109KB (token budget)
- Commits v2.18.0 + v2.19.0 lack tradeoff language in body
  (would require amend to fix)
- self_health_check + runtime audit checker bugs (C7, C10-12)

### v2.19.0 — planning + acceptance frameworks (core layer) (2026-07-31)

Commit: `7c4734f`. Tag: `v2.19.0`.

**MINOR: capability frameworks shipped in core layer.**

Per user 2026-07-31 priority: 1) planning first, 2) acceptance next,
3) specific tasks last. Shipped two core-layer frameworks:

- `core-layer/PLANNING_FRAMEWORK.md` (5512 B) — codifies how to plan
  before doing (4-phase ATDD protocol, planning template, anti-patterns)
- `core-layer/ACCEPTANCE_FRAMEWORK.md` (6967 B) — codifies how to
  verify (criteria catalog, new tools, layer mapping)

Trade-off: doc-heavy release (no specific tasks this turn) per user
explicit priority ordering.

### v2.18.0 — PLAN_2026-07-30 (ATDD planning-first protocol) (2026-07-31)

Commit: `e195141`. Tag: `v2.18.0`.

**MINOR: project-layer plan doc.** Per user catch 字面 ship ≠ 真
ship 意图 (字面 trap 反复). Shipped `docs/PLANS/PLAN_2026-07-30.md`
(8246 B) with:
- ATDD 4-phase protocol (accept → plan → ship → verify)
- 真搜资料 evidence (TDD + LLM planning)
- 真承认之前 ship 多轮 redundant

Trade-off: more planning, less shipping — per user explicit "做好
规划再行动".

### v2.17.0 — ACCEPTANCE_PROTOCOL (verify/fix separation) (2026-07-31)

Commit: `a92fd35`. Tag: `v2.17.0`.

**MINOR: acceptance protocol.** Per user "一边验收一边改不对":
shipped `docs/ACCEPTANCE_PROTOCOL.md` (8087 B) defining:
- Phase 1 acceptance (verify only, NO fix)
- Phase 2 fix (after acceptance report)
- Phase 3 re-verify (new acceptance on fixed state)

Trade-off: more turns per change, but acceptance results become
stable + auditable.

### v2.16.0 — comprehensive fix + broken refs audit (2026-07-31)

Commit: `c0cb039`. Tag: `v2.16.0`.

**PATCH: docs/REFs cleanup + audit.** Per runtime audit found 22
broken markdown cross-refs (per 真 fresh hermes-verify-comprehensive
script). Shipped:

- `AGENTS.md` — broken `RETROSPECTIVE.md` ref → `RETROSPECTIVE_2026-07-20.md`
- `README.md` — added ## Uninstall section (A4 angle closure)
- `hooks/README.md` — updated for 3 hooks + Install/Uninstall +
  `.gitattributes` note
- `AGENTS_DETAIL.md` — fixed relative path for RETROSPECTIVE link
- `docs/BROKEN_REFS_AUDIT_2026-07-30.md` — documents remaining 21
  broken refs (TODO/DONE/DETAIL split deferred)

Trade-off: 5 file changes (~170 lines), audit exposed link-integrity
gap in existing audit infrastructure (self_health_check /
cross_repo_audit don't check link validity).

### v2.15.0 — project acceptance report (2026-07-31)

Commit: `b9c10b8`. Tag: `v2.15.0`.

**PATCH: project-level acceptance report.** Per user "做整个项目
验收" ask + system requirement for hermes-verify- prefix tempfiles:

- Ran comprehensive hermes-verify-project-acceptance.py (12 checks)
- Found 22 broken refs + OPERATING_RULES.md 109KB
- Shipped `docs/PROJECT_ACCEPTANCE_2026-07-30.md` (7953 B)

Trade-off: report lives in project layer, but per v2.17.0 +
v2.18.0 acceptance protocol, should migrate to user layer
(`~/.config/sua/acceptance/`) in future session.

## 2026-07-30 — core-layer self-contained

### v2.9.0 — core-layer AGENTS_CORE.md cleanup (2026-07-30)

Commit: `f3c9372`. Tag: `v2.9.0`.

**MINOR cleanup of core layer.** Per user explicit
authorization + M-n 15 multi-session rule (core layer
modification requires user turn 3+), this commit cleans
`core-layer/AGENTS_CORE.md` (the always-loaded L0 contract
that future agents see first).

**Removed**: 48 P-14 self-contained mandate violations
(19 strict + 29 loose):
- 12 per-user-message date references
- 7 per-c-number references
- 15 user-message ref variants (loose match)
- (full list in commit body)

**Replaced with**:
- "per cache optimization protocol (per docs/PRINCIPLES.md + docs/OPERATING_RULES.md)"
- "per 自主阅读学习 protocol + M_RULE_AUTHORING 3-condition gate"
- "per docs/OPERATING_RULES.md version notes" (was "per docs/OPERATING_RULES.md (P15 demote history)/c80/c78/c167")
- "per P7 Occam — avoid repetition in working memory" (was user-message quote)

**Preserved**: All M-n / P-n / R-n protocol content,
hooks references, hard rules, "What NOT TO DO" section,
commit message contract, "When in doubt" section.

**File size**: 9625B → 9146B (-479B).

**Risk**: Core-layer modification = per M-n 15, requires
multi-session + user explicit. This commit ships under
explicit user authorization.

### v2.8.0 — AGENTS.md P-14 cleanup (2026-07-30)

Commit: `b8ab638`. Tag: `v2.8.0`.

**PATCH cleanup of AGENTS.md (user layer).** Removed
P-14 self-contained mandate violations from the main
entry doc. Replaced 11 per-user-message + 27
AGENTS_DETAIL cross-refs + 2 RETROSPECTIVE refs with
generic protocol references.

**File size**: 7660B → 6686B (-974B).

This was the first round of P-14 cleanup; v2.9.0
completes the loop with core-layer modification
(authorized by user).

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
