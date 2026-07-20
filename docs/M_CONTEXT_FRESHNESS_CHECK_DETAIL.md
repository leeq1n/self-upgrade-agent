# M-context-freshness-check (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-context-
> freshness-check段.  Per P11 摘要+引用 + R6, this
> companion is required when the summary rule段
> describes a multi-path procedure.  Load when:
> agent considers modifying a frequently-modified
> doc OR entering a new domain.

## Why this L2 doc exists

The OPERATING_RULES.md § M-context-freshness-check
段 (c106, per user message "经常修改的文件 + 新的领域")
provides the 2-path action.  This L2 doc provides
decision tree, worked examples, and how both paths
compose.

## When to use which path (decision tree)

```
Q1: Is the doc modified 3+ times in last 10 commits?
├── Yes → Path 1 (intra-agent re-read)
└── No → Q2

Q2: Is the domain new (not searched in last 20 commits)?
├── Yes → Path 2 (inter-domain MCP search)
└── No → Don't apply (M-n 17 not needed)
```

## Path 1: Intra-agent context check

**When**: doc modified 3+ times recently.

**Action** (3 sub-steps):

1. **Re-read the doc**: full read, not skim.
2. **Confirm 印象**: check memory for current
   context.  If 印象 不清晰 → re-read thoroughly.
3. **Verify before modifying**: ensure modifications
   don't drift from current content.

**Output**: refreshed understanding + confirmation
that modifications align with current state.

**Worked example**: c112 (M-n 18 PLAN file) — before
creating `.hermes/plan/2026-07-15-replan.md`, agent
re-read PROJECT_STATE.md + OPERATING_RULES.md M-n
18段 + user message "写下来" directive.  This ensured
PLAN file aligned with current 3-project arch and
M-n 18 protocol.

## Path 2: Inter-domain search

**When**: entering a new domain (not searched in
last 20 commits).

**Action** (3 sub-steps):

1. **Select MCP**: sciverse (academic) / llm_wiki
   (project wiki) / zotero (literature) / mineru
   (PDF parsing) / chrome_devtools (web).
2. **Search for prior art**: avoid reinventing
   (per M-n 14 类比 = find similar pattern).
3. **Cite in _DETAIL companion**: per P11 + R6,
   cite 3+ sources when codifying new M-n or P-n.

**Output**: search results + cited prior art + 避免
重复.

**Worked example**: c94 (M-n 11 prior art) — before
codifying M-n 11 (sub-project), used sciverse to
search 3 papers (Li 2022 / Tsagkari 2020 / Sparrius
1980).  Cited in M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md.

## How both paths compose

Per M-n 16 (observe-think-execute 6-stage chain):

- **Path 1** applies to stage 1 (观察) + stage 6
  (修改、运行代码): re-read before + verify after.
- **Path 2** applies to stage 2 (思考-1 归纳) +
  stage 4 (思考-2 怎么行动): search for similar
  past patterns.

Both paths may apply to the same task (e.g., c94
applied Path 2 only; c109 applied Path 1 only; some
tasks apply both).

## When NOT to use (anti-patterns)

### Anti-pattern 1: Skip Path 1 (modify without re-read)

Modifying doc without re-read leads to drift.  Per
P14 docs stay current.

### Anti-pattern 2: Skip Path 2 (enter new domain without search)

Entering new domain without search leads to
reinventing.  Per P7 奥卡姆 + M-n 14 类比 = find
similar pattern.

### Anti-pattern 3: Over-rely on Path 1 (memory may be stale)

Memory may be stale.  Always verify (Path 1 sub-
step 3) before modifying.

### Anti-pattern 4: Over-rely on Path 2 (search results may be outdated)

Search results may be outdated (especially for fast-
moving fields).  Verify with multiple sources (per
M-n 14 逻辑 verification).

## Relationship to other M-rules + P-n

- **P14 docs stay current**: Path 1 enforces this.
- **M-n 11 (sub-project)**: when entering new domain,
  may spawn sub-project (Path 2 → M-n 11).
- **M-n 14 (two-track reasoning)**: Path 2 uses
  Track 1 (类比 to search results) + Track 2
  (verify with multiple sources).
- **M-n 15 (principle-reordering)**: Path 1
  complements M-n 15 sub-step 1 (重读).
- **M-n 16 (observe-think-execute)**: Path 1 applies
  to stage 1 (观察); Path 2 applies to stage 2
  (思考-1) when entering new domain.
- **M-n 18 (recursive-summary-protocol)**: Path 1
  may include sub-task summary before modifying.
- **P28 (recursion)**: this M-rule is recursive
  (apply to itself: re-read this M-rule when
  modifying).

## Self-application (per P28 recursion)

This L2 doc IS M-n 17 applied to itself:
- Before writing this L2 doc (c113), Path 1 applied:
  re-read OPERATING_RULES.md M-n 17段 + memory
  entry 7.
- M-n 17 is itself a "context freshness check" M-rule,
  so writing its L2 companion requires Path 1.

## Cross-references

- `OPERATING_RULES.md` § M-context-freshness-check —
  the L0/L1 段 (in SUA)
- `docs/PRINCIPLES.md` — P14 (Path 1 enforces this)
- `docs/M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md` —
  Path 2 worked example (c94)
- `OPERATING_RULES.md` § M-n 14/15/16/18 — related
- user message 2026-07-15 — origin

## Changelog

- c106 (OPERATING_RULES.md): add M-context-freshness-
  check段 (summary, 2 paths).
- c113 (this file): add L2 detail companion per
  P11 + R6.
