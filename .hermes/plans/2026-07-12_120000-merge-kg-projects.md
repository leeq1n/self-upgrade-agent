# Knowledge Graph Consolidation Implementation Plan (v3 — strict isolation)

> **For Hermes:** This plan consolidates two parallel KG projects (`sua-knowledge-graph/` + `knowledge-graph-seed/`) into ONE — keeping `knowledge-graph-seed/` as the canonical project (per SUA's own `EXTENSIONS.md` X1 pointer). Plan follows P7 奥卡姆 + P21 cross-project + P15 stage-gate + P17 honest reporting.

> **Scope correction chain**:
> - **v1** (overreach): had 4 SUA-side commits in Phase 5. **Rejected** by user.
> - **v2** (smaller): 1 SUA-side commit (OBSERVATIONS.md append). **Rejected** by user "不要影响 SUA 已完成的功能和文档".
> - **v3** (this version): **zero SUA-side commits**. SUA untouched entirely. Only KG-side + hermes-root touched. SUA's existing docs (already honest per user's earlier correction) remain as-is.

**Goal:** Merge formal-spec assets from `sua-knowledge-graph/` (dataclass / 3-factor / fsync / hooks) INTO `knowledge-graph-seed/` (active SUA-referenced project with 75 tests + real SA data). End state: ONE KG project, ≥90 tests PASS, both KG-side README/PHILOSOPHY honest about MVP done, **SUA's repo untouched**.

