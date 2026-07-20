# PRINCIPLES.md — Detail (L2)
Last P20-verified: 2026-07-14 (split from summary per R5+R6)

> L0: L2 detail for PRINCIPLES.md.  Per P11 摘要+引用,
> the summary file is the L0/L1 layer (≤ 7KB); this file
> is the L2 layer (per-P-n full text + boundary + 实操).
> Per R6, this detail file is referenced from the summary.

This file holds:
1. Meta principles段 (P19, P20, P20细则, P21, P24, P25, P26)
2. P-n vs M-* boundary段
3. L2 实操段

See `PRINCIPLES.md` for the summary.

---

## Meta principles

## Data Flow (P19)

**P19: Data flow observability**

When functions execute sequentially (A → B → C), persist A's
output to disk so B can read it without re-running A.  This:
  - Makes the data flow observable (`cat upgrades/foo.jsonl`)
  - Lets us replay a step without redoing prior steps
  - Lets us debug which input led to which output
  - Survives crashes (we can pick up where we left off)

Per user insight 2026-07-09: '如果有几个功能是顺序执行,
你可以先把前面的输出存下来, 作为下一个功能的输入'.

Concrete pattern in v3.0.1:
  - `read_papers()` -> `save_summaries()` (JSONL overwrite)
  - `read_summaries()` -> `select_best()` -> `save_decision()` (JSONL append)

Format: JSONL (one record per line).  Append-only for events,
single-snapshot for state.

**实操 (L2)**: per sequential function chain, write `save_X()` +
`read_X()` to `upgrades/X.jsonl`.  Per Test + Doc roots.

**Cross-ref to OPERATING_RULES.md M-task-summary
destroy contract**: P19 says "persist intermediate
state"; the destroy contract says "destroy
intermediate state after parent consumes it".
These are **complementary, not contradictory** —
P19 = add-phase (persist for replay/debug);
destroy contract = reduce-phase (clean up
consumed intermediates).  For batch / multi-leaf
tasks, see `docs/SUMMARY_LIFECYCLE.md` and the
"Child-summary destroy contract" sub-section in
`docs/OPERATING_RULES.md` M-task-summary段.

**Note (per commit 45, 2026-07-14)**: P19 moved here from above References section (was at line 113) for numerical order (P19 → P20 → P20.细则 → P21 → P22/P23 in PRINCIPLES_DETAIL.md → P24 → P25 → P26). Per user meta-rule "原则顺序不是一成不变的" (commit 42) + "自顶向下" (commit 44), P-n sections should be in numerical order within their containing段.
### P20. 渐进式披露 (progressive disclosure)

Documents should expose content in layers, each layer addressing a
different consumer question.  The default reader is an agent that
DOES NOT know the project's full context — it should be able to
read **only the layers it needs** and stop.

**实操 (L2)**: every new doc starts with L0 (1-line header) +
L1 (1-3 paragraphs).  L2 is the rest.  Per Doc root.

Three layers, in order of increasing cost:

| Layer | Question it answers | When to write | When the agent reads it |
|---|---|---|---|
| L0 — Pointer | "Where do I look?" | Always (header line) | Default (always read) |
| L1 — Summary | "What is this in 30 seconds?" | Always (1-3 paragraphs) | When L0 matches a need |
| L2 — Detail | "Give me the full story" | Optional, by file size | When L1 prompts a question |

Rules:
- A document with no L1 is **stealth** — only the agent that
  actively searches for it finds it.  Use for cross-project
  pointers (e.g. `docs/EXTENSIONS.md`) and ideas-not-yet-projects.
- A document's L1 must be readable in < 2 min (target ≤ 2KB).
  A document's L2 is for the consumer who already knows they
  need the full story (target ≤ 7KB).  If longer, the document
  is doing two jobs and should be split (P11 applies).
- L0 must be a single line (or short table cell).  No prose.
- P20 is recursive: this principle's own definition follows P20.
  L0 = the section header, L1 = this paragraph, L2 = the table.

Failure mode P20 guards against:
- An agent that "doesn't know there's an EXTENSIONS.md" loads
  every file referenced in INDEX.md.  That defeats the purpose
  of having a per-doc L0.
- An agent that "knows" a doc exists, reads all of it, including
  the parts not relevant to its task.  P20 layers let the agent
  stop after L0 or L1.

### P20.细则 (concrete rules — mechanical, not interpreted)

> P20 is the principle (abstract); this list is the binding
> contract.  Each rule is doc-level (mentally checked by future
> agents per P20 self-discipline).  Per the user's 2026-07-10
> framing: "原则 (P20) = 抽象类, 细则 = 具体实现".

