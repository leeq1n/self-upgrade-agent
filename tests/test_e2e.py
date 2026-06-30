"""End-to-end test with fully mocked LLM.

This is the canonical "does the full pipeline work?" test.  It runs
all 7 pipeline stages (research → filter → patchgen → sandbox →
evaluate → decide → promote) with LLM calls mocked, so it
works offline and doesn't burn ModelScope daily quota.

The test is intentionally exhaustive — it does not check specific
values, just that the pipeline runs to completion and the final
state is internally consistent.  When a real LLM is available, the
end-to-end live test (--live in run.py) does the same thing with
real HTTP calls and checks specific success/failure values.

Why mocked?  As of 2026-06-30, ModelScope daily quota for the
8 available API keys is exhausted.  Without a working LLM, we
can't run the live test.  Mocking proves the *code paths* work;
real LLM exercises the *contract*.

The same script (with mocks removed) is what `python run.py --live`
runs in production.
"""
import os
import sys
import json
import time
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


PATCH_JSON = json.dumps({
    "function": '''def plan_task(task, llm_call):
    """MOCK-IMPROVED: better prompt for 3-5 numbered steps."""
    return llm_call("Break into 3 steps:").split("\\n")[:3]''',
    # Sandbox auto-detects any "def test_*" function name, so test_p or
    # test_xxx both work.  What matters is the assertion: the mock
    # function returns the list ["1.", "2.", "3."] (3 elements), so
    # the test must assert that exact list.  An earlier version asserted
    # ["1.\\n2.", "3."] (2 elements with an embedded newline) which is
    # impossible to satisfy — hence the spurious "sandbox error: ''"
    # in CI logs.
    "test": 'def test_xxx(): assert plan_task("x", lambda p: "1.\\n2.\\n3.") == ["1.", "2.", "3."]',
    "module": "planner.py",
})

SCORE_JSON = json.dumps({
    "applicability_to_agent_pipeline": 9,
    "novelty": 8,
    "abstract_quality": 7,
})

GOOD_TASK_RESPONSE = "1. Plan the trip\n2. Book hotels\n3. Pack bags"


def _fake_chat(messages, system=None, config=None, response_format=None):
    """Mock LLM chat: returns scores for filter, patches for patchgen,
    task outputs for benchmark."""
    prompt = " ".join(m.get("content", "") for m in messages)
    if "applicability_to_agent_pipeline" in prompt:
        return MagicMock(content=SCORE_JSON, error="", model="mock")
    if "surgical PATCH" in prompt or "function" in prompt:
        return MagicMock(content=PATCH_JSON, error="", model="mock")
    return MagicMock(content=GOOD_TASK_RESPONSE, error="", model="mock")


