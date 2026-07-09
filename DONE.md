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


## v2.3.1 — Automatic replay loop (commit `216f7e0`)

- [x] **`replay_all()` in src/failures.py** — iterates unique failure
  modes, calls `replay_one()` for each, aggregates verdicts into
  `ReplayReport`.  Total ~70 LOC.
- [x] **`replay_all_failures()` driver in src/v2_round.py** — wires
  play_fn to run_one_round (real LLM call), reads from
  `upgrades/failures.jsonl`, returns `ReplayReport`.
- [x] **5 new tests** in `tests/test_v2_failures.py::TestReplayAll`:
  empty log, 3 unique modes, dedup, mixed verdicts, to_dict.

Verified:
  - Unit: 19 PASS (was 14, +5)
  - Full suite: 458 PASS + 6 skip + 0 fail (was 453; +5)
  - 11/11 hermes-verify PASS

P18 (Failure → regression test) loop is now closed:
  - v2.3 (commit `0dc68cb`): log on failure
  - v2.3.1 (commit `216f7e0`): replay the log

What this means:
  - The agent can now self-test for regressions
  - If a known failure recurs, the replay catches it
  - If a known failure is now fixed, the replay reports it
  - Both are reported in a single ReplayReport

Next:
  - User to invoke `replay_all_failures()` on real data
  - User to run 5 consecutive KEPT rounds (stability test)


## v2.3.2 — User-runnable scripts (commit `pending`)

Per user feedback 2026-07-08: "下次能不能整理好一个小脚本给我跑，
跑完你删掉？不然我要一行一行复制过去。"

- [x] **`scripts/run_replay.py`** — one-shot replay of
  `upgrades/failures.jsonl`, prints JSON report.
  Usage: `python scripts/run_replay.py`
- [x] **`scripts/run_5_rounds.py`** — 5 consecutive rounds with
  FIXED_PAPER (DyLAN 2310.02170), prints summary.
  Usage: `python scripts/run_5_rounds.py`
- [x] **`scripts/_self_check_run_replay.py`** — dry-run verifier
  for run_replay (no LLM needed).
  Usage: `python scripts/_self_check_run_replay.py`
- [x] **`scripts/__init__.py`** — package init so the scripts
  are importable as modules (for tests / IDE).

Note: tried adding tests/test_scripts.py but the import chain
triggers the real LLM path in conftest fixtures, hanging the
suite.  Removed the test file.  The scripts are validated by
the `_self_check_run_replay.py` dry-run instead.


## v2.4.0 — CLI consolidation (commit `pending`)

Per user feedback 2026-07-08: "一堆奇奇怪怪的 run 入口, 是否需要清理
一下? 这项目需要有统一管理的功能, 能跑自进化, 能具体使用, 能整理
项目使其干净. 此外就是测试不同规模的功能, 也可以当作 debug".

This commit unifies the entry points:

- NEW self_upgrade/__main__.py (replaces v1.8.x unified CLI):
  - Click-based group with 3 subcommands
  - `improve` — one round of self-improvement
  - `replay` — replay the failure log (P18)
  - `test-scale N` — N consecutive rounds (debug / load test)
  - `--mock` / `--no-mock` flag (top-level, for future)
  - Lazy imports so the CLI is fast to load

- NEW tests/test_v2_cli.py (9 tests):
  - Click group structure
  - Subcommand help texts
  - Invalid input rejection
  - Lazy import speed (CLI module imports in <5s)

- MODIFIED tests/test_v181_features.py:
  - Replaced 2 obsolete v1.8.x tests with 2 v2.x tests
  - test_cli_has_three_subcommands
  - test_no_legacy_scripts_directory

- DELETED obsolete files:
  - tests/test_unified_cli.py (v1.8.x CLI tests)
  - tests/test_gc.py (v1.8.x gc subcommand tests)
  - tests/test_audit_cli.py (v1.8.x audit subcommand tests)
  - scripts/__init__.py
  - scripts/run_replay.py
  - scripts/run_5_rounds.py
  - scripts/_self_check_run_replay.py
  - scripts/start_llama_servers.sh

- MODIFIED:
  - self_upgrade/__main__.py rewritten (replaces v1.8.x CLI)

Verified:
  - Full suite: 449 PASS + 6 skip + 0 fail (was 458 before deleting
    obsolete tests + adding test_v2_cli.py)
  - python -m self_upgrade --help shows 3 subcommands
  - Click group structure verified by tests/test_v2_cli.py
  - Lazy import: CLI module loads in <5s (no LLM required)

Usage (the user now has ONE entry point):
  python -m self_upgrade improve --target core/planner.py
  python -m self_upgrade replay
  python -m self_upgrade test-scale 5
  python -m self_upgrade --help


## v2.4.1 — Gitignore cleanup (commit `a5d3029`)

Per P17 honest reporting: in commit `2442d09` (v2.4.0) I ran
`git add -A` which inadvertently staged `upgrades/*.json`,
`*.db`, `*.jsonl`, and `archive/*.json` files (runtime state).

This commit fixes that mistake:

- [x] **`git rm --cached -r upgrades/`** — removed 20 files
  from git index.  Files remain on disk (no data loss).
- [x] **Added `upgrades/*` to `.gitignore`** with `!upgrades/.gitkeep`
  exception so the directory is "tracked" if empty.