| # | Rule | Failure mode it catches |
|---|---|---|
| R1 | `INDEX.md` must contain exactly two top-level sections after the intro: "Reading order for a new agent" and "Conditional loads".  No third category. | A new doc created and added to INDEX as "Helpful resources" or "Other" — bypasses the layer contract. |
| R2 | The "Reading order" section must number its links 1..N contiguously (no gaps, no duplicates). | Renumbering accident or skipped step that confuses the reader. |
| R3 | Every link in "Conditional loads" must have a `trigger:` annotation (one line, ≥ 5 words) describing when to read it. | Stealth doc with no clear "when to read" — defeats the purpose of being conditional. |
| R4 | `EXTENSIONS.md` must be ≤ 500 bytes AND contain only a table (no prose paragraphs before/after). | The pointer file becomes a narrative — now the agent reads it to "understand" instead of to "look up". |
| R5 | Every `docs/*.md` file ≤ 7KB is "self-contained summary".  Every file > 7KB must have a `*_DETAIL.md` companion whose name starts with the summary's filename minus `.md`. | A long doc that doesn't split — agent reads 12KB to get the 2KB it needed. |
| R6 | `_DETAIL.md` companions must be referenced (linked) from their summary file.  A `_DETAIL.md` with no inbound link is an "orphan detail" and must be deleted or referenced. | Dead file that future agents trip over. |
| R7 | Principles (P-n) are defined in EITHER `PRINCIPLES.md` (summary, brief) OR `PRINCIPLES_DETAIL.md` (full text), per the P11 split in commit `f753ec3`.  Any other `docs/*.md` may REFERENCE a P-n but must NOT redefine it.  Redefinition is a hard violation.  **Exception**: meta-rules (P22, P23) live in `_DETAIL.md` because their full text is in the same file as the P-n list. | Drift: parent says P7 is X, child says P7 is Y — system collapses. |
| R8 | Cross-project links use relative paths (`../other-project/...`).  Absolute paths or `https://` (except for external sources) are not allowed in `docs/`. | A doc breaks when the project is moved or cloned. |
| R9 | Every `docs/*.md` must begin with a single-line `L0:` frontmatter (≤ 120 chars) describing what the file is, in plain language.  This line is the L0 layer; the rest is L1+. | Doc with no L0 = not findable by the L0-only reader. |
| R10 | Every `docs/*.md` should end with a `Last P20-verified: YYYY-MM-DD` line, updated whenever the doc is meaningfully changed. | Stale doc — the L0/L1/L2 contract was true on date X but may have rotted. |
| R11 | Before commit, mentally check R1-R10 against any changed/new `docs/*.md` file. | New doc slipped in without verify, rotting the layer contract. |
| R12 | When `PRINCIPLES.md` is modified, every child project's `docs/PHILOSOPHY.md` (if it exists) must be re-synced in the SAME commit.  Per P21. | Parent-child drift: parent adds P22, child doesn't know, child cites "P1-P21" forever. |

How to use this list (per user 2026-07-10 'doc > script' 哲学):
1. Before any `docs/*.md` change, mentally check R1-R12.
2. No mechanical script — doc-level self-discipline.
3. If a rule is too strict in practice, update the rule — don't
   skip or weaken it.

### P21. Independent projects (cross-project boundaries)