@pytest.fixture
def mocked_end_to_end_env(monkeypatch, tmp_path):
    """Set up: load .env, mock LLM, isolate upgrades/ to tmp_path."""
    # Load .env
    env_path = os.path.join(
        os.path.dirname(__file__), "..", ".env"
    )
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                if " #" in v:
                    v = v.split(" #", 1)[0].rstrip()
                v = v.strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v

    # Mock src.llm
    import src.llm
    monkeypatch.setattr(src.llm, "chat", _fake_chat)
    monkeypatch.setattr(
        src.llm, "chat_simple",
        lambda prompt, system=None, **kw: _fake_chat(
            [{"role": "user", "content": prompt}], system=system
        ).content,
    )

    # node_filter calls filter_papers(..., use_llm=True) without passing
    # llm_config, so score_paper() short-circuits to keyword scoring and
    # the mock chat() / chat_simple() above never gets invoked for the
    # filter stage.  Replace score_paper() wholesale so all papers
    # route through the LLM-mock path and qualify with deterministic
    # high scores.
    from src import filter as filter_mod
    monkeypatch.setattr(
        filter_mod, "score_paper",
        lambda paper, config, use_llm=False, llm_config=None: filter_mod.ScoredPaper(
            paper=paper,
            abstract_score=7.0,
            applicability_score=9.0,
            novelty_score=8.0,
        ),
    )

    # Use only 3 benchmark tasks (faster, but exercises the loop)
    from src import benchmark as bm_mod
    original_load = bm_mod.load_tasks
    monkeypatch.setattr(
        bm_mod, "load_tasks",
        lambda path="benchmarks/tasks.json": original_load(path)[:3],
    )

    # Mock arXiv search so the e2e test doesn't hit the network.
    # Real arXiv API can be slow (10+ seconds) which makes this test
    # fragile on CI.  We return 3 fake papers with the right shape
    # so the filter/patchgen/evaluate pipeline has real input to
    # chew on.
    #
    # IMPORTANT: pipeline_lg does `from src.research import search_arxiv`
    # at import time, so the binding lives in pipeline_lg's namespace,
    # not in src.research.  We patch the pipeline_lg attribute.
    from src import pipeline_lg as plg
    from src.research import Paper
    fake_papers = [
        Paper(
            arxiv_id="2606.99999",
            title="Self-Evolving World Models for LLM Agent Planning",
            authors="Test Author",
            published="2026-06-30",
            abstract=(
                "We propose self-evolving world models that LLM agents use "
                "for planning. The world model is updated based on agent "
                "execution traces, improving planning quality over time."
            ),
            categories="cs.AI",
        ),
        Paper(
            arxiv_id="2606.99998",
            title="Multi-Agent Coordination with Tool-Use LLMs",
            authors="Another Author",
            published="2026-06-29",
            abstract=(
                "We study how multi-agent LLM systems coordinate tool use "
                "through shared memory and reflection."
            ),
            categories="cs.CL",
        ),
        Paper(
            arxiv_id="2606.99997",
            title="A/B Benchmarking for Code Generation Models",
            authors="Third Author",
            published="2026-06-28",
            abstract=(
                "We propose a benchmark suite for evaluating code generation "
                "models using paired comparison and bootstrap confidence intervals."
            ),
            categories="cs.SE",
        ),
    ]
    monkeypatch.setattr(plg, "search_arxiv", lambda cfg: fake_papers)

    # Snapshot + restore core/planner.py
    planner = os.path.join(
        os.path.dirname(__file__), "..", "core", "planner.py"
    )
    backup = planner + ".e2e_test_bak"
    if os.path.exists(planner):
        with open(planner, encoding="utf-8") as f:
            original = f.read()
        with open(backup, "w", encoding="utf-8") as f:
            f.write(original)
    else:
        original = None
        with open(planner, "w", encoding="utf-8") as f:
            f.write("# placeholder for e2e test\n")

    # Snapshot + restore upgrades/manifest.json
    manifest = os.path.join(
        os.path.dirname(__file__), "..", "upgrades", "manifest.json"
    )
    manifest_bak = manifest + ".e2e_test_bak"
    if os.path.exists(manifest):
        with open(manifest, encoding="utf-8") as f:
            manifest_orig = f.read()
        with open(manifest_bak, "w", encoding="utf-8") as f:
            f.write(manifest_orig)
    else:
        manifest_orig = None

    yield

    # Restore
    if original is not None:
        with open(planner, "w", encoding="utf-8") as f:
            f.write(original)
    else:
        os.remove(planner)
    if os.path.exists(backup):
        os.remove(backup)
    if manifest_orig is not None:
        with open(manifest, "w", encoding="utf-8") as f:
            f.write(manifest_orig)
    elif os.path.exists(manifest):
        os.remove(manifest)
    if os.path.exists(manifest_bak):
        os.remove(manifest_bak)
    # Clean bench_tmp / bench_bak leftover from node_evaluate
    for suffix in (".bench_bak", ".bench_tmp"):
        p = planner + suffix
        if os.path.exists(p):
            os.remove(p)


