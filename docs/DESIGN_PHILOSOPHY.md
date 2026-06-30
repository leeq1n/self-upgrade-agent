# Self-Upgrade Agent — Design Philosophy

> These are the design principles that emerged during the development
> of this project.  They came from the user (not the assistant) and
> were applied iteratively as the project matured from v1.0 → v1.5.1.
>
> When you make a change that violates one of these, you should either
> have a good reason, or fix the change to align with the principle.

---

## P1. Trust evidence, not assumptions

**Symptom**: I assumed 7 API keys were all dead because the first
test I ran burned through their quota.  I was wrong — 3 of them
were still alive and 5 had **permanent** auth failures (401/403),
not quota exhaustion.  I had confused "tried and failed" with
"unavailable forever".

**Rule**:
- "It failed once" is not "it doesn't work" — check the *reason* it failed.
- "It worked once" is not "it always works" — verify across multiple runs.
- Before you decide a model or key is broken, **actually test it** with
  a one-shot `httpx` call and read the response body.

**In this project**:
- `src/llm.py::_is_daily_quota_error` distinguishes 429-quota from
  401/403-auth by reading the response body keywords.
- `QuotaState.mark_permanently_dead` (100y cooldown) vs
  `mark_dead` (24h cooldown) are separate methods because they
  have different recovery semantics.

---

## P2. The bootloader pattern: A modifies B, switch only after B passes

**Symptom**: I "implemented" the A/B benchmark for promoting patches
to `core/`, but in v1.5.0 the actual swap was a bare
`open(orig_path, "w").write(patched)` — non-atomic, half-written
files on crash, AND Python's module cache meant the trial
afterwards ran the *old* in-memory `core.planner`.  The A/B
comparison was a silent no-op.

**Rule**:
- A modifies B: writing the new version must be **atomic** (`.tmp`
  + `os.replace`, not a bare `open(orig_path, "w")`).
- Test B: while testing, the live code must be the new version.
  Evict from `sys.modules` to defeat the import cache.
- Switch to B: only after test passes.  Restore from backup if it
  fails.
- A crash at any point in the cycle must leave the system in a
  recoverable state (either the original A or the new B, never
  half of either).

**In this project**:
- `src/pipeline_lg.py::node_evaluate` uses `.bench_tmp` + `os.replace`
  for the test write, `shutil.move` for the restore, and clears
  `sys.modules[core.*]` before the upgraded trial.
- `src/switcher.py::promote_patch` uses the same atomic pattern.
- 8 tests in `tests/test_evaluate_atomicity.py` cover the
  pre-/post-replace crash scenarios.

---

## P3. Default to cheap, upgrade only when justified

**Symptom**: v1.4.0 set the default model to `Qwen3.5-2B` because
it sounded cheap.  I never verified that the 2B model actually
exists on ModelScope — it doesn't.  The default was 400-erroring
on every call.

**Rule**:
- For defaults, pick the *cheapest model that is actually served
  by your provider* and verify it.
- For testing, use the cheapest model that works — it costs
  the user less.
- For production (rare, important runs), let the user opt into a
  more expensive model.

**In this project**:
- v1.5.0 default: `ZhipuAI/GLM-5.1` (verified to return 200 OK on
  the 3 alive keys).
- Test mode: `conftest.py` sets short timeouts (10s per-request,
  20s total) so a misconfigured test fails fast.
- Users can override with `LLM_MODEL=` env var for one-off runs.

---

## P4. Test files must not leave the system in a weird state

**Symptom**: v1.4.0's `tests/test_promote_and_rollback` writes
to `core/planner.py`.  If the test crashed between write and
restore, the test runner would leave the project in a broken state
for the next test.

**Rule**:
- Tests that modify real files (vs mocks) must use a fixture
  that snapshots + restores, even on assertion failure.
- Atomic operations in tests should still use atomic patterns
  (`.tmp` + rename) so a SIGKILL during the test doesn't leave
  garbage files.

**In this project**:
- `tests/test_switcher.py::clean_switcher` snapshots `core/planner.py`
  and restores on teardown.
- `tests/test_evaluate_atomicity.py::restore_planner` does the
  same, plus cleans up `.bench_bak` / `.bench_tmp`.

---

## P5. The user can be wrong about the project's state

**Symptom**: DeepSeek's "everything is done ✅" review missed
real issues (the .env had wrong keys, the test was hanging
180s+ on LLM 429, the surgical merge bootloader was actually
direct-overwrite).  An LLM that was supposed to "evaluate"
the project went along with the surface-level claim that the
project was done.

**Rule**:
- "X says it's done" is not "X is done" — verify with your own
  measurements.
- Tests passing is necessary, not sufficient.  Tests that
  exist but don't exercise the right path can pass while the
  real path is broken.
- Run the code, look at the log output, read the file diffs.

**In this project**:
- 137 tests pass, but the project *also* has ISSUES.md listing
  11 known issues.  Tests + issues ≠ "done"; tests + issues
  *resolved* = done.
- `docs/DELIVERY.md` calls out which 4-dim 5/5 are achieved
  and which P1 work is still open.

