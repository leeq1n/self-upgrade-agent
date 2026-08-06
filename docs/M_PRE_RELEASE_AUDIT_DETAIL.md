> L0: M-n 36 L2 detail — 发布前 5 项检查 (release-audit).
# M-n 36: M-release-audit (per user message 2026-07-16 + retrospective)

> L2 detail.  Companion to `M_ACCEPTANCE_PROTOCOL_DETAIL.md`
> (M-n 29) + `M_PRE_TASK_SCAN_DETAIL.md` (M-n 34) +
> `M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md` (M-n 35).

## What is release-audit (here)

In SUA context: **release preparation** = the
sequence of operations that produces a `x.0.0` tag
for distribution (e.g., github push, zip
distribution, npm publish).  Release-audit = the
checks BEFORE tagging that catch "git history
clutter" / "unreleased fixes" / "missing changelog"
problems.

## Why needed

Per user message 2026-07-16 retrospective audit:

> "我需要将agent-reflection-skill推到github对吧？
> 当我推的时候，能只推最后一个版本（1.0.0版本），
> 避免github上项目commit混乱吗？"

Pre-1.0.0 development had 11 commits including:
- Q1 + Q2 fix iterations (commits a84a5ee, ee45e39)
- A M-n 29 acceptance FAIL fix (commit 2cc5329)
- Multiple cross-ref updates from sibling propagation

For a clean github push, these should be **collapsed**
to 1 commit (the release commit) + a CHANGELOG.md that
records the pre-release history.

This was **discovered reactively** (user message challenge
triggered the squash) — not proactively caught by
existing infrastructure.  Per user message 2026-07-16
"判断下问题在哪，怎么处理" — **M-n 36 codifies this
discovery into infrastructure**.

## When to apply

**Default-on** for:
- Tagging any `x.0.0` release (major version bump)
- Pre-push to github / git hosting
- Pre-publish to package manager (npm, PyPI, etc.)
- Pre-distribution of zip artifact

**Optional but recommended** for:
- Minor version tags (`x.y.0`)
- Patch version tags (`x.y.z`)

**Skip** for:
- Internal development tags (e.g., `dev/feature-x`)
- Pre-release tags (`x.0.0-rc.N`)

## The 5 release-audit checks

### Check 1: Commit history cleanliness

For x.0.0 release, the main branch should have:
- 1 initial commit (or N commits from previous x.0.0
  tag) — **NOT the full development history**
- 1 release commit (the vx.0.0 squashed state)

If main branch has more than N+1 commits where N is
expected, **suggest squash** before tagging.

### Check 2: Tag points at HEAD

`git rev-parse v1.0.0^{commit}` should equal
`git rev-parse HEAD`.  If tag is **behind** HEAD (e.g.,
.gitignore commit added after tag), **suggest
move tag forward**.

### Check 3: CHANGELOG.md exists + records pre-release history

If main branch has been **squashed**, the squash
commit's message + a `CHANGELOG.md` file should
document the pre-release commits.

### Check 4: Build artifact (zip) matches tag tree

If a distribution artifact exists (zip, tarball), it
should match `git ls-tree v1.0.0` content exactly.  Use
`git archive` to verify or regenerate.

### Check 5: Documentation cross-refs + integrity

- `AGENTS.md` should have release note (if applicable)
- `README.md` should have "what's in this version"段
- `VERIFICATION.md` should reference current version

## How to apply (mechanical layer)

Per user message 2026-07-16 codification pattern
(M-n 35 = critical-thinking, M-n 29 = 5-step):

1. **Script**: `agent-tools/scripts/release_audit.py`
   (currently being added per this rule)
2. **Hook**: `hooks/prepare-commit-msg` extended to
   detect "release" / "tag" / "v" keywords + auto-run
   audit
3. **AGENTS.md L0 surface**: "Read first" item 10 =
   this rule (release-audit)
4. **OPERATING_RULES.md L1 surface**: `### M-release-audit`
   section
5. **Cross-ref**: 4 sibling repos' VERIFICATION.md
   should reference this rule

## Integration with existing M-rules

- **M-n 34 (pre-task scan)**: when pre-task scan
  encounters "release / tag / version bump" task,
  should apply M-n 36 instead of generic pre-scan