When a project is referenced from another project's docs, the
referencing project should **link to a location, not duplicate
content**.  The referenced project should be **readable on its
own** (or have a single, clearly-stated "this is incomplete,
read the parent" disclaimer).

**实操 (L2)**: when referencing another project, link to a path,
not copy content.  Use EXTENSIONS.md as pointer file.  Per Doc
root.

Rules:
- Each project has its own `docs/` tree, its own PRINCIPLES,
  its own PHILOSOPHY (when relevant).  No "main project owns
  the truth" assumption.
- Cross-project links use relative paths (`../other-project/...`),
  not absolute paths or doc IDs.
- A project's PHILOSOPHY may inherit principles from another
  project **only if** the inherited text is reproduced in full
  (no "see P7 in parent" shortcuts).  Add a `synced from
  <parent> as of <date>` marker so drift is detectable.
- A principle that is "new" to a child project must be
  **proposed in the parent first**, then the child can reference
  it.  A child cannot mint new principles the parent doesn't have.

This is the formal statement of the philosophy behind
`docs/EXTENSIONS.md` (parent) and `docs/PHILOSOPHY.md` (children).

**P22 + P23 (meta-rules)** are listed in the L0 axiom table above
and the L1 children column.  See `PRINCIPLES_DETAIL.md` for full
text.  R12 in P20.细则 governs child-project sync.


### P25. Principle modification discipline (per user 2026-07-14, lifted from commit f6c796d by commit 33)

Modifying principles (P-n) or operating rules (M-*) is
**higher risk than editing other docs** because:

- All future agents will read and apply the modified rule.
- A wrong P-n propagates as silent system drift.
- A contradiction with existing rules breaks the
  M-self-audit 6-step checks.

**Required procedure** (per user "修改原则的时候需要
先阅读原则，这里的修改需要非常谨慎，这条感觉也需
要你记到原则里"):

1. **Read first**: load PRINCIPLES.md + the specific
   doc containing the M-* rule to be modified.  Read
   FULL text (not skim).  Same as M-must-read but for
   doc modification.

2. **Identify root axiom**: which of the 4 root axioms
   (奥卡姆 / Workflow / Test / Doc) does the change
   descend from?  Per the L0 table at the top of this
   doc.

3. **Verify no duplication**: check that no existing
   P-n or M-* covers the proposed change.  If similar
   rule exists, extend it; don't create parallel rules.

4. **Draft with all 4 elements**: trigger, action,
   anti-patterns, rationale.  Per P11 (摘要+引用) +
   M-self-application 4-level.

5. **Impact analysis** (per P-n vs M-* boundary 段
   below): which existing rules reference the
   modified rule?  Are cross-refs still valid?
   Is the new rule a P-n or M-* per the 3-case
   test (P-n about work / M-* about agent behavior /
   P-n about principles themselves)?

6. **Commit with detailed trace**: cite the P-n
   modified, cite the user message that motivated
   the change, list cross-refs to update.

7. **Post-modify re-apply new rules check**
   (per user meta-rule 2026-07-14, codified in
   commit 41): after the commit lands, re-apply
   **every newly-cited or newly-modified rule**
   from the batch to the **work-state of the
   batch itself** (not just to the future).
   This is the explicit self-referential step.

   Why: per user "修改原则后需要在新规则的情
   况下检查，这点你应该已经学到原则并且顺利
   运用".  Per P26 step 4: "Document the
   verification".  Without this step, a P-n
   modification can pass all 6 procedural steps
   yet still leave the work-state invisible to
   fresh agents.

   Mechanism (per P26 fresh-agent simulation):

   a. For each **newly added or modified P-n or
      M-*** in the batch: simulate a fresh agent
      running that rule against the work just
      committed.

   b. If simulation reveals a gap (e.g. cross-
      ref missing, doc not findable, test not
      passing) — fix in the same commit (or in
      a follow-up commit if gap requires new
      logical feature).

   c. If simulation passes — explicitly state
      "fresh-agent simulation passed" in the
      commit message body (this is P26 step 4
      "document the verification").

   This step is **distinct from** step 6
   ("commit with detailed trace"): step 6
   traces the **procedural correctness** of
   the modification; step 7 verifies the
   **work-state discoverability** after the
   modification.

**Anti-patterns**:

- Modify P-n without reading all existing P-n first.
- Create parallel rules instead of extending existing.
- Skip "root axiom" check — orphans the rule.
- Cite the change as "fix typo" or "minor update" —
  principle modification is always significant.
- **Skip step 7 (post-modify re-apply new rules
  check)**: the rule lands, but fresh agents
  can't discover the work.  This is the failure
  mode P26 was designed to catch.
- **Treat step 7 as optional**: it is not.
  P26 makes fresh-agent simulation **mandatory**
  at user-acceptance time.  Step 7 makes it
  mandatory at P-n modification time too.

**Self-application** (per M-self-application 4-level):

- This procedure applies to ITSELF: modifying THIS
  P25 requires reading it first + impact analysis +
  extended commit message.
- Per M-self-application 4-level level 2: rule-itself
  audit.  Future modification of this P25 must follow
  this same procedure.
- **Step 7 self-application**: when this段 is
  modified, the new step (step 7) must be applied
  to the work-state of THIS commit (i.e. extending
  P25 must include post-modify fresh-agent check
  of the P25 extension itself).
- **Bootstrap exception**: the original commit
  that introduced step 7 (commit 41) cannot have
  applied step 7 to itself before step 7 was
  codified.  The first application is implicit
  (the commit 41 message body documents the
  fresh-agent simulation run for the **previous**
  batch 37-40, plus for the P25 extension
  itself).

**实操 (L2)**: per principle / M-* rule modification,
follow the 6-step procedure in order.  Skip any step
only if explicitly justified in commit message.

**See also**:

- `docs/PRINCIPLES.md` "P-n vs M-* boundary"段 (the
  3-case classification test).
- `docs/OPERATING_RULES.md` "User-provided meta-rules
  → codify to doc"段 (related M-* rule about
  codification process).
- AGENTS.md "Read FULLY before modifying" pointer.

### P26. User-acceptance must include fresh-agent discoverability check (per user recurring meta-rule, 2026-07-14)

Per user 2026-07-14 recurring instruction (cited
"many times"): "在给用户验收这个agent规则的项目
的时候，需要判断新agent是否能获取它应该知道的
东西".

This rule formalizes M-self-audit step 2 ("new-agent
simulation") as a **first-class P-n**, because:
1. User-recurring check is more authoritative than
   agent-derived codification (per M_RULE_AUTHORING:
   user-provided rules bypass 3-condition gate).
2. The check applies regardless of agent (P-n test:
   "what should be true at handoff?") — not just
   "how should the agent behave" (M-* test).
3. Without explicit P-n, future agents may
   de-prioritize the check as "just an audit step".

**Trigger**: when delivering work to user for
acceptance (e.g. "all pass" / "ready for review" /
"this batch is done"), AND when ending a session
that may be resumed by a different agent.

**Action**: before claiming "ready for user acceptance":

1. **Self-pose the fresh-agent simulation**: pick a
   hypothetical agent that has zero context about
   this session (no memory, no recent commits read,
   no informal context).  What would they see?

2. **Check discoverability for each claim of
   completion**: for each "done" / "complete" /
   "fixed" / "added" assertion in the batch, can a
   fresh agent find the evidence?
   - Files: are they in expected locations?
   - Docs: are they up-to-date (R10)?
   - Cross-refs: do they resolve (R8)?
   - Tests: do they pass?

3. **Apply M-self-audit step 2 explicitly**: read
   `docs/M_SELF_AUDIT.md` step 2 and run the
   "could new agent" prompt.

4. **Document the verification**: in commit message
   body (parent verification) or session summary,
   state the fresh-agent simulation result.

**Anti-patterns**:

- Claim "all pass" or "ready for user" without
  fresh-agent simulation → silent gap on user
  side.
- Treat M-self-audit step 2 as optional
  ("just an audit step") → it is a P-n.
- Only simulate your own memory of the work
  ("I remember doing X, so X is done") → this is
  NOT fresh-agent simulation.
- Skip the check for "obvious" tasks → the
  obvious ones are where gaps hide.

**实操 (L2)**:

Per M-self-audit 6-step checklist, step 2 is
"new-agent simulation".  P26 makes this **mandatory**
at user-acceptance time, not optional.  Per R11
("before commit, mentally check R1-R10"), the
fresh-agent check is a meta-check on top of R11:
not "is the doc structured right?" but "could
a fresh agent find what they need to verify
the structure?".

**Self-application**:

P26 applies to itself: when modifying P26, the
fresh-agent check must pass (can a fresh agent
discover the new check?).  Per P25 6-step
procedure (the sibling meta-principle about
principle modification).

**See also**:

- `docs/M_SELF_AUDIT.md` step 2 (the operational
  checklist this rule formalizes).
- `docs/PRINCIPLES.md` "P-n vs M-* boundary"段
  (P25 explains why P26 is P-n not M-*).
- AGENTS.md "Hard rules"段 (P26 candidate for
  inclusion in top-6 invariant list, depending
  on user preference).
- `docs/OPERATING_RULES.md` "User-provided meta-
  rules → codify to doc"段 (the M-* rule about
  codification that this P-n extends).

---

### P27. Project self-organization (per c52 SELF_ORG + commit 73)

Per M_RULE_AUTHORING 3-condition gate + P25 6-step:

**Trigger** (when this principle should fire):
- After every commit (post-commit phase)
- After every P-n / M-* modification
- After every doc reorganization
- After every parent verification (SUMMARY_LIFECYCLE)
- When project state entropy is detected (per c44 audit finding)

**Action** (what the principle requires):

1. **Top-down check**: project docs should be in
   top-down + 分治 structure (per P20 progressive
   disclosure).
2. **类比 check**: are there 5 essence families
   in current docs? per P22 step 3.
3. **Ordering check**: are P-n in numerical order?
   per P14 doc ordering.
4. **Cross-ref check**: every new doc has parent
   (per P13).
5. **Cap check**: every doc ≤ 7KB / 300 lines
   (per R5/R8).
6. **L0 + R10 check**: L0 line present,
   Last P20-verified stamped (per R9/R10).
7. **Inductive check**: per P22 step 3, find
   commonalities; per P-n vs M-* boundary
   3-case test, decide where new content lives.

**Anti-patterns** (what this principle prevents):

- Wait for user prompting before organizing
- Ad-hoc reorganization (no plan)
- Add new structure without removing old
- Skip the "obviously broken" cases

**Rationale**: Per user meta-rule 2026-07-14:
"未来我不说的话, 这项目会自己整理原则和项目为
顺序规范吗?". Per P20 progressive disclosure
applied recursively (this principle self-applies
to project docs).

**Bootstrap exception**: This principle was
codified explicitly in commit 73, so prior
commits predating P27 did not auto-apply it.
Going forward, every commit should fire
P27 checks.

**实操 (L2)**: Per commit, agent should
self-apply 7-check (top-down + class + ordering
+ cross-ref + cap + L0+R10 + inductive) BEFORE
commit.  Per Doc + Workflow roots.

**Relationship**: P27 is **meta-principle**
spanning all 4 root axioms (奥卡姆 / Workflow /
Test / Doc).  Per P22 case 3 boundary test
(principle about principles), P27 is **P-n
meta, not M-***.

### Recursion (P28 candidate, per skill b502577 + user meta-rule 2026-07-15)

**Trigger** (when recursion should be invoked):
- When the project itself is the problem
- When P-n / M-* are being evaluated for self-application
- When the agent is reviewing its own behavior at a
  meta level
- When SUA's sibling project (agent-reflection-skill)
  receives a self-application request from the user

**Action** (what recursion requires):
1. Apply any P-n to the project itself (not just to
   artifacts the project produces).
2. Apply M-self-application to M-self-application
   (per M-self-application 4-level L4, the highest
   level is the agent's own behavior pattern).
3. Cross-reference sister project (skill) before
   making meta-decisions.
4. Limit recursion to depth 2 (primitives on self,
   not primitives on primitives on self).

**Why recursion is a candidate, not yet P28**:
- Per M_RULE_AUTHORING 3-condition gate, this is
  the **1st observed occurrence** of the recursion
  primitive in SUA (the previous 4 primitives were
  in skill).
- Per P25 6-step, lifting to P28 requires: read
  first + root axiom (cross-axiom, like P27) +
  no duplication (no existing P-n covers recursion)
  + 4 elements (above) + impact analysis +
  commit with trace + post-modify re-apply new
  rules check.
- This 段 **does the impact analysis** but stops
  short of full lift.  When the next 2+ SUA
  commits demonstrate recursion, then P28 lift.

**Cross-axiom position** (like P27): recursion
spans all 4 root axioms (it is the *act of applying
P-n to self*, not the *content* of any single P-n).
Per 信息拓扑 方案 C (c81): cross-axiom principles
live flat in PRINCIPLES.md (and detail in
PRINCIPLES_FULL.md), not in PRINCIPLES_DETAIL_DETAIL.md.

**Cross-ref** to skill b502577: 6th reasoning
primitive (recursion) in
`../agent-reflection-skill/docs/framework/analogy-and-induction.md`.
The skill commit also adds a "Self-application" 段
demonstrating recursion on the skill itself.

**P28 LIFT (per c96, 2026-07-15)**: per M_RULE_AUTHORING
3-condition gate + 你 directive "不用找我确认"
+ bootstrap exception:

- **Trigger**: when agent (or project) needs to
  apply P-n to itself.
- **Action**: explicit recursive loop with depth
  limit 2 (per M-n 12 boundary + memory 9 trap
  detection).
- **Why lift now**: c82 candidate + c92 M-n 12
  self-application + c93 L2 self-application +
  c94 MCP-first self-application + c95 autonomy
  boundary self-application = **5+ observed
  recursion demos** (3-condition gate met).
- **Apply to**: project self-organization, doc
  structure, P-n evaluation, M-rule refinement.

---



---

### P29 (agent 主动 reduce context, PROPOSED per c165)

> Per M_RULE_AUTHORING 3-condition gate + 你
> vision + P22 case-3 boundary test.

**Why P29 is proposed**:

P29 = "agent 主动 reduce context" (主动 reduces
context via 类比 + 节点 生命周期 + periodic
re-analysis + pace continuity + 3-layer).

**M_RULE_AUTHORING 3-condition gate**:

- **Condition 1 (3+ sites)**: ✅ PASS
  - c44 framework codify
  - c50 docs framework applied
  - c74 P27 cross-axiom
  - c115 整理 (整理 = analyze + induction + sort)
  - c122 M-n 23 re-analysis
  - c127 re-analysis 3 issues
  - c163 修订 L4 boundary explicit
  - **Total: 7+ sites**
- **Condition 2 (triggerable)**: ✅ PASS
  - Trigger: 整理 / re-analysis / pace-
    continuity / context-too-large
- **Condition 3 (5+ observed)**: ✅ PASS
  - All 7 sites above are observed cases

**Gate met: P29 PROPOSAL**.

**P-n vs M-* boundary (per c33 case 3 test)**:
P29 = case 3 (principle about how project
self-organizes).  Like P22 (stuck→plan), P25
(principle modification discipline), P26 (fresh-
agent check), P27 (project self-org), P28
(recursion to self).

**4-element 段**:

1. **Trigger**: when project 做了 很久 OR
   context exceeds threshold OR multiple
   complex cases accumulate.
2. **Action** (4 sub-steps per M-n 14 + M-n 18 +
   M-n 23 + M-n 24):
   - (1) Identify when context exceeds threshold
     (per M-n 23).
   - (2) Apply 类比 to find similar prior patterns
     (per M-n 14 entropy decrease).
   - (3) Compress to essence (per M-n 14
     compression + M-n 18 节点 生命周期).
   - (4) Destroy redundant summaries (per M-n 18
     destruction contract).
3. **Why**: makes agent 不 depend on external
   context management + applies 4 root axioms
   + extends P27 self-org + P28 recursion.
4. **Anti-patterns**:
   - **Don't** 主动 reduce without identifying
     threshold (premature compression).
   - **Don't** skip 类比 step (compress
     without finding pattern = loss of
     meaning).
   - **Don't** destroy before summarizing (per
     M-n 18 destruction contract).
   - **Don't** apply when context is small
     (奥卡姆 = simplicity, not brevity).