---

## P6. Clean interfaces, clean implementations

**Symptom**: v1.4.0 had `src/evaluate.py` AND `src/pipeline_lg.node_evaluate`
AND `src/benchmark.py` — three different ways to do A/B
benchmarking, with no clear "use this one" rule.  Code review
finds a second `def filter_papers` that does the same thing
slightly differently.

**Rule**:
- One way to do a thing.  If you have two, one is legacy (mark it).
- Public API: prefer fewer functions that take more options over
  many functions that each take few options.
- File size: 200-400 lines is comfortable.  700+ lines means the
  module is doing too much.

**In this project (current state)**:
- `src/llm.py` 792 lines — needs to be split (open ISS-007).
- `src/pipeline_lg.py` 680 lines — borderline; has LangGraph
  orchestration + per-node logic.  Worth splitting.
- `src/evaluate.py` vs `pipeline_lg.node_evaluate` — duplicate
  functionality.  Resolve ISS-004 by deleting one and making the
  other the single source of truth.

---

## P7. End-to-end is the only test that matters

**Symptom**: v1.4.0 had 107 unit tests, all green, in 2.07s.  The
project still hadn't successfully promoted a patch.  Unit tests
verify the *parts* but not the *whole*.

**Rule**:
- Unit tests catch bugs in isolation; integration tests catch
  bugs in composition.  You need both, but the integration tests
  are the ones that catch "the parts work but the system
  doesn't."
- An "end-to-end happy path" test should exist that runs the
  full pipeline on at least one real input.

**In this project (v1.5.0)**:
- A real end-to-end promote succeeded once (v1.5.0 commit
  `97aa0a1`, using the "Self-Evolving World Models" paper).
  Documented in `docs/DELIVERY.md`.
- However, that promote was triggered *manually* (bypassing
  the A/B benchmark) because the test environment had no
  working API keys.  A *truly* end-to-end test (search →
  filter → patchgen → sandbox → evaluate → decide → promote)
  in CI is still on the roadmap.

---

## P8. Never lose data, always be reversible

**Symptom**: `node_evaluate` originally wrote `core/planner.py`
non-atomically.  A crash mid-write would leave the file
half-written, with no backup.  The next time the agent starts
up, `import core.planner` fails with a syntax error.

**Rule**:
- Every state change must be either atomic (crash-safe) or
  reversible (has a backup + restore path).
- "I have a try/except" is not enough — `try/except` doesn't
  run on SIGKILL, OOM, or power loss.

**In this project**:
- All writes to `core/*.py` go through `.tmp` + `os.replace`.
- `upgrades/backups/<module>_<timestamp>.bak` snapshots before
  every promote.
- `quota_state.json` and `manifest.json` are committed with
  `os.replace` so a crash mid-write leaves the previous version
  intact.
- `switcher.rollback_patch(target_module)` restores the most
  recent backup.

---

## P9. Documentation is part of the deliverable

**Symptom**: Mid-development, the only docs were `README.md` and
`PROJECT_BRIEF.md`.  The actual *how* of running + debugging was
scattered across chat history.  When the conversation closed,
that knowledge was effectively lost.

**Rule**:
- If a question came up once in chat, it should appear in a doc
  file the next time someone asks it.
- Each user-facing CLI flag has at least a one-line `--help`
  description.
- Each non-obvious design decision has a comment + a doc entry
  explaining the trade-off.

**In this project**:
- `README.md` — user-facing overview
- `PROJECT_BRIEF.md` — what state the project is in
- `ISSUES.md` — what doesn't work yet + roadmap
- `docs/API_REFERENCE.md` — function signatures
- `docs/LLM_CALLS.md` — LLM key management + troubleshooting
- `docs/DELIVERY.md` — what the project can do today
- `docs/DESIGN_PHILOSOPHY.md` (this file) — the *why*

---

## P10. The user drives the direction

**Symptom**: At one point I spent an hour making the project
"production-ready" (adding metrics dashboards, deployment
scripts, Kubernetes manifests) when the user just wanted to know
"is it done?"  I was optimizing for a goal nobody had stated.

**Rule**:
- The user's stated goal is the goal.  When the goal is unclear,
  ask.  When the goal is clear, optimize for that.
- "Polish" should be reactive to user feedback, not proactive.
  The user will tell you when something is good enough.

**In this project**:
- The user's goal is captured in `IDEA.md` (one page, no
  embellishment).
- `ISSUES.md` is a roadmap organized by user-stated priorities
  (P0 → P1 → P2), not by what would be "fun to build."

---

## How to apply these

When reviewing a PR / commit:
- Does it violate any of P1-P10?  If yes, fix it or document why.
- Does it have a corresponding test for the user-facing behavior?
  (P7)
- Does it leave the system in a recoverable state on crash?  (P8)
- Is the "why" documented in a comment + a doc file?  (P9)

When the user says "this is wrong":
- Trust them, even if your tests pass.  (P5)
- Look for the *cause*, not the symptom.  (P1)
- Add a regression test.  (P7)