Verified:
  - `git check-ignore` confirms `upgrades/failures.jsonl` is
    now ignored
  - 28 PASS in test_v2_cli.py + test_v2_failures.py (no
    regression)
  - Working tree fully clean

Lesson recorded in TODO.md:
  - `git add -A` is too permissive for our project (has
    runtime artifacts).  Use `git add <file>` or `git add -u`.


## v3.0.0 — Multi-paper reading (commit `pending`)

Per user feedback 2026-07-08: 'multi-paper reading,
generate ideas/views/plans then let LLM judge'.

This commit introduces `src/v3_multipaper.py`:

- [x] **PaperSummary dataclass** — id, title, idea, viewpoint,
  plan, section.  Each is a 1-line summary extracted from the
  hand-curated catalog.
- [x] **parse_literature_catalog(path)** — reads
  `docs/LITERATURE_DETAIL.md`, splits by `##` headings, extracts
  `**TL;DR**`, `**Why ... use**`, `**Use it for**` per section.
- [x] **read_papers(ids=None)** — returns all summaries, or
  filter by arxiv_id list.
- [x] **_infer_arxiv_id(heading)** — slugifies "Self-Harness (2026)"
  to "self-harness".  Good enough for now; full arxiv_id
  resolution is future work.
- [x] **17 tests** in `tests/test_v3_multipaper.py`:
  - PaperSummary / to_dict
  - _infer_arxiv_id (5 cases: simple, year suffix, dash, em dash,
    empty)
  - parse_literature_catalog (5 cases: 3-paper sample,
    required fields, idea extraction, viewpoint/plan extraction,
    missing file raises CatalogParseError, real catalog has
    >= 5 papers)
  - read_papers (4 cases: all by default, filter by ids,
    unknown ids, dedup)
  - paper_count

Verified:
  - 17 PASS in 0.14s
  - Real catalog parses: 11 papers extracted
  - Full suite: 466 PASS + 6 skip + 0 fail (was 449; +17 net)

Design choices (per session lessons):
  - Deterministic parsing, not LLM.  Avoids LLM-temperature
    noise that has hurt v2.x (per LITERATURE).
  - Catalog source: `docs/LITERATURE_DETAIL.md` (per P11:
    project knowledge, not session memory).
  - No new deps.  Pure stdlib (re, dataclasses).
  - Pure functional API: read_papers() returns list, no side
    effects.

NOT in this commit (future):
  - v3.0.1 — LLM-as-judge on top of summaries
  - v3.0.2 — wire into run_one_round (multi-paper selection)
  - v3.0.3 — think-execute harness for LLM (per user idea)


## v3.0.1 step 1.1 — Judge mock (commit `6158559`)

Per user workflow 2026-07-09: '先测通小功能, 再联合成大
功能继续测, 一步一步确认功能'.  This is the FIRST of 4
small steps toward LLM-as-judge.

- [x] **`src/v3_judge.py`** (~70 LOC, NEW):
  - `select_best_mock(summaries, ranking_fn=None) -> PaperSummary`
  - `EmptySummariesError` (raised on empty input)
  - `_default_rank`: plan*2 + idea + viewpoint (length heuristic)
  - `is_mock()` returns True (sanity check)
- [x] **`tests/test_v3_judge.py`** (~150 LOC, 12 tests, NEW):
  - EmptySummaries (1), SingleSummary (2), MultipleSummaries (5),
    IsMock (1), MockIntegrationWithMultiPaper (3)

Verified:
  - 12 PASS in 0.08s
  - Full suite: 478 PASS + 6 skip + 0 fail (was 466; +12)
  - 10/10 hermes-verify PASS

NOT in this commit (future steps):
  - v3.0.1 step 1.2: real LLM call (select_best using v2 LLM)
  - v3.0.1 step 1.3: joint test (v3_judge + v3_multipaper end-to-end)
  - v3.0.1 step 1.4: wire into v2_round (multi-paper selection
    replaces FIXED_PAPER)

Step 1.1 alone is NOT useful for self-improvement yet.  It is
the foundation; the LLM judge will replace the length-based
heuristic in step 1.2.


## v3.0.1 step 1.2 — Real LLM judge (commit `3073015`)

Per user workflow (small-step): step 1.1 (mock) → step 1.2
(real LLM with mock fallback).

- [x] **`select_best(summaries, config=None)`** — real LLM call.
  Lazy imports `src.v2_agent._chat` so the mock stays cheap.
- [x] **`_build_judge_prompt(summaries)`** — builds the prompt
  asking for `{"best_arxiv_id": "..."}` JSON.
- [x] **`_parse_llm_response(text)`** — regex tolerant of
  markdown fences, extra spaces, partial JSON.
- [x] **`_call_llm(prompt, config)`** — wraps `_chat`.
- [x] **Fallback strategy** (per fail-OPEN):
  - Non-JSON response → mock
  - Unknown id → mock
  - LLM exception → mock
  - Empty response → mock
  - config=None → mock
- [x] **+15 tests** (27 total now):
  - BuildJudgePrompt (2), ParseLlmResponse (6), Fallback (2),
    WithMockedLlm (5)

Verified:
  - 27 PASS in 0.14s
  - Full suite: 493 PASS + 6 skip + 0 fail (was 478; +15)
  - 16/16 hermes-verify PASS

NOT in this commit (future steps):
  - v3.0.1 step 1.3: joint test (e2e with mocked LLM)
  - v3.0.1 step 1.4: wire into v2_round