**Cross-axiom integration**:

P29 spans all 4 root axioms (per P22 case-3 +
extends P27 cross-axiom + P28 meta-meta):

| Root axiom | How P29 applies |
|---|---|
| Test | Re-analysis verifies context reduction |
| Doc | Context reduction keeps docs concise |
| Workflow | Pace-continuity avoids context overflow |
| 奥卡姆 | Reduces to essence (per M-n 14 entropy) |

**5 essence family placement**:

P29 belongs to **Meta-rules** family (like P22,
P23, P25, P26, P27, P28).  Essence: **process
for the process itself** (主动 reduce context
is process-for-process).

**Status**:

P29 is **proposed** (not yet fully working).
Per P25 6-step, lifting to full P29 requires:
- (1) Read existing P-n for overlap check ✅
  (no overlap with P27 or P28)
- (2) M_RULE_AUTHORING 3-condition gate ✅ (all 3
  pass)
- (3) Bootstrap exception for codification ✅
  (你 vision matches)
- (4) Documentation update (this 段) ✅
- (5) Commit message cites P-n (c165) ✅
- (6) Verify with P26 fresh-agent check
  (deferred to future commit)

**LIFT vs PROPOSED distinction**:

Per c96 P28 LIFT pattern, P29 is currently
**PROPOSED** (not fully LIFT).  Full LIFT
requires:
- 1+ future commit demonstrating P29 applied
  to a project self-organization task