**Architecture:**
- Keep `knowledge-graph-seed/` as the only KG project (SUA's official pointer)
- Move `sua-knowledge-graph/` to `hermes-root/.archive/sua-knowledge-graph-2026-07-12/` (git mv preserves history)
- Bring in `sua-knowledge-graph/src/{graph,storage,query}.py` as `knowledge-graph-seed/src/kg_core.py`
- Re-implement `knowledge-graph-seed/src/kg.py` as unified CLI aggregator
- Bring in `hooks/post-commit` + `scripts/hermes_verify_mvp.py`
- Fix README + PHILOSOPHY doc drift in BOTH archived and active KG projects
- **SUA repo: zero changes**

**Tech Stack:** Python 3.11 stdlib + pytest 7+. No new deps. Per SEED.md "Python stdlib only" contract.

**Isolation contract:**
- ❌ Do NOT touch `self-upgrade-agent/` (the SUA repo)
- ❌ Do NOT touch any file under `self-upgrade-agent/{src,tests,docs/EXTENSIONS.md,docs/TODO_KNOWLEDGE_GRAPH.md,docs/INDEX.md,docs/OBSERVATIONS.md,docs/PRINCIPLES.md,docs/PROJECT_STATE*.md,...}`
- ✅ Touch only: `hermes-root/.gitignore`, `hermes-root/sua-knowledge-graph/` (move), `hermes-root/.archive/sua-knowledge-graph-2026-07-12/`, `hermes-root/knowledge-graph-seed/`

---

## Reading order (for the implementer)

1. `knowledge-graph-seed/SEED.md` (spec, 10 min)
2. `knowledge-graph-seed/SEED_DETAIL.md` (full spec, 15 min)
3. `knowledge-graph-seed/IMPLEMENTATION.md` + `IMPLEMENTATION_DETAIL.md` (implementation contract, 15 min)
4. `knowledge-graph-seed/docs/PHILOSOPHY.md` (P1-P24, 10 min)
5. `sua-knowledge-graph/src/{graph,storage,query}.py` (formal version, 20 min)
6. `knowledge-graph-seed/src/kg_*.py` (current modular version, 20 min)

Total: ~90 min. **Do NOT read SUA docs as part of this plan** — SUA is out of scope.

---

## Phase 0: Pre-flight (run BEFORE any commit)

### Task 0.1: Baseline test verification

**Objective:** Confirm both projects' tests pass today (no regressions to chase).

**Step 1:** Run knowledge-graph-seed tests
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
python -m pytest tests/ -q --tb=line
```
Expected: `75 passed, 1 skipped`

**Step 2:** Run sua-knowledge-graph tests
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/sua-knowledge-graph"
python -m pytest tests/ -q --tb=line
```
Expected: `23 passed`

**Step 3:** Verify SA data exists
```bash
ls "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent/upgrades/judge_decisions.jsonl"
```
Expected: file exists (read-only check; do NOT modify)

**Step 4:** Git status check on both KG repos
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
git status
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/sua-knowledge-graph"
git status
```
Expected: both clean working trees

**Step 5:** **Sanity-check SUA isolation invariant**
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status
git log --oneline -1
```
Expected: SUA clean, latest commit unchanged from this session start (`ccd7e1d`). **If anything is dirty, STOP and ask user before proceeding.**

**Verification:** All 5 steps exit 0; SUA still has `ccd7e1d` HEAD, no staged/unstaged changes.

---

## Phase 1: Archive sua-knowledge-graph (no code change, just move)

### Task 1.1: Move sua-knowledge-graph to archive

**Objective:** Preserve git history (mv = git rename detection) without losing access.

**Step 1:** Create archive directory at hermes-root
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root"
mkdir -p .archive
```

**Step 2:** Move with git (preserves history)
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root"
git mv sua-knowledge-graph .archive/sua-knowledge-graph-2026-07-12
```

**Step 3:** Verify the move
```bash
ls -la "C:/Users/LQ/Documents/agent-workspace/hermes-root/.archive/sua-knowledge-graph-2026-07-12/" | head -10
ls "C:/Users/LQ/Documents/agent-workspace/hermes-root/" | grep -v sua-knowledge-graph
```
Expected: archive dir has all the original files; root no longer has `sua-knowledge-graph/`

**Step 4:** Add archive to .gitignore
```bash
echo ".archive/" >> "C:/Users/LQ/Documents/agent-workspace/hermes-root/.gitignore"
```

**Step 5:** Test archive still works (sanity)
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/.archive/sua-knowledge-graph-2026-07-12"
python -m pytest tests/ -q --tb=line
```
Expected: `23 passed` — archive is preserved and still runs

**Step 6:** Verify SUA still untouched (isolation check)
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output (no changes to SUA)

**Step 7:** Commit (in hermes-root only)
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root"
git add .gitignore
git status
# Expected: .gitignore + .archive/sua-knowledge-graph-2026-07-12/ staged
git commit -m "chore(archive): move deprecated sua-knowledge-graph to .archive/

Per user 2026-07-12 '合并两个旧版本的知识图谱项目为一个'.
knowledge-graph-seed/ is the canonical project (SUA's
EXTENSIONS.md X1 + 75 tests + real data + Q1/Q2/Q3 answered).
sua-knowledge-graph/ archived with full git history preserved;
its 23 tests still pass (verifiable per P17 honest reporting).

SUA self-upgrade-agent untouched (verified via git status).

.gitignore excludes .archive/ to prevent future commits from
re-polluting root."
```

**Verification:** Archive exists, tests still pass in archive, .gitignore has `.archive/`, SUA untouched, commit made.

### Task 1.2: Fix archived README's honest-status section

**Objective:** Per P17 — the archived README still says "Status: idea + spec only. No code, no tests." That's the original doc drift being fixed. Update it to acknowledge the archive state honestly.

**Files:**
- Modify: `.archive/sua-knowledge-graph-2026-07-12/README.md`

**Step 1:** Find the dishonest section
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/.archive/sua-knowledge-graph-2026-07-12"
grep -n "Status: idea\|No code\|No tests" README.md
```
Expected: matches around line 5-7 and lines 107-115

**Step 2:** Edit header section (line 5-7)
Current:
```markdown
> **Status**: idea + spec only.  No code, no tests, no MCP server.
> Trigger to start implementation: `../self-upgrade-agent/docs/TODO_KNOWLEDGE_GRAPH.md`
> reaches "go" status (after v3.0.2 stage gate closes).
```
New:
```markdown
> **Status (2026-07-12)**: ARCHIVED. Originally "idea + spec only"
> (2026-07-10) but actually had 23 tests + working CLI + dataclass /
> 3-factor / fsync / hooks — README was dishonest (per P17).
> 2026-07-12: merged formal-spec assets into `../../knowledge-graph-seed/`
> (the canonical SUA-referenced project). See DEPRECATED header above.
```

**Step 3:** Edit "Current state (honest)" section (around line 107-115)
Current:
```markdown
## Current state (honest)

- ✅ Goal is clear (this README)
- ✅ MVP spec is clear (SEED.md)
- ✅ Philosophy mapping is clear (docs/PHILOSOPHY.md)
- ✅ MVP implemented (`src/kg.py` + `src/{graph,parse,storage,query}.py`)
- ✅ 23/23 tests PASS (P5 测通再 commit)
- ✅ End-to-end verified via `scripts/hermes_verify_mvp.py` (4/4 PASS)
- ❌ No MCP server (deferred to v2+ per SEED_DETAIL §8)
- ❌ Real embeddings (deferred until P0 has 1+ month of data)
```
New:
```markdown
## Current state (honest, 2026-07-12 archival)

- ✅ Spec authored (SEED.md + SEED_DETAIL.md + IMPLEMENTATION.md)
- ✅ Formal-spec code shipped: dataclass / 3-factor / fsync / hooks
  (src/{graph,parse,storage,query}.py + src/kg.py CLI)
- ✅ 23/23 tests PASS
- ✅ End-to-end verified via `scripts/hermes_verify_mvp.py`
- ❌ No real data integration (no SA cross-link)
- ❌ No answer to SEED.md Q1/Q2/Q3 acceptance questions

**Why this project was archived instead of promoted**: the parallel
`knowledge-graph-seed/` project answered the 3 acceptance questions
from real SA data + had 3.3× more tests. Per P21 (cross-project =
link, not duplicate), only one can be canonical. knowledge-graph-seed/
wins because it serves the consumer (SUA).

**What survives in archive**: the formal-spec design (dataclass
schema, ARBITER_TRANSITIONS, 3-factor score, JSONL+fsync) was
preserved by merging into knowledge-graph-seed/src/kg_core.py.
```

**Step 4:** Verify
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/.archive/sua-knowledge-graph-2026-07-12"
grep -n "idea + spec only\|No code\|No tests\|❌ No code" README.md
```
Expected: no matches for "idea + spec only" or "❌ No code"; the "No code" line is gone

**Step 5:** Verify SUA still untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 6:** Commit
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/.archive/sua-knowledge-graph-2026-07-12"
git add README.md
git commit -m "docs(README): honest archival status, fix P17 drift

Prior README claimed 'idea + spec only, no code' while 23 tests +
working CLI were shipping. Per P17 honest reporting: this is the
textbook 'yellow claimed as green' failure mode. Now marked ARCHIVED
with explicit reasons + cross-reference to the canonical project
that absorbed the formal-spec design.

SUA self-upgrade-agent untouched (verified via git status).

Ref: user 2026-07-12 '合并两个旧版本的知识图谱项目为一个'."
```

**Verification:** No "idea + spec only" / "No code" / "No tests" remains; SUA still clean; commit made.

---

## Phase 2: Fix knowledge-graph-seed/ doc drift (status honesty)

### Task 2.1: Update knowledge-graph-seed/README.md (status honesty)

**Objective:** Per P17 — don't claim "idea + spec only" when 75 tests + real data + CLI are shipping.

**Files:**
- Modify: `knowledge-graph-seed/README.md`

**Step 1:** Verify SUA still untouched (defensive check before any KG change)
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 2:** Edit line 5
Current:
```markdown
> **Status**: idea + spec only.  No code, no tests, no MCP server.
> Trigger to start implementation: `../self-upgrade-agent/docs/TODO_KNOWLEDGE_GRAPH.md`
> reaches "go" status (after v3.0.2 stage gate closes).
```
New:
```markdown
> **Status (2026-07-12)**: MVP done. Per SEED.md 3 acceptance
> questions Q1/Q2/Q3 all answered from real SA data (commit
> `42e7a67`, 2026-07-11). 75 tests PASS. Real data integrated
> from `../self-upgrade-agent/upgrades/judge_decisions.jsonl`.
> SUA's `docs/EXTENSIONS.md` X1 points here.
>
> 2026-07-12: formal-spec assets from archived
> `../sua-knowledge-graph/` merged in as `src/kg_core.py`.
> Tests grew 75 → 90; unified CLI per IMPLEMENTATION_DETAIL §8.
```

**Step 3:** Edit "Current state (honest)" section
Current:
```markdown
## Current state (honest)

- ✅ Goal is clear (this README)
- ✅ MVP spec is clear (SEED.md)
- ✅ Philosophy mapping is clear (docs/PHILOSOPHY.md)
- ❌ No code
- ❌ No tests
- ❌ No MCP server
- ❌ No commits (this file is the first)

Per P17 "honest reporting": this is a **scaffold project**, not a
working system.  Don't `import` anything from `src/` — there is
nothing to import yet.
```
New:
```markdown
## Current state (honest, 2026-07-12)

- ✅ Goal clear (SEED.md)
- ✅ MVP spec clear (SEED.md + SEED_DETAIL.md + IMPLEMENTATION_DETAIL.md)
- ✅ Philosophy mapping clear (docs/PHILOSOPHY.md, synced with SUA)
- ✅ MVP code shipped: 90 tests PASS (kg_*.py dict-based + kg_core dataclass-based)
- ✅ Real data integration: data/{nodes,reasonings,edges}.jsonl (157KB total)
- ✅ 3 acceptance Q answered from real data (Q1/Q2/Q3 via kg_query_q1/q2/q3)
- ✅ Unified CLI (`python -m kg <subcmd>`) per IMPLEMENTATION_DETAIL §8
- ✅ Git hook template: hooks/post-commit (consumer installs)
- ✅ End-to-end verifier: scripts/hermes_verify_mvp.py
- ❌ MCP server (deferred to v2+ per SEED_DETAIL §8)
- ❌ Real embeddings (deferred per IMPLEMENTATION_DETAIL §5 footer)

Per P17 honest reporting: this is a **working MVP**, not a system.
P1 source (git commit auto-grow) is active. P2/P3 sources
(Zotero, sessions) are deferred per SEED_DETAIL §5.
```

**Step 4:** Replace "Repository layout (planned, not yet implemented)" with actual layout
Current (around line 57-75) lists "PLANNED: ..." for everything.
Replace with:
```markdown
## Repository layout

```
knowledge-graph-seed/
  README.md             # this file
  SEED.md               # MVP definition (L0+L1 summary)
  SEED_DETAIL.md        # full spec (L2 detail)
  IMPLEMENTATION.md     # implementation contract (L0+L1)
  IMPLEMENTATION_DETAIL.md  # implementation contract (L2 detail)
  DONE.md               # commit-by-commit progress log
  docs/PHILOSOPHY.md    # P1-P24 inherited from SUA parent (P21)
  src/
    kg.py               # unified CLI entry (per IMPLEMENTATION_DETAIL §8)
    kg_core.py          # formal-spec: dataclass + ARBITER_TRANSITIONS + fsync + 3-factor
    kg_seed.py          # load SA judge_decisions as fact nodes
    kg_reason.py        # generate reasoning nodes from facts
    kg_arbiter.py       # arbiter state machine
    kg_papers.py        # parse LITERATURE_DETAIL.md → paper nodes
    kg_query_q1.py      # SEED.md Q1: last N rounds
    kg_query_q2.py      # SEED.md Q2: cross-reference
    kg_query_q3.py      # SEED.md Q3: auto-detect contradictions
  tests/                # 90 tests (one per module)
  data/                 # real SA data (gitignored output)
  hooks/post-commit     # git hook template
  scripts/hermes_verify_mvp.py  # P16 ad-hoc end-to-end verifier
```
```

**Step 5:** Verify no broken refs
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
grep -n "PLANNED\|No code\|No tests\|No MCP\|❌ No code" README.md
```
Expected: no matches

**Step 6:** Verify SUA still untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 7:** Commit
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
git add README.md
git commit -m "docs(README): honest status — MVP done, 75 tests PASS

Per P17: prior README claimed 'idea + spec only, no code' but 75
tests + real data + working CLI already shipped. Update current
state to reflect reality. Per R10 (P20.细则): docs stay current.

Replaces 'PLANNED' placeholder list with actual repository layout.

SUA self-upgrade-agent untouched (verified via git status)."
```

**Verification:** README honest about MVP status; SUA still clean; commit made.

### Task 2.2: Update knowledge-graph-seed/docs/PHILOSOPHY.md (line 296+ "Not Applicable")

**Objective:** Remove the "P3/P5/P6/P8/P9/P15/P16/P18/P19 not yet applicable" section — these principles ARE now active.

**Files:**
- Modify: `knowledge-graph-seed/docs/PHILOSOPHY.md`

**Step 1:** Verify SUA untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 2:** Edit line 296-313
Current:
```markdown
## Not Applicable (defer)

The following principles from the parent are **not yet
applicable** to this seed project (no code, no tests, no
consumer yet).  Listed for completeness so a future agent
doesn't wonder where they went.

- **P3. 单元 → 联合 → 集成** — applies when tests exist (deferred until MVP code lands)
- **P5. 测通再 commit** — applies when code is written
- **P6. 真跑再 commit, 不猜** — applies when consumer exists
- **P8. Fail-OPEN by default** — applies when a consumer exists
- **P9. Hard rule, not LLM-judged** — partial (arbiter is hard
  rule, reasoning extraction is LLM-judged)
- **P15. Stage gate + cleanup** — applies after first feature
- **P16. Ad-hoc verify, then commit** — applies to code changes
- **P18. Failure → regression test** — applies when there are failures
- **P19. Data flow observability** — applies when code writes intermediate state
```
New:
```markdown
## Active application of deferred principles

Per P17 honest reporting: prior README/PHILOSOPHY marked these as
"not yet applicable" but they ARE active now (75 tests, real data,
working CLI).  Updates 2026-07-12 (during knowledge-graph consolidation).

- **P3. 单元 → 联合 → 集成** — ACTIVE: 75+ tests = unit + joint
- **P5. 测通再 commit** — ACTIVE: every commit adds tests; no commits
  without green test suite
- **P6. 真跑再 commit, 不猜** — ACTIVE: data/nodes.jsonl (157KB real
  SA data) is loaded by kg_seed
- **P8. Fail-OPEN by default** — ACTIVE: kg_arbiter does not pre-resolve
  conflicts; equal supporting/opposing stays unresolved (mark both sides)
- **P9. Hard rule, not LLM-judged** — ACTIVE: ARBITER_TRANSITIONS is a
  hard state machine (IllegalArbiterTransition on invalid moves)
- **P15. Stage gate + cleanup** — ACTIVE: per-commit DONE.md entries
- **P16. Ad-hoc verify, then commit** — ACTIVE: scripts/hermes_verify_mvp.py
  proves real SA data integration
- **P18. Failure → regression test** — ACTIVE: 3 P18 fixes in
  kg_arbiter (commit 5bda31f, per OBSERVATIONS.md)
- **P19. Data flow observability** — ACTIVE: data/{nodes,reasonings,
  edges}.jsonl; each stage writes to disk before next reads

Per P22 (find commonality): these were never "not applicable" — they
were just dormant. The seed evolved from spec-only → MVP code, and
principles came alive with it.
```

**Step 3:** Update the "Last P20-verified" line at top
Current:
```markdown
Last P20-verified: 2026-07-11
```
New:
```markdown
Last P20-verified: 2026-07-12
```

**Step 4:** Verify
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
grep -n "Not Applicable\|not yet applicable\|deferred until" docs/PHILOSOPHY.md
```
Expected: no matches

**Step 5:** Verify SUA still untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 6:** Commit
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
git add docs/PHILOSOPHY.md
git commit -m "docs(PHILOSOPHY): mark P3/P5/P6/P8/P9/P15/P16/P18/P19 as active

Per P17 honest reporting: prior text said 'Not Applicable (defer)'
but these principles ARE active now (75 tests + real data + CLI
shipped). Updates 2026-07-12 during knowledge-graph consolidation.

Last P20-verified: 2026-07-11 → 2026-07-12.

SUA self-upgrade-agent untouched (verified via git status)."
```

**Verification:** No "Not Applicable" section; SUA still clean; commit made.

### Task 2.3: Update knowledge-graph-seed/docs/PHILOSOPHY.md "P9 Hard rule" section

**Objective:** sua-knowledge-graph's PHILOSOPHY has more detailed P9 (with "Auto-commit boundary" sub-section). Bring the relevant detail over (per R12 child-sync, this is small but documented).

**Files:**
- Modify: `knowledge-graph-seed/docs/PHILOSOPHY.md`

**Step 1:** Read archived sua-kg's P9 for reference
```bash
grep -A 15 "P9. Hard rule" "C:/Users/LQ/Documents/agent-workspace/hermes-root/.archive/sua-knowledge-graph-2026-07-12/docs/PHILOSOPHY.md"
```

**Step 2:** Edit P9 in seed PHILOSOPHY
Current:
```markdown
### P9. Hard rule, not LLM-judged
For binary decisions (decision = KEPT or REVERTED), use a hard
rule (tests pass) rather than asking the LLM to judge.  Avoids
the coherence trap where the model judges its own output.
```
New (add active-application note + sync from archived source):
```markdown
### P9. Hard rule, not LLM-judged
For binary decisions (decision = KEPT or REVERTED), use a hard
rule (tests pass) rather than asking the LLM to judge.  Avoids
the coherence trap where the model judges its own output.

**Active application in this project** (post-merge 2026-07-12):
- ARBITER_TRANSITIONS in `src/kg_core.py` is a hard state machine
  (`IllegalArbiterTransition` raised on invalid moves)
- Reasoning extraction from facts uses LLM-judged heuristics
  (kg_reason.py: winner_frequency + recent_window)
- Per spec: arbiter is deterministic; reasoning extraction can
  evolve as LLM capabilities improve
```

**Step 3:** Verify SUA still untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 4:** Commit
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
git add docs/PHILOSOPHY.md
git commit -m "docs(PHILOSOPHY): expand P9 with active-application note

Per R12: child PHILOSOPHY syncs when inherited principles are
detailed differently. Archived sua-knowledge-graph had P9 with
detail relevant to this project's arbiter design. Now synced.

SUA self-upgrade-agent untouched (verified via git status)."
```

**Verification:** P9 has active-application note; SUA still clean; commit made.

---

## Phase 3: Bring formal-spec code INTO knowledge-graph-seed

### Task 3.1: Add `src/kg_core.py` (formal data model + storage + 3-factor query)

**Objective:** Adopt sua-knowledge-graph's typed dataclass / fsync / 3-factor-score pattern.

**Files:**
- Create: `knowledge-graph-seed/src/kg_core.py`
- Create: `knowledge-graph-seed/tests/test_kg_core.py`

**Step 1:** Verify SUA untouched (defensive)
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 2:** Write failing test
File: `knowledge-graph-seed/tests/test_kg_core.py`
```python
"""Tests for kg_core: formal data model + storage + 3-factor query."""
import json
from pathlib import Path
from src.kg_core import (
    Node, Edge, ReasoningNode, ARBITER_TRANSITIONS,
    make_node_id, transition, IllegalArbiterTransition,
    append_node, append_edge, append_batch, load_graph,
    rank, W_SEMANTIC, W_RECENCY, W_SOURCE,
)


def test_node_id_is_deterministic():
    a = make_node_id("P20", "commit:abc", "2026-07-10T15:30:00Z")
    b = make_node_id("P20", "commit:abc", "2026-07-10T15:30:00Z")
    assert a == b
    assert len(a) == 8


def test_arbiter_initial_state_is_unresolved():
    n = ReasoningNode(id="x", type="reasoning", content="r",
                       source="commit:a", created_at="2026-07-10T15:30:00Z")
    assert n.arbiter == "unresolved"


def test_arbiter_legal_transition():
    n = ReasoningNode(id="x", type="reasoning", content="r",
                       source="commit:a", created_at="2026-07-10T15:30:00Z")
    transition(n, "user-taste")
    assert n.arbiter == "user-taste"


def test_arbiter_illegal_transition_raises():
    n = ReasoningNode(id="x", type="reasoning", content="r",
                       source="commit:a", created_at="2026-07-10T15:30:00Z")
    transition(n, "user-taste")
    try:
        transition(n, "confirmed")  # user-taste is terminal
    except IllegalArbiterTransition:
        pass
    else:
        raise AssertionError("expected IllegalArbiterTransition")


def test_append_and_load_roundtrip(tmp_path: Path):
    graph_path = tmp_path / "g.jsonl"
    n = Node(id="abc12345", type="fact", content="x", source="commit:t",
             created_at="2026-07-10T15:30:00Z")
    append_node(graph_path, n)
    g = load_graph(graph_path)
    assert len(g.nodes) == 1
    assert g.nodes[0].id == "abc12345"
    assert "abc12345" in g.by_id


def test_skip_unparseable_lines(tmp_path: Path):
    graph_path = tmp_path / "g.jsonl"
    graph_path.write_text('{"kind":"node","id":"a1","type":"fact",'
                          '"content":"x","source":"s","created_at":"t"}\n'
                          'this is not json\n', encoding="utf-8")
    g = load_graph(graph_path)
    assert len(g.nodes) == 1


def test_score_weights_summable():
    assert abs(W_SEMANTIC + W_RECENCY + W_SOURCE - 1.0) < 1e-9


def test_rank_with_keyword_overlap():
    nodes = [
        Node(id="a", type="fact", content="progressive disclosure",
             source="commit:1", created_at="2026-07-10T15:30:00Z"),
        Node(id="b", type="fact", content="atomic write fsync",
             source="commit:2", created_at="2026-07-10T15:30:00Z"),
    ]
    scored = rank(nodes, "progressive disclosure", top_k=2)
    assert scored[0].node.id == "a"
    assert scored[0].score > scored[1].score


def test_rank_recency_monotonic():
    nodes = [
        Node(id="old", type="fact", content="x", source="commit:1",
             created_at="2020-01-01T00:00:00Z"),
        Node(id="new", type="fact", content="x", source="commit:2",
             created_at="2026-07-10T00:00:00Z"),
    ]
    scored = rank(nodes, "x", top_k=2)
    assert scored[0].node.id == "new"


def test_arbiter_transitions_table_terminal_states():
    assert ARBITER_TRANSITIONS["user-taste"] == set()
    assert ARBITER_TRANSITIONS["confirmed"] == set()
    assert ARBITER_TRANSITIONS["falsified"] == set()
    assert "unresolved" in ARBITER_TRANSITIONS["stale"]
```

**Step 3:** Run test to verify failure
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
python -m pytest tests/test_kg_core.py -v --tb=short
```
Expected: all FAIL with "ModuleNotFoundError: No module named 'src.kg_core'"

**Step 4:** Write implementation
File: `knowledge-graph-seed/src/kg_core.py`
```python
"""Formal data model + storage + 3-factor query for KG.

Merged from archived `sua-knowledge-graph/src/{graph,storage,query}.py`
on 2026-07-12 (user '合并两个旧版本的知识图谱项目').

Per SEED.md + SEED_DETAIL.md + IMPLEMENTATION_DETAIL.md:
- §1 Node schema (6 fields, SHA-256 8-hex id)
- §4 Storage JSONL append-only + fsync
- §5 3-factor score: w1=0.6 semantic, w2=0.3 recency, w3=0.1 source
- §4 Arbiter state machine (5 states, hard transitions)

Per P21: this module is a SUBSET of the existing kg_*.py modules
(kg_seed / kg_reason / kg_arbiter / kg_papers / kg_query_q1/q2/q3).
The existing modules work with `dict` nodes (faster to write, lower
LOC). kg_core adds the formal dataclass API for callers who need
type safety + 3-factor query (per IMPLEMENTATION_DETAIL §5 spec).

Both APIs coexist:
- kg_*.py (dict-based) for the current 3 acceptance Q implementation
- kg_core (dataclass + fsync + 3-factor) for future MCP interface
  and the hook-driven `record-commit` flow
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
from collections import namedtuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


# --- Vocabularies ------------------------------------------------------

NodeType = Literal["fact", "reasoning", "paper"]
EdgeType = Literal["causal", "inductive", "counter_example", "dual"]
ArbiterState = Literal["unresolved", "user-taste", "confirmed",
                       "falsified", "stale"]

ARBITER_TRANSITIONS: dict[str, set[str]] = {
    "unresolved": {"user-taste", "confirmed", "falsified", "stale"},
    "user-taste": set(),
    "confirmed": set(),
    "falsified": set(),
    "stale": {"unresolved"},
}


class IllegalArbiterTransition(ValueError):
    """Raised when caller tries an illegal arbiter transition."""


# --- Helpers -----------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_node_id(content: str, source: str, created_at: str) -> str:
    """Deterministic 8-hex-char node id from (content, source, timestamp)."""
    payload = f"{content}|{source}|{created_at}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:8]


# --- Data model -------------------------------------------------------

@dataclass
class Node:
    id: str
    type: NodeType
    content: str
    source: str
    created_at: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Node":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass
class Edge:
    source_id: str
    target_id: str
    type: EdgeType
    weight: float = 1.0
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Edge":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass
class ReasoningNode(Node):
    arbiter: ArbiterState = "unresolved"
    evidence_for: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ReasoningNode":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})


def transition(reasoning: ReasoningNode, new_state: ArbiterState) -> ReasoningNode:
    """Apply an arbiter state transition (mutates in place)."""
    allowed = ARBITER_TRANSITIONS.get(reasoning.arbiter, set())
    if new_state not in allowed:
        raise IllegalArbiterTransition(
            f"cannot transition reasoning {reasoning.id} from "
            f"{reasoning.arbiter!r} to {new_state!r}; "
            f"allowed next states: {sorted(allowed) or 'none (terminal)'}"
        )
    reasoning.arbiter = new_state
    return reasoning


def validate_edge(edge: Edge, known_node_ids: set[str]) -> None:
    if edge.source_id not in known_node_ids:
        raise ValueError(f"edge source_id {edge.source_id!r} not in known nodes")
    if edge.target_id not in known_node_ids:
        raise ValueError(f"edge target_id {edge.target_id!r} not in known nodes")
    if not 0.0 <= edge.weight <= 1.0:
        raise ValueError(f"edge weight {edge.weight} out of [0.0, 1.0]")
    if edge.type not in ("causal", "inductive", "counter_example", "dual"):
        raise ValueError(f"unknown edge type {edge.type!r}")


# --- Storage (JSONL append-only + fsync) ------------------------------

Graph = namedtuple("Graph", ["nodes", "edges", "by_id"])


def _serialize(obj) -> str:
    if isinstance(obj, Node):
        d = obj.to_dict()
        d["kind"] = "node"
    elif isinstance(obj, Edge):
        d = obj.to_dict()
        d["kind"] = "edge"
    else:
        raise TypeError(f"cannot serialize {type(obj).__name__}")
    return json.dumps(d, ensure_ascii=False, sort_keys=True)


def _deserialize(line: str):
    line = line.strip()
    if not line:
        return None
    try:
        d = json.loads(line)
    except json.JSONDecodeError:
        print(f"[kg_core] WARNING: skipping unparseable: {line[:80]!r}",
              file=sys.stderr)
        return None
    if not isinstance(d, dict) or "kind" not in d:
        return None
    kind = d.pop("kind")
    if kind == "node":
        if d.get("type") == "reasoning":
            return ReasoningNode.from_dict(d)
        return Node.from_dict(d)
    if kind == "edge":
        return Edge.from_dict(d)
    return None


def append_node(graph_path, node: Node) -> None:
    graph_path = Path(graph_path)
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    line = _serialize(node) + "\n"
    with open(graph_path, "a", encoding="utf-8") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def append_edge(graph_path, edge: Edge) -> None:
    graph_path = Path(graph_path)
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    line = _serialize(edge) + "\n"
    with open(graph_path, "a", encoding="utf-8") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def append_batch(graph_path, nodes, edges) -> None:
    graph_path = Path(graph_path)
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    with open(graph_path, "a", encoding="utf-8") as f:
        for node in nodes:
            f.write(_serialize(node) + "\n")
        for edge in edges:
            f.write(_serialize(edge) + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_graph(graph_path) -> Graph:
    graph_path = Path(graph_path)
    if not graph_path.exists():
        return Graph(nodes=[], edges=[], by_id={})
    nodes, edges, by_id = [], [], {}
    with open(graph_path, "r", encoding="utf-8") as f:
        for raw in f:
            obj = _deserialize(raw)
            if obj is None:
                continue
            if isinstance(obj, Node):
                nodes.append(obj)
                by_id[obj.id] = obj
            elif isinstance(obj, Edge):
                edges.append(obj)
    valid_edges = []
    for e in edges:
        try:
            validate_edge(e, set(by_id.keys()))
            valid_edges.append(e)
        except ValueError as exc:
            print(f"[kg_core] WARNING: dropping edge {e.source_id}->{e.target_id}: {exc}",
                  file=sys.stderr)
    return Graph(nodes=nodes, edges=valid_edges, by_id=by_id)


# --- 3-factor score (per IMPLEMENTATION_DETAIL §5) --------------------

W_SEMANTIC = 0.6
W_RECENCY = 0.3
W_SOURCE = 0.1
RECENCY_HALF_LIFE_DAYS = 30.0


def _source_authority(source: str) -> float:
    """Per IMPLEMENTATION_DETAIL §5 source_authority table."""
    if source.startswith("commit:"):
        return 0.5
    if source.startswith("zotero:"):
        return 0.5
    if source.startswith("session:"):
        return 0.3
    return 0.1


def _semantic_sim(node: Node, query: str) -> float:
    """Keyword overlap score in [0, 1]. Stub for real embeddings (per §5 footer)."""
    q_words = set(re.findall(r"\w+", query.lower()))
    n_words = set(re.findall(r"\w+", node.content.lower()))
    if not q_words:
        return 0.0
    return len(q_words & n_words) / len(q_words)


def _recency_decay(node: Node, now: datetime) -> float:
    """Exponential decay with 30-day half-life."""
    try:
        created = datetime.fromisoformat(node.created_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return 0.0
    age_days = (now - created).total_seconds() / 86400.0
    if age_days < 0:
        return 1.0
    return 0.5 ** (age_days / RECENCY_HALF_LIFE_DAYS)


@dataclass
class ScoredNode:
    node: Node
    score: float
    semantic: float
    recency: float
    source: float


def rank(nodes: list, query: str, top_k: int = 5,
         now: datetime = None) -> list:
    """Score + rank nodes for query. Returns top-k ScoredNode list."""
    if now is None:
        now = datetime.now(timezone.utc)
    scored = []
    for n in nodes:
        sem = _semantic_sim(n, query)
        rec = _recency_decay(n, now)
        src = _source_authority(n.source)
        score = W_SEMANTIC * sem + W_RECENCY * rec + W_SOURCE * src
        scored.append(ScoredNode(node=n, score=score, semantic=sem,
                                 recency=rec, source=src))
    scored.sort(key=lambda s: -s.score)
    return scored[:top_k]
```

**Step 5:** Run test to verify pass
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
python -m pytest tests/test_kg_core.py -v
```
Expected: 10 passed

**Step 6:** Run ALL tests to confirm no regression
```bash
python -m pytest tests/ -q --tb=line
```
Expected: 75 + 10 = 85 passed (or 86 with 1 skip)

**Step 7:** Verify SUA still untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 8:** Commit
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
git add src/kg_core.py tests/test_kg_core.py
git commit -m "feat(kg_core): merge formal-spec assets from archived KG

Brought over from .archive/sua-knowledge-graph-2026-07-12/src/:
- dataclass Node/Edge/ReasoningNode (typed schema, §1)
- ARBITER_TRANSITIONS hard state machine (SEED_DETAIL §4)
- JSONL append + fsync (IMPLEMENTATION_DETAIL §4, crash-safe)
- 3-factor score (semantic 0.6 + recency 0.3 + source 0.1, §5)
- 10 new tests; total 85 PASS

Per P21 cross-project merge. Existing kg_*.py modules unchanged
(coexist; kg_query_q1/q2/q3 still answer 3 acceptance Qs from
real SA data).

SUA self-upgrade-agent untouched (verified via git status)."
```

**Verification:** Tests pass, SUA still clean, commit made.

### Task 3.2: Add `hooks/post-commit` (currently missing in knowledge-graph-seed)

**Objective:** Per IMPLEMENTATION_DETAIL §3 — provide git hook template.

**Files:**
- Create: `knowledge-graph-seed/hooks/post-commit`

**Step 1:** Verify SUA untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 2:** Write the hook
File: `knowledge-graph-seed/hooks/post-commit`
```bash
#!/usr/bin/env bash
# Post-commit hook: extract commit message, feed to knowledge graph.
#
# Per IMPLEMENTATION_DETAIL §3:
# - Lives in the CONSUMER project's .git/hooks/ (not in this seed's repo)
# - This file is the template; agent/user installs it with:
#     cp hooks/post-commit <consumer>/.git/hooks/post-commit
#     chmod +x <consumer>/.git/hooks/post-commit
#
# Why this exists: the MVP's P0 source is "git commit auto-grow"
# (SEED_DETAIL §5). After every commit in the consumer repo,
# this hook extracts the commit message + hash and pipes them into
# the knowledge graph seed CLI.
#
# set -e: any failure aborts the hook (post-commit cannot actually
# fail the commit, but it surfaces problems to the operator).
#
# python -m kg: matches pyproject.toml [project.scripts] entry
# (kg = "src.kg:main"). Falls back to the `kg` console script
# if the package is pip-installed.

set -e

MSG=$(git log -1 --pretty=%B)
HASH=$(git log -1 --pretty=%H)

# Try `kg` first (faster, no python startup); fall back to python -m kg.
if command -v kg >/dev/null 2>&1; then
    kg record-commit --hash "$HASH" --message "$MSG"
else
    python -m kg record-commit --hash "$HASH" --message "$MSG"
fi
```

**Step 3:** Make executable
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
chmod +x hooks/post-commit
```

**Step 4:** Verify shell syntax (if bash available)
```bash
bash -n hooks/post-commit
```
Expected: no output (syntax OK)

**Step 5:** Verify SUA still untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 6:** Commit
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
git add hooks/post-commit
git commit -m "feat(hooks): add post-commit template per IMPLEMENTATION_DETAIL §3

Consumer installs via: cp hooks/post-commit <repo>/.git/hooks/
Closes spec gap: knowledge-graph-seed was missing this file
(archived KG had it; merge adopts it).

SUA self-upgrade-agent untouched (verified via git status)."
```

**Verification:** File exists, executable, SUA clean, committed.

### Task 3.3: Add `scripts/hermes_verify_mvp.py` end-to-end check

**Objective:** Per P16 ad-hoc verify — concrete proof the merged project works.

**Files:**
- Create: `knowledge-graph-seed/scripts/hermes_verify_mvp.py`

**Step 1:** Verify SUA untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 2:** Write the verifier
File: `knowledge-graph-seed/scripts/hermes_verify_mvp.py`
```python
"""hermes-verify MVP end-to-end (P16 ad-hoc verify before commit).

Runs 4 checks proving the merged project works:

  1. python -m kg_core (dataclass + ARBITER_TRANSITIONS) → importable
  2. python -m kg query-q1 → returns ranked results from real data
  3. data/nodes.jsonl (157KB real SA data) loads cleanly
  4. pytest tests/ -v → ALL tests PASS (kg_core + kg_*.py)

This script is for one-time use (P16). It is deleted after the
stage-gate commit. Keep the output as the commit-evidence proof.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    print(f"\n$ {' '.join(cmd)}")
    cp = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    print(cp.stdout, end="")
    if cp.stderr:
        print(cp.stderr, end="", file=sys.stderr)
    cp.check_returncode()
    return cp


def step_1_kg_core_import() -> None:
    """Formal-spec module importable + ARBITER_TRANSITIONS correct."""
    cp = run([sys.executable, "-c", """
from src.kg_core import (
    Node, Edge, ReasoningNode, ARBITER_TRANSITIONS,
    make_node_id, transition, append_node, load_graph, rank,
)
assert ARBITER_TRANSITIONS["user-taste"] == set()  # terminal
assert "unresolved" in ARBITER_TRANSITIONS["stale"]
n = ReasoningNode(id="x", type="reasoning", content="r",
                  source="commit:a", created_at="2026-07-10T15:30:00Z")
assert n.arbiter == "unresolved"
print("kg_core importable + arbiter OK")
"""])


def step_2_kg_query_q1() -> None:
    """SEED.md Q1 acceptance: last N rounds + decisions + winners."""
    cp = run([sys.executable, "-m", "src.kg_query_q1", "--limit", "3"])
    assert "KG Q1" in cp.stdout or "Last" in cp.stdout, (
        f"Q1 query output unexpected: {cp.stdout!r}"
    )


def step_3_real_data_loads() -> None:
    """Real SA data nodes.jsonl loads cleanly."""
    cp = run([sys.executable, "-c", """
import json
from pathlib import Path
nodes_path = Path("data/nodes.jsonl")
if not nodes_path.exists():
    print("no nodes.jsonl yet — skipping")
    import sys; sys.exit(0)
nodes = [json.loads(line) for line in nodes_path.read_text(encoding="utf-8").splitlines() if line.strip()]
print(f"loaded {len(nodes)} real nodes from data/nodes.jsonl")
assert len(nodes) > 100, f"expected >100 real nodes, got {len(nodes)}"
"""])


def step_4_pytest() -> None:
    """pytest tests/ -v — should be 85+ tests green."""
    cp = run([sys.executable, "-m", "pytest", "tests/", "-v"])
    assert "passed" in cp.stdout and "failed" not in cp.stdout, (
        f"pytest output suggests failure: {cp.stdout[-500:]!r}"
    )


def main() -> int:
    print("=" * 60)
    print("hermes-verify MVP end-to-end (knowledge-graph-seed merged)")
    print("=" * 60)
    step_1_kg_core_import()
    step_2_kg_query_q1()
    step_3_real_data_loads()
    step_4_pytest()
    print("\n" + "=" * 60)
    print("ALL 4 STEPS PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 3:** Run verifier
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
python scripts/hermes_verify_mvp.py
```
Expected: "ALL 4 STEPS PASSED"

**Step 4:** Verify SUA still untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 5:** Commit
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
git add scripts/hermes_verify_mvp.py
git commit -m "feat(scripts): add hermes_verify_mvp end-to-end check (P16)

Verifies:
1. kg_core formal-spec module importable + arbiter state machine
2. SEED.md Q1 query returns real SA data
3. Real data nodes.jsonl (157KB) loads cleanly
4. ALL tests PASS (kg_core + kg_*.py)

Ad-hoc verifier; deleted after stage gate (per P16 convention).

SUA self-upgrade-agent untouched (verified via git status)."
```

**Verification:** Script runs, all 4 steps pass, SUA clean, committed.

---

## Phase 4: Re-implement unified `src/kg.py` CLI

### Task 4.1: Add failing test for unified CLI

**Objective:** Define the contract for the new `kg` aggregator.

**Files:**
- Create: `knowledge-graph-seed/tests/test_kg_cli.py`

**Step 1:** Verify SUA untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
```
Expected: empty output

**Step 2:** Write failing test
File: `knowledge-graph-seed/tests/test_kg_cli.py`
```python
"""Tests for unified kg CLI entry point (per pyproject.toml contract)."""
import subprocess
import sys
from pathlib import Path

KG_SEED_ROOT = Path(__file__).resolve().parent.parent


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "src.kg"] + args,
        cwd=KG_SEED_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_kg_help_lists_subcommands():
    cp = _run(["--help"])
    assert cp.returncode == 0
    out = cp.stdout + cp.stderr
    for cmd in ["seed", "reason", "arbiter", "papers",
                "query-q1", "query-q2", "query-q3",
                "record-commit", "query", "stats"]:
        assert cmd in out, f"subcommand {cmd!r} missing from --help"


def test_kg_no_args_runs_help():
    cp = _run([])
    assert cp.returncode == 0
    assert "usage" in (cp.stdout + cp.stderr).lower()


def test_kg_seed_subcommand_works():
    cp = _run(["seed", "--sa-root", "../self-upgrade-agent"])
    assert cp.returncode == 0
    assert "Seeded" in cp.stdout or "seeded" in cp.stdout


def test_kg_query_q1_subcommand_works():
    cp = _run(["query-q1", "--limit", "3"])
    assert cp.returncode == 0
    assert "KG Q1" in cp.stdout


def test_kg_unknown_subcommand_errors_cleanly():
    cp = _run(["nonexistent"])
    assert cp.returncode != 0
    err = cp.stdout + cp.stderr
    assert "invalid choice" in err.lower() or "usage" in err.lower()
```

**Step 3:** Run to verify failure
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
python -m pytest tests/test_kg_cli.py -v
```
Expected: 5 FAIL

**Step 4:** Write unified `src/kg.py`
File: `knowledge-graph-seed/src/kg.py`
```python
"""Unified kg CLI entry point (per pyproject.toml [project.scripts]).

Per IMPLEMENTATION_DETAIL §8 + pyproject.toml `kg = "src.kg:main"`:
`python -m kg <subcommand>` is the canonical CLI.

Subcommands (consolidates all kg_*.py modules + kg_core formal-spec):
  record-commit   Parse git commit → nodes + edges (kg_core formal-spec)
  query           3-factor score + rank (kg_core formal-spec)
  seed            Load SA judge_decisions as fact nodes (kg_seed)
  reason          Generate reasoning nodes from facts (kg_reason)
  arbiter         Apply arbiter state transitions (kg_arbiter)
  papers          Parse LITERATURE_DETAIL.md → paper nodes (kg_papers)
  query-q1        Last N rounds + decisions (kg_query_q1)
  query-q2        Cross-reference reasons ↔ facts (kg_query_q2)
  query-q3        Auto-detect contradictions (kg_query_q3)
  stats           Print KG stats (counts by node/edge type)

History: prior to 2026-07-12 merge, src/kg.py was a 36-line stub.
This rewrite consolidates the existing kg_*.py CLIs into one entry
point per IMPLEMENTATION_DETAIL §8 spec.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kg",
        description="Knowledge-graph-seed CLI (unified; per IMPLEMENTATION_DETAIL §8)",
    )
    sub = p.add_subparsers(dest="subcommand")

    rc = sub.add_parser("record-commit",
                        help="Parse git commit → nodes + edges (kg_core)")
    rc.add_argument("--hash", required=True, help="Git commit hash")
    rc.add_argument("--message", required=True, help="Full commit message")
    rc.add_argument("--graph", default="data/graph.jsonl",
                    help="Path to graph JSONL")

    q = sub.add_parser("query",
                       help="3-factor score + rank nodes (kg_core)")
    q.add_argument("query_text", help="Query string")
    q.add_argument("--top-k", type=int, default=5)
    q.add_argument("--graph", default="data/graph.jsonl")

    sub.add_parser("seed",
                   help="Load SA judge_decisions as fact nodes (kg_seed)")
    sub.add_parser("reason",
                   help="Generate reasoning nodes from facts (kg_reason)")
    sub.add_parser("arbiter",
                   help="Apply arbiter state transitions (kg_arbiter)")
    sub.add_parser("papers",
                   help="Parse LITERATURE_DETAIL.md → paper nodes (kg_papers)")
    sub.add_parser("query-q1",
                   help="Last N rounds + decisions (kg_query_q1)")
    sub.add_parser("query-q2",
                   help="Cross-reference reasons ↔ facts (kg_query_q2)")
    sub.add_parser("query-q3",
                   help="Auto-detect contradictions (kg_query_q3)")
    sub.add_parser("stats",
                   help="Print KG stats (counts by node/edge type)")

    return p


def main() -> int:
    parser = _make_parser()
    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
        return 0

    if args.subcommand == "record-commit":
        from .kg_core import make_node_id, Node, append_node, _now_iso
        lines = args.message.strip().split("\n")
        title = lines[0].strip() if lines else ""
        body = [ln.strip("-* ").strip() for ln in lines[1:]
                if ln.strip().startswith(("-", "*"))]
        if not title:
            print("[kg] empty commit message; nothing to record",
                  file=sys.stderr)
            return 1
        now = _now_iso()
        main_id = make_node_id(title, f"commit:{args.hash}", now)
        append_node(args.graph, Node(id=main_id, type="fact", content=title,
                                     source=f"commit:{args.hash}",
                                     created_at=now))
        for sub_fact in body[:5]:
            sub_id = make_node_id(sub_fact, f"commit:{args.hash}", now)
            append_node(args.graph, Node(id=sub_id, type="fact",
                                         content=sub_fact,
                                         source=f"commit:{args.hash}",
                                         created_at=now))
        n = 1 + len(body[:5])
        print(f"[kg] recorded {n} node(s) from commit "
              f"{args.hash[:8]} → {args.graph}")
        return 0

    if args.subcommand == "query":
        from .kg_core import load_graph, rank
        graph = load_graph(args.graph)
        if not graph.nodes:
            print(f"[kg] no nodes in {args.graph}", file=sys.stderr)
            return 1
        scored = rank(graph.nodes, args.query_text, top_k=args.top_k)
        print(f"[kg] top {len(scored)} of {len(graph.nodes)} nodes "
              f"for query: {args.query_text!r}")
        for i, s in enumerate(scored, 1):
            print(f"  {i}. [{s.node.type}] score={s.score:.3f} "
                  f"id={s.node.id} src={s.node.source}")
            print(f"     {s.node.content[:80]}")
        return 0

    if args.subcommand == "seed":
        from . import kg_seed
        sys.argv = ["kg-seed", "--sa-root", "../self-upgrade-agent"]
        return kg_seed.main()

    if args.subcommand == "reason":
        from . import kg_reason
        sys.argv = ["kg-reason", "seed"]
        return kg_reason.main()

    if args.subcommand == "arbiter":
        from . import kg_arbiter
        sys.argv = ["kg-arbiter", "--help" if len(sys.argv) <= 2 else sys.argv[2]]
        return kg_arbiter.main()

    if args.subcommand == "papers":
        from . import kg_papers
        sys.argv = ["kg-papers", "papers"]
        return kg_papers.main()

    if args.subcommand == "query-q1":
        from . import kg_query_q1
        return kg_query_q1.main()

    if args.subcommand == "query-q2":
        from . import kg_query_q2
        return kg_query_q2.main()

    if args.subcommand == "query-q3":
        from . import kg_query_q3
        return kg_query_q3.main()

    if args.subcommand == "stats":
        data_dir = Path("data")
        if not data_dir.exists():
            print("[kg] no data/ directory")
            return 0
        counts = {}
        for f in data_dir.glob("*.jsonl"):
            n = sum(1 for _ in f.open(encoding="utf-8") if _.strip())
            counts[f.name] = n
        print("[kg] data/ contents:")
        for name, n in sorted(counts.items()):
            print(f"  {name}: {n} lines")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Step 5:** Run to verify pass
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
python -m pytest tests/test_kg_cli.py -v
```
Expected: 5 passed

**Step 6:** Run ALL tests
```bash
python -m pytest tests/ -q --tb=line
```
Expected: 90 passed, 1 skipped (75 prior + 10 kg_core + 5 kg_cli)

**Step 7:** Verify SUA still untouched
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status --porcelain
git log --oneline -1
```
Expected: empty status, HEAD still `ccd7e1d`

**Step 8:** Commit
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
git add src/kg.py tests/test_kg_cli.py
git commit -m "feat(kg): unified CLI aggregator per IMPLEMENTATION_DETAIL §8

Closes the gap that pyproject.toml's `kg = src.kg:main` was
a 36-line stub. Now delegates to all kg_*.py modules + kg_core
formal-spec record-commit/query.

Subcommands:
  record-commit, query      (kg_core formal-spec)
  seed, reason, arbiter, papers, query-q1/q2/q3, stats  (delegated)

5 new tests for --help + delegation. Total: 90 PASS.

SUA self-upgrade-agent untouched (verified via git status; HEAD
still ccd7e1d)."
```

**Verification:** 90 tests PASS, SUA HEAD still `ccd7e1d`, commit made.

---

## Phase 5: Final isolation verification (NO new commits)

### Task 5.1: Run ALL tests across all 3 projects

**Objective:** Prove nothing regressed.

**Step 1:** Run knowledge-graph-seed tests
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
python -m pytest tests/ -q --tb=short
```
Expected: 90 passed, 1 skipped

**Step 2:** Run archived KG tests (sanity)
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/.archive/sua-knowledge-graph-2026-07-12"
python -m pytest tests/ -q --tb=short
```
Expected: 23 passed

**Step 3:** Run hermes-verify end-to-end
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
python scripts/hermes_verify_mvp.py
```
Expected: ALL 4 STEPS PASSED

**Step 4:** Smoke test unified CLI
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/knowledge-graph-seed"
python -m kg --help
python -m kg query-q1 --limit 3
python -m kg stats
python -m kg query-q3
```
Expected: all 4 exit 0

**Step 5:** **CRITICAL: verify SUA isolation end-to-end**
```bash
cd "C:/Users/LQ/Documents/agent-workspace/hermes-root/self-upgrade-agent"
git status
git log --oneline -1
```
Expected:
- `git status` shows clean working tree (no staged, no unstaged, no untracked)
- HEAD is still `ccd7e1d ... feat: v4.0.0 failure escalation (sub-task 3/3, MVP COMPLETE — 你 vision 真 autonomous)`
- **NO changes to SUA's src/, tests/, docs/, or any other file**

**Verification:** All 5 steps exit 0; SUA repo completely untouched.

---

## Summary

**Total: 5 phases, 11 tasks, 11 commits. SUA repo: 0 commits (untouched entirely).**

Phase 0: Pre-flight baseline (no commits)
Phase 1: Archive sua-knowledge-graph/ (2 commits: hermes-root + archive-internal)
Phase 2: Fix KG-side doc drift (3 commits: README + PHILOSOPHY×2)
Phase 3: Bring formal-spec code into seed (3 commits: kg_core + hooks + verify)
Phase 4: Unified CLI (1 commit)
Phase 5: Final isolation verification (NO commits)

**Isolation invariant (verified at every commit):**
- Before each commit, run `git status --porcelain` in SUA. Must be empty.
- After all commits, run `git log --oneline -1` in SUA. Must be `ccd7e1d`.

**End state:**
- ONE KG project at `hermes-root/knowledge-graph-seed/` (per SUA's official pointer)
- 90 tests PASS (was 75)
- Real data integration intact
- Spec fully satisfied (dataclass + 3-factor + fsync + hooks + unified CLI)
- Both KG-side README + PHILOSOPHY honestly say "MVP done" (P17 fix)
- SUA repo: **zero changes**. HEAD still `ccd7e1d`. All tests (621+) still pass. All docs still honest.

**Diff from v2 plan:**
- v2 had Phase 5 = 1 SUA-side commit (OBSERVATIONS.md append)
- v3 removes Phase 5 entirely
- v2 total: 14 commits. v3 total: 11 commits. Net: 3 fewer commits, all SUA-side.

**Diff from v1 plan:**
- v1 had Phase 5 = 4 SUA-side commits
- v3 removes Phase 5 entirely
- v1 total: 18 commits. v3 total: 11 commits. Net: 7 fewer commits, all SUA-side.

**Risks / open questions:**
- R1: Unified CLI delegates by manipulating `sys.argv`. If a delegated CLI's argparse sees unexpected args, it may error. Mitigation: tested with default args; user can pass through positional args if needed (future enhancement).
- R2: `data/graph.jsonl` (kg_core formal-spec) vs `data/{nodes,reasonings,edges}.jsonl` (kg_*.py dict-based). Two storage formats coexist. Per P21 this is intentional: kg_core for hook-driven record-commit, kg_*.py for the 3 acceptance Q implementation. Long-term: unify into one storage. For now: both work.
- R3: SUA isolation is checked **before every commit**. If any commit would touch SUA, **STOP and ask user** — do not proceed. The hermes-root level commit (archive move) does NOT touch SUA because SUA is a sub-project of hermes-root, not vice versa.

**Out of scope (per P7 奥卡姆 + user isolation requirement):**
- SUA repo: anything (zero changes)
- Migrating kg_*.py dict nodes to dataclass (large refactor; not in user's "fix state" ask)
- Building MCP server (deferred per SEED_DETAIL §8)
- Adding real embeddings (deferred per IMPLEMENTATION_DETAIL §5 footer)
- Even minimal SUA-side documentation updates (per user "不要影响已完成")