- **M-n 29 (acceptance)**: when claiming "release
  DONE", must pass M-n 36 5 checks first
- **M-n 35 (critical-thinking)**: when designing release
  strategy, apply 4 critical-thinking primitives
  (质疑: what could be missing?  逆向: what if we
  don't tag?  预演失败: tag v1.0.0 release fails in
  30 days?  对立论证: strongest case for not tagging?)

## Anti-patterns

| Anti-pattern | Why bad | Better |
|---|---|---|
| Tag x.0.0 without audit | Re-occurrence of "github commit confusion" | Run M-n 36 5 checks first |
| Skip squash (push full history) | Github history cluttered | Squash + CHANGELOG.md |
| Tag at non-HEAD commit | Tag out of sync with state | Move tag forward + verify |
| Ship zip not matching tag | Distribution mismatch | `git archive` to regenerate |
| No CHANGELOG.md | Pre-release history lost | CHANGELOG.md with pre-release table |

## Sources cited (per P14 / P29)

- user message 2026-07-16 retrospective 4-FAIL (per
  M-n 32 Guardrail #4)
- npm publish convention (squash for first major)
- Linux kernel stable release pattern (clean
  branches per release)
- Chromium release branch pattern (orphan branch
  for release)
- GitHub PR squash-merge default

## P-n / M-n cited

P5 (tests pass — script pre-commit verify), P11
(摘要+引用 this file), P14 (docs stay current —
modify AGENTS.md in same batch), P17 (老实说 —
explicit gap from prior failure), P22 (when
stuck→plan), P25 (post-modify re-apply), P29
(recursion).

M-n 14 (two-track — constructive + adversarial),
M-n 18 (destruction — clean history), M-n 28
(plan-conditional), M-n 29 (acceptance-protocol
modified for release case), M-n 32
(self-learning-guardrail Guardrail #1 — pre-flight
verify), M-n 34 (pre-task-scan self-application),
M-n 35 (critical-thinking primitives applied
during codification).

## Where to commit (heuristic — per user message 2026-07-16)

**You turn 2026-07-16**: "下次你修改直接在
commit 比较细的项目上改, 大版本的项目尽量少
提交, 这样能减少工作量".

**Pattern**:

| Project type | Commit strategy |
|---|---|
| **Skill / fine-grained project** (e.g., agent-reflection-skill) | **Direct commit OK**.  Smaller scope, easier to verify, less coupling. |
| **Big project** (e.g., SUA, with hooks + scripts + multiple M-n) | **Minimize commits**.  Batch related changes into 1 commit.  Prefer doc-only changes for M-rule updates. |
| **Sibling project** (skill-incubator, KG) | **Cross-ref only** (don't duplicate content). |

**Why**:

1. **Big projects accumulate state** — each
   commit shifts HEAD, requiring tag/tag-pointer
   maintenance.
2. **Squash cycles multiply** — every commit
   added to a big project post-tag forces a
   re-squash for clean releases.
3. **Cross-repo sync** — content changes in
   big projects need propagation to N consumers.

**For release_audit.py specifically**:

- **SUA has reference impl** (`agent-tools/scripts/release_audit.py`)
  — canonical M-n 36 codification
- **Skill projects that ship releases copy the
  script** (per commit 55d2ef9 example) — that's
  fine, since each skill needs its own copy
- **Modifications**: when fixing release_audit.py
  bugs, fix in SUA first (canonical), then
  propagate to skill projects (less work
  cumulatively than re-deriving per-skill)

**Re-derivation test (per M-n 34 + M-n 35
critical-thinking #2 逆向)**: when designing
a new M-rule or script, ask:

> "Which project is the **canonical source of
> truth** for this content?"

If **SUA** (it's a meta-rule): SUA gets the
canonical impl + doc; consumers copy on
adoption.

If **skill** (it's domain-specific): skill
gets the impl directly; SUA only documents
the rule pattern.

**M-n 18 destruction extension**: this
heuristic = "minimize cross-project commits"
= M-n 18 applied at **organizational level**
(not just within-file destruction).

**Sources cited**:

- user message 2026-07-16 explicit heuristic
- Monorepo pattern (canonical + consumers)
- DNS hierarchy (root → TLD → domain)
- Single source of truth (M-n 27)