- User confirmation (per 你 vision "自动
  allowed", this may be auto-LIFT in c167+)
- Verification per P26

**Cross-references**:

- SUA `docs/PRINCIPLES.md` P29 段 (per c165)
- SUA `docs/OPERATING_RULES.md` § M-n 14
  entropy dimension (c107)
- SUA `docs/OPERATING_RULES.md` § M-n 18
  recursive-summary-protocol (c111 + c114)
- SUA `docs/OPERATING_RULES.md` § M-n 23
  periodic-re-analysis (c127)
- SUA `docs/OPERATING_RULES.md` § M-n 24
  pace-continuity (c134)
- user message 2026-07-15 (3W1H + re-analysis +
  pace-continuity explicit directives)


**P29 LIFT (per c167, 2026-07-15)**: per M_RULE_AUTHORING
3-condition gate + 你 directive "不用找我确认"
+ bootstrap exception + P25 6-step step 6
verification:

- **Trigger**: when agent (or project) needs
  to actively reduce context.
- **Action**: explicit 4-sub-step loop with
  entropy awareness + 类比 + 节点 生命周期
  + periodic re-analysis + pace continuity:
  - (1) Identify when context exceeds threshold
    (per M-n 23 trigger: 10+ commits OR 1+ hour).
  - (2) Apply 类比 to find similar prior
    patterns (per M-n 14 entropy decrease +
    M-n 17 Path 2 inter-domain MCP search).
  - (3) Compress to essence (per M-n 14
    compression primitive + M-n 18 节点
    生命周期).
  - (4) Destroy redundant summaries (per
    M-n 18 destruction contract + sibling
    isolation).
- **Why lift now**: c165 itself demonstrates
  P29 applied (主动 reduced context by moving
  P29 detail to PRINCIPLES_FULL.md +
  slimming L0 line per P20 R9) +
  c137 (project 整洁) + c127 (re-analysis 3
  issues COMPLETE) + c115 (整理 = analyze +
  induction + sort) + c122 (M-n 23 re-
  analysis) + c134 (M-n 24 pace-continuity) =
  **6+ P29 demonstrations** (P25 6-step step
  6 verification met).
- **Apply to**: project self-organization,
  context reduction, doc structure, M-rule
  refinement, multi-commit batch work.

**Status update**: P29 PROPOSED → P29 LIFTED
(per c167).  P-n count: 24 → 25 working
(per c96 P28 LIFT pattern + c165 PROPOSAL
+ c167 LIFT verification).

---




### M-n 25 self-application: user message-pattern-recognition (per c183 + P28 recursion)

> L0: M-n 25 = "user message-pattern-recognition"
> (per user message 2026-07-15 explicit codify
> request).  This段 is M-n 25 applied to
> itself (per P28 recursion + M-self-
> application 4 levels).

**M-n 25 in 1 sentence**: When agent receives
a user message, parse the parts (directive /
真问题 / 真意 / 隐含 codify / 隐含
verification) and recognize which of 5
patterns (A-E) it matches.

**5 patterns A-E** (per c183 + c185 verification):

| Pattern | Structure | Example | Action |
|---|---|---|---|
| A | 2-3 parts + directive | "M-n 21 + top-down 默认" | M-n 12 + M-n 22 + direct M-rule |
| B | 3-4 parts + 真问题 | "M-n 22 + 自顶向下 + 继续" | M-n 22 + 答 真问题 |
| C | 5 parts + 真问题 + 隐含 codify | "5 directives + 学习思路 + 有没有学过" | codify new M-n |
| D | directive + 真问题 verify | "skill 跟 SUA 规范 + 做到了吗？" | M-n 21 答 + apply directive |
| E | implicit + 主动 | "按计划继续推进" | M-n 24 commit + continue |

**M-n 25 self-application (per P28 recursion +
M-self-application 4 levels)**:

- **L1 (object)**: M-n 25 rule = parse +
  recognize user message patterns.
- **L2 (rule)**: M-n 25 rule = M-self-
  application 4 levels applied to user message
  recognition.
- **L3 (memory)**: M-n 25 codified +
  persisted (entry 7 + M_TURN_PATTERN_
  RECOGNITION_DETAIL.md).
- **L4 (behavior)**: Future agents apply
  M-n 25 when receiving user message.

**Why M-n 25 is meta-meta-meta (per P28 +
P29 cross-axiom)**:

- P22 case 3: principle about principles
- P28 (recursion): applied to M-n 25 itself
- P29 (agent 主动 reduce context): M-n 25
  helps agent recognize user message patterns,
  which reduces clarification back-and-forth
  (= context reduction)
- M-n 25 IS M-self-application level 4
  applied to a specific domain (user message
  recognition)

**Cross-references**:

- SUA `docs/OPERATING_RULES.md` § M-turn-
  pattern-recognition段 (M-n 25 main 段)
- SUA `docs/M_TURN_PATTERN_RECOGNITION_DETAIL.md`
  (L2 companion)
- SUA `docs/OPERATING_RULES.md` § M-self-
  application 4 levels (c18 origin)
- SUA `docs/OPERATING_RULES.md` § M-n 12
  terminology-clarity (refine user message terms)
- SUA `docs/OPERATING_RULES.md` § M-n 14
  two-track-reasoning (类比 find similar
  user message vs 逻辑 parse 1 turn)
- SUA `docs/OPERATING_RULES.md` § M-n 22
  3W1H-think-first (for user message 真意)
- user message 2026-07-15 — origin (Pattern C)

**Status**: M-n 25 self-application段
codified (per c185 verification).  This
demonstrates P28 recursion: M-n 25 is
applied to itself in 4 levels (L1: parse
rule; L2: rule about rule; L3: memory of
rule; L4: behavior change due to rule).

---

## P-n vs M-* boundary (clarification per user 2026-07-14)

When proposing a new rule, decide which category it
belongs to BEFORE drafting (per M-intent-parsing
"过原则再判断"):

| Category | Question it answers | When to use | Examples |
|---|---|---|---|
| **P-n** (principle) | "What should be true?" | Atomic, stable, applies to all projects.  Cited in commit messages.  Needs `commit-msg` hook allow-list update. | P5 测通 / P7 奥卡姆 / P11 摘要+引用 / P14 docs current / P17 老实说 / P22 stuck→plan / P23 doc>script |
| **M-*** (workflow) | "How should the agent behave?" | Behavioral, agent-self-management, project-specific extensions of the meta-rules. | M-task-summary / M-must-read / M-context-snapshot / M-subtask-summary / M-intent-parsing / M-learn / M-add-then-reduce / M-self-audit / M-self-application |

**Decision rule** (per M-add-then-reduce signal-trigger):

- If the rule describes **agent behavior** (e.g.
  "before X, do Y" / "after W, capture Z") → **M-***.
- If the rule describes **principle that should
  hold regardless of agent** (e.g. "tests must
  pass before commit" / "奥卡姆 applies to
  docs") → **P-n**.

**Why this matters** (per user 2026-07-14):

M-self-audit 6-step audit checklist (e.g. step 6
"verify-before-edit") is a **workflow rule** because
it describes agent behavior, not a principle.  Putting
it in PRINCIPLES.md (as a new P25) would have been
**mis-categorization** — the rule is HOW to behave,
not WHAT should be true.  The actual fix: extend
M-self-audit step 6 (in `docs/M_SELF_AUDIT.md`),
not add a new P-n.

**3rd case — meta-principles about principles**
(per commit 33 follow-up audit, 2026-07-14):

The boundary table above has 2 cases.  A 3rd case
exists but was missed in the original (commit 5263030):

- **Meta-principle about principles**: a rule that
  describes **how principles themselves should
  behave**, not how the agent behaves.  This is
  different from a workflow rule (about agent
  behavior) and from a normal principle (about
  the work).

  Examples:
  - P22 (stuck→plan): meta-principle about how
    problem-solving should proceed.
  - P23 (doc>script with nuance): meta-principle
    about how tool choice should be made.
  - **P25 candidate**: "principle modification
    discipline" (committed as
    `docs/OPERATING_RULES.md` M-*段 in commit f6c796d,
    but **mis-classified** — should be P25 per
    this 3rd case).
  - **P26 candidate**: "user-acceptance must include
    fresh-agent discoverability check" (was
    M-self-audit step 2 in `docs/M_SELF_AUDIT.md`,
    user-recurring meta-rule, lifted by commit 39).
    Reason: the rule is **about what should be true
    at user-acceptance time** (not just "how the
    agent should behave when auditing") — i.e. it's
    a principle about the **handoff state**, not
    about audit procedure.

  **Test for meta-principle about principles**:
  Ask "does this rule describe how principles
  themselves should behave, OR how the agent should
  behave when modifying principles?"  If the former
  → P-n.  If the latter → M-*.

  **Implication for commit f6c796d**: the段
  "P-n / M-* modification discipline" should be
  in PRINCIPLES.md as P25, not in OPERATING_RULES.md
  as M-*.  See commit 33 follow-up.

**Anti-patterns**:

- **Don't promote a workflow rule to P-n** just
  because it's important.  Importance ≠ atomicity.
- **Don't demote a principle to M-*** just because
  it's hard to express as a workflow.  Principles
  can be meta (P22, P23 are meta-principles about
  process).
- **Don't add a new P-n to bypass M-self-audit's
  3-condition gate** for M-rules.  The gate exists
  precisely to keep workflow rules at the right
  level (per agent-onboarding skill
  `references/M_RULE_AUTHORING.md` 3-condition gate).

**See also**:

- `docs/OPERATING_RULES.md` — the 9 M-* rules and
  their canonical brief form.
- `docs/M_SELF_AUDIT.md` — audit checklist that
  checks both P-n adherence and M-* behavior.
- `docs/EXTENSIONS.md` X2 — cross-project M-rule
  source (where canonical 9 M-rules live).

---

## L2: 实操 (per P-n)

Each P-n has a 1-line "实操" describing how to actually follow the
principle.  See [PRINCIPLES_DETAIL.md](PRINCIPLES_DETAIL.md) for the
full list.  L2 is the third layer of progressive disclosure
(L0 = root axioms, L1 = principles, L2 = how to follow).

- Done tasks: [../../DONE.md](../../DONE.md)