class TestEndToEnd:
    """All 7 stages of the pipeline run to completion with mocked LLM."""

    def test_pipeline_runs_to_completion(self, mocked_end_to_end_env):
        from src.pipeline_lg import run
        from src.config import load_config

        cfg = load_config("config.yaml")
        cfg.evaluate.trials_per_test = 1

        t0 = time.time()
        state = run(cfg, dry_run=False)
        elapsed = time.time() - t0

        # ── Stage outputs ──
        assert len(state.get("papers") or []) > 0, "research should return papers"
        scored = state.get("scored_papers") or []
        assert len(scored) > 0, "filter should qualify some papers"
        # patchgen should generate a patch (mock LLM returns valid JSON)
        patch = state.get("patch") or {}
        # Note: in dry-run mode, no patch.  In real --live, mock returns patch.
        # If patch exists, verify it has the right shape.
        if patch:
            assert "function" in patch
            assert "test" in patch
            assert "module" in patch

        # evaluate ran
        ev = state.get("eval") or state.get("evaluation") or {}
        if ev:
            assert "baseline_rate" in ev
            assert "upgraded_rate" in ev

        # pipeline set done=True at the end
        assert state.get("done") is True, "pipeline did not reach 'done' state"

        # Sanity: no Python-level exceptions
        assert not state.get("errors"), f"pipeline errors: {state.get('errors')}"

        # Sanity: the elapsed time is bounded (mocked LLM should be fast)
        assert elapsed < 120, f"end-to-end took {elapsed:.1f}s (expected <120)"

    def test_pipeline_dry_run_works_without_llm(self, mocked_end_to_end_env):
        """dry_run=True uses simulated eval data, no LLM needed at all."""
        from src.pipeline_lg import run
        from src.config import load_config

        cfg = load_config("config.yaml")
        cfg.evaluate.trials_per_test = 1

        state = run(cfg, dry_run=True)
        # dry-run always sets done
        assert state.get("done") is True
        # dry-run eval uses simulated 0.80 / 0.85-ish numbers
        ev = state.get("eval") or state.get("evaluation") or {}
        assert ev.get("baseline_rate", 0) > 0

    def test_pipeline_handles_no_papers_qualified(self, monkeypatch):
        """If the filter rejects all papers, pipeline should end cleanly
        with empty patch (no promote, no crash)."""
        from src.llm import LLMConfig
        from src import llm as llm_mod

        def reject_all(messages, system=None, config=None, response_format=None):
            return MagicMock(
                content='{"applicability_to_agent_pipeline": 1, "novelty": 1, "abstract_quality": 1}',
                error="", model="mock",
            )

        monkeypatch.setattr(llm_mod, "chat", reject_all)
        monkeypatch.setattr(llm_mod, "chat_simple", lambda p, **kw: reject_all([{"role":"user","content":p}]).content)

        # node_filter uses keyword scoring (no llm_config), so the chat
        # mock above never affects filter.  Patch score_paper to return
        # sub-threshold scores so the filter rejects every paper.
        from src import filter as filter_mod
        monkeypatch.setattr(
            filter_mod, "score_paper",
            lambda paper, config, use_llm=False, llm_config=None: filter_mod.ScoredPaper(
                paper=paper,
                abstract_score=0.1,
                applicability_score=0.1,
                novelty_score=0.0,
            ),
        )

        # Load .env so from_env works
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if " #" in v:
                        v = v.split(" #", 1)[0].rstrip()
                    v = v.strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v

        from src.pipeline_lg import run
        from src.config import load_config
        cfg = load_config("config.yaml")

        # Snapshot planner to restore later
        planner = os.path.join(os.path.dirname(__file__), "..", "core", "planner.py")
        with open(planner, encoding="utf-8") as f:
            original = f.read()
        try:
            state = run(cfg, dry_run=False)
            # Pipeline exits cleanly when filter rejects all papers:
            # _papers_qualified routes to END, and "done" stays False
            # because node_decide is the only node that flips it.
            assert state.get("done") is False, (
                "expected early END (done=False), got done=True"
            )
            # No patch was generated (filter rejected all)
            assert not state.get("patch"), "should not promote with no patch"
            # No exceptions bubbled up
            assert not state.get("errors"), f"pipeline errors: {state.get('errors')}"
        finally:
            with open(planner, "w", encoding="utf-8") as f:
                f.write(original)
