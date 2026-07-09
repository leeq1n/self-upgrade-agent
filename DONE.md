# DONE — Completed Work (one line per item)

When you finish a TODO, move it here.  Each entry: one line + key commit.

## v2.x minimal agent (this session, 2026-07-08)

- [x] **v2.0.0 minimal agent** — 1 LLM call + 1 harness test, no
  LangGraph, no self-refine.  Commit `af7d26d`.  See
  [docs/INDEX.md](docs/INDEX.md#project-state) §1.

- [x] **v2.1.0 atomic apply_patch** — file-level atomic via tempfile +
  os.replace, AST-based surgical merge, revert restores byte-perfect.
  Commits `facd69d`, `1f2fbdb` (defensive None/empty patch handling).
  See [docs/INDEX.md](docs/INDEX.md#project-state) §2.

- [x] **v2.2.0 run_one_round** — closes the loop: improve → apply →
  tests → KEPT/REVERTED decision.  Commit `9915a9e`.  See
  [docs/INDEX.md](docs/INDEX.md#project-state) §3.

- [x] **Tests: 438 PASS + 6 skip + 0 fail** (per commit `9915a9e`).
  Layered: unit (test_v2_agent, test_v2_apply) → joint
  (test_v2_integration, test_v2_round) → real e2e smoke (Temp script,
  not in suite).

## v1.8.x stable baseline (prior sessions)

- [x] v1.8.1-alpha on master — fixes 6+ root-cause bugs.
- [x] v1.8.2-alpha on feature/v1.8.2-pdf-memory — MCP memory + ReAct +
  arxiv PDF + memory writes.  Superseded by v2.x.

## Cleanup (this session)

- [x] **Docs cleanup**: 19 → 4 docs.  Old docs deleted in commit
  `361fe5d` (now superseded by commit `9915a9e` branch history; `518d3ec`).
  Kept: `PROJECT_STATE.md`, `USER_INSIGHTS.md`, `CONSTRAINTS.md`,
  `MODEL_STRATEGY.md`.

- [x] **PROJECT_STATE.md** rewritten as single source of truth (one
  paragraph sections, error list, constraint list).  Commit
  `81e7574` content carried forward.

- [x] **TODO.md + DONE.md** added as task tracking (you asked 2026-07-08).
- [x] **LITERATURE.md / LITERATURE_DETAIL.md** added — paper knowledge
  moved from session memory to project docs.  11 papers covered:
  Reflexion, Self-Refine, One Step Forward, Constitutional AI,
  Self-Harness, Harness Engineering, Multi-Agent Failure,
  HyperAgents, Agent Improvement Loop (Substack), SkillOpt,
  Factory Droid.  See [docs/LITERATURE.md](docs/LITERATURE.md) for
  table view; [docs/LITERATURE_DETAIL.md](docs/LITERATURE_DETAIL.md)
  for full notes.

- [x] **Doc orphan check** — every summary now links to its _DETAIL
  companion or another doc.  Every cross-doc link resolves.  Verified
  programmatically.

## Stage gate: doc structure (commit `c51dfd4`, then `19ebf8b`, then this)

- [x] **PRINCIPLES.md added** — 18 cross-project portable principles
  distilled from this session.  Categories: workflow (P1-P6), design
  (P7-P10), documentation (P11-P14), process (P15-P18).  See
  [docs/PRINCIPLES.md](docs/PRINCIPLES.md).  Each rule has WHY +
  HOW.  Can be copied verbatim to any future project.

- [x] **TODO.md updated** — closed stage gate (v2.0.0 → v2.2.0) items
  re-stated; PRINCIPLES link added; "run real e2e with new prompt"
  added as a fresh TODO (the prompt-as-interface refactor needs real
  verification).

- [x] **INDEX.md updated** — PRINCIPLES row added; reading order now
  includes PRINCIPLES as step 6 (general, not project-specific).

- [x] **Doc orphan check** — every summary has _DETAIL pointer or
  next-level reference; PRINCIPLES.md is portable (no _DETAIL needed).


## v2.3.0 — Failure → regression test pipeline (commit `0dc68cb`)

- [x] **`src/failures.py`** — append-only JSONL log of failure
  signatures, dedup by (arxiv, target, decision), replay
  mechanism (`replay_one` returns now_passes / still_fails /
  not_replayed).  Total ~150 LOC.
- [x] **`src/v2_round.py`** wired to call `log_failure()` on each
  of the 3 failure return paths (NO_PATCH, APPLY_FAILED, REVERTED).
  KEPT path does NOT log (successes aren't regression tests).
- [x] **`tests/test_v2_failures.py`** (14 tests) — unit + joint
  coverage of the log+replay contract.
- [x] **Real data**: `upgrades/failures.jsonl` shows actual
  failure signatures from test runs (timestamp + decision + error).

Verified:
  - Unit (test_v2_failures.py): 14 PASS
  - Full suite: 453 PASS + 6 skip + 0 fail (was 439; +14)
  - Real persistence: JSONL file written and readable

Per P18 (PRINCIPLES.md "Failure → regression test"): the loop is
now half-closed.  The other half — automatic replay of the log
to detect if a known failure recurs — is a future v2.3.x.
