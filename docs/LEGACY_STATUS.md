# Legacy code status — 2026-07-30

> **Trigger**: User 2026-07-30 ask: "到现在为止的修改是否符合原则且有价值".
> Plus IMPLEMENTATION_PLAN P4: "v1.x legacy code cleanup (src/, tests/, self_upgrade/)".
>
> **Decision**: keep src/ + self_upgrade/ as test fixtures (NOT delete).
> This document captures the analysis + decision.

## 1. What "v1.x legacy" actually contains

```
src/                  — 59 files, 527 KB
├── _archived/         — old modi.py + skillgen.py (clearly archived)
├── ab_benchmark.py    — A/B testing harness (per SUA evaluation)
├── ab_integration.py  — A/B + pipeline integration
├── benchmark.py       — benchmarking
├── chat_repl.py       — REPL for chat mode
├── decide.py          — decision logic
├── filter*.py         — candidate filter
├── keyword_expander.py — keyword expansion
├── langchain_bridge.py — LangChain integration
├── llm.py             — LLM client wrapper
├── patchgen.py        — patch generator
├── pipeline.py        — main pipeline
├── research*.py       — research fetch (arxiv, s2, pwc, github)
├── skillgen.py        — skill generation (legacy)
├── skill_*.py         — skill lifecycle
├── switcher.py        — switch logic
└── ... (~30 more files)

self_upgrade/         — 2 files, 19 KB
├── __init__.py
└── __main__.py

tests/                — 78 .py files
```

## 2. Per README — this IS legacy

`README.md` line 80-85 (canonical statement):

> "This project was originally a self-improving agent that modifies
> `core/planner.py`. The code still exists and is functional, but
> is no longer the project's focus. For code documentation and CLI
> usage, see `README_DETAIL.md` § Code legacy."

## 3. Per 真 evidence — src/ + self_upgrade/ are STILL active

75 files in current codebase import from `src/` or `self_upgrade/`:

| Importer type | Count | Status |
|---|---|---|
| `tests/test_*.py` | 74 | Active tests (exercises src/ modules) |
| `core/agent.py` | 1 | Core agent runtime |
| `collect_papers.py` | 1 | CLI script |
| `run_1round.py` | 1 | CLI script |
| `run_3rounds_manual.py` | 1 | CLI script |
| `run_stable.py` | 1 | CLI script |

`requirements.txt` has `langgraph>=0.2` (used by `src/langchain_bridge.py`).

**Conclusion**: src/ is "documented legacy" but still actively used by
74 tests + 5 CLI scripts. NOT deletable without major refactor.

## 4. Decision (per P-7 Occam + R137 wordy-trap defense)

**Keep src/ + self_upgrade/ as-is.** Do NOT delete.

Rationale:
1. README self-declares as legacy but doesn't say "delete".
2. 74 tests + 5 scripts actively use it — deletion breaks CI.
3. The v2.x work (audit infrastructure, AGENTS.md, hooks) is
   ADDITIVE to v1.x agent, not a replacement.
4. Per M-n 18 destruction principle: "Never destroy BEFORE
   verifying replacement is in place." Replacement is not in place.
5. Cost of keeping = 527 KB on disk + 74 tests in CI.
   Cost of deleting = broken CI + lost functionality.

## 5. What we COULD do (deferred to future session)

- Move src/ to `src/_legacy/` (signals legacy status more strongly)
- Add `# LEGACY: see docs/LEGACY_STATUS.md` docstring to each module
- Add `pytest --ignore=tests/test_*legacy*` for faster CI
- Add `@deprecated` decorators with migration path

None of these are urgent; the current state is documented + functional.

## 6. v2.x work is independent of v1.x decision

The v2.3.0 → v2.13.0 work added:
- AGENTS.md + core-layer/ (agent discipline)
- hooks/ (commit-msg, pre-commit enforcement)
- .hermes/scripts/ (audit scripts)
- docs/ (knowledge library)

None of this REQUIRES deleting src/. The two layers coexist:
- v1.x = self-improving paper discovery agent (src/)
- v2.x = agent discipline knowledge library (AGENTS.md + hooks)

Both are valid SUA products, just different focuses.

## 7. References

- `README.md` line 80-85 (canonical legacy statement)
- `requirements.txt` (langgraph dependency proves v1.x still active)
- `tests/test_*.py` (74 tests exercise v1.x modules)
- IMPLEMENTATION_PLAN 2026-07-30 P4 (the source task)
- M-n 18 destruction principle (verify replacement first)
- P-7 Occam (smallest effective change)
- P-17 no fabricate (honest value assessment)
- R137 wordy-trap defense (avoid over-claiming cleanup)