"""Tests for end-to-end harness (v3.0.2 step 2.4).

Joint test: Thinker + Executor + Loop work together as a single
harness.  The "harness" is the smallest unit of v3.0.2.

Per LITERATURE (Nate Berkopec 'verifiable + looped', Self-Harness
40->62%, Lilian Weng 'harness as important as model'): the harness
is the bottleneck.  This test verifies the harness works as a
closed loop.

All tests use mock components to avoid LLM calls.  Real LLM
integration is exercised by the user running `python -m self_upgrade
improve-multi` in their environment.
"""
import json
import pytest
from unittest.mock import patch

from src.v4_thinker import MockThinker, Step, JsonThinker
from src.v4_executor import MockExecutor, FunctionExecutor, Result
from src.v4_loop import Loop, LoopResult, LoopStatus


# ── Helper ─────────────────────────────────────────────────────

def make_harness(thinker, executor, max_retries=0):
    """Compose a Loop with given thinker + executor."""
    return Loop(thinker, executor)


# ── End-to-end with mock ───────────────────────────────────────

class TestEndToEndMock:
    def test_simple_three_step_pipeline(self):
        """prompt -> 3 steps -> all succeed -> SUCCEEDED."""
        thinker = MockThinker(fixed_plan=[
            Step("load", args={"src": "data.csv"}),
            Step("analyze"),
            Step("save", args={"dst": "out.json"}),
        ])
        executor = MockExecutor(default_value="ok")
        harness = make_harness(thinker, executor)
        result = harness.run("load and analyze data.csv")
        assert result.status == LoopStatus.SUCCEEDED
        assert len(result.results) == 3
        assert [r.step_name for r in result.results] == [
            "load", "analyze", "save"]
        assert all(r.success for r in result.results)
        assert result.attempts == 1
        assert result.elapsed_s >= 0  # not strictly tested, just present

    def test_function_executor_with_realistic_handlers(self):
        """FunctionExecutor with handlers that mimic real operations."""
        # Track side effects
        effects = {"loaded": [], "written": []}

        def load_handler(step):
            src = step.args.get("src", "default")
            effects["loaded"].append(src)
            return Result(success=True, value=f"content of {src}",
                          step_name=step.name)

        def write_handler(step):
            dst = step.args.get("dst", "default")
            effects["written"].append(dst)
            return Result(success=True, value=f"wrote to {dst}",
                          step_name=step.name)

        thinker = MockThinker(fixed_plan=[
            Step("load", args={"src": "a.txt"}),
            Step("load", args={"src": "b.txt"}),
            Step("write", args={"dst": "out.txt"}),
        ])
        executor = FunctionExecutor({
            "load": load_handler,
            "write": write_handler,
        })
        harness = make_harness(thinker, executor)
        result = harness.run("load a, load b, write out")
        assert result.status == LoopStatus.SUCCEEDED
        assert effects["loaded"] == ["a.txt", "b.txt"]
        assert effects["written"] == ["out.txt"]

    def test_harness_loop_result_is_serializable(self):
        """LoopResult.to_dict() returns valid JSON-serializable dict."""
        thinker = MockThinker(fixed_plan=[Step("a"), Step("b")])
        executor = MockExecutor()
        harness = make_harness(thinker, executor)
        result = harness.run("test")
        # Should be JSON-serializable (P19 observability)
        d = result.to_dict()
        json.dumps(d)  # raises if not serializable
        assert d["status"] == "SUCCEEDED"
        assert len(d["plan"]) == 2
        assert len(d["results"]) == 2

    def test_harness_with_max_retries_recovers(self):
        """Self-Harness style: re-plan on failure until success."""
        plan_calls = [0]

        class AdaptiveThinker(MockThinker):
            def plan(self, prompt):
                plan_calls[0] += 1
                if plan_calls[0] >= 3:
                    # Third try: produce a successful plan
                    return [Step("ok")]
                # First two tries: produce a failing step
                return [Step("flaky")]

        executor = MockExecutor(fail_on=["flaky"])
        harness = make_harness(AdaptiveThinker(), executor)
        result = harness.run("recover from failure", max_retries=5)
        # 3 attempts: 2 failed, 1 succeeded
        assert result.attempts == 3
        assert result.status == LoopStatus.SUCCEEDED


# ── Failure modes ──────────────────────────────────────────────

class TestFailureModes:
    def test_executor_unknown_step_fails(self):
        """Thinker produces a step that FunctionExecutor doesn't know."""
        thinker = MockThinker(fixed_plan=[Step("unknown_op")])
        executor = FunctionExecutor({})  # no handlers
        harness = make_harness(thinker, executor)
        result = harness.run("do unknown")
        assert result.status == LoopStatus.FAILED
        assert "unknown step" in result.results[0].error

    def test_handler_exception_caught(self):
        """If a handler raises, the loop catches and continues (then fails)."""
        def bad_handler(step):
            raise RuntimeError("explode")
        thinker = MockThinker(fixed_plan=[Step("boom")])
        executor = FunctionExecutor({"boom": bad_handler})
        harness = make_harness(thinker, executor)
        result = harness.run("trigger exception")
        assert result.status == LoopStatus.FAILED
        assert "explode" in result.results[0].error

    def test_history_persists_across_runs(self):
        """Loop.history grows with each run (P19 observability)."""
        thinker = MockThinker(fixed_plan=[Step("a")])
        executor = MockExecutor()
        harness = make_harness(thinker, executor)
        for i in range(3):
            harness.run(f"prompt {i}")
        assert len(harness.history) == 3
        # All distinct
        ids = {id(r) for r in harness.history}
        assert len(ids) == 3


# ── Joint with JsonThinker (lazy LLM) ─────────────────────────

class TestJointWithJsonThinker:
    """Joint: JsonThinker (lazy) + MockExecutor + Loop.

    JsonThinker._call_llm is patched so we don't need a real LLM.
    This validates the wiring without hitting the API.
    """

    def test_json_thinker_in_harness(self):
        """JsonThinker.plan() called by Loop, parsed, executed."""
        jt = JsonThinker(config={"fake": True})
        # Patch _call_llm to return a fixed plan
        with patch.object(jt, "_call_llm",
                          return_value='[{"name": "step1", "args": {}},'
                                       ' {"name": "step2", "args": {}}]'):
            executor = MockExecutor()
            harness = make_harness(jt, executor)
            result = harness.run("plan me something")
        assert result.status == LoopStatus.SUCCEEDED
        assert len(result.results) == 2

    def test_json_thinker_bad_response_fallback(self):
        """JsonThinker returns invalid JSON -> noop -> FAILED."""
        jt = JsonThinker(config={"fake": True})
        with patch.object(jt, "_call_llm", return_value="not json"):
            executor = MockExecutor(fail_on=["noop"])
            harness = make_harness(jt, executor)
            result = harness.run("test")
        # JsonThinker fell back to noop step; executor fails on noop
        assert result.status == LoopStatus.FAILED
        assert result.results[0].step_name == "noop"

    def test_json_thinker_exception_fallback(self):
        """JsonThinker._call_llm raises -> noop -> status depends on executor."""
        jt = JsonThinker(config={"fake": True})
        with patch.object(jt, "_call_llm",
                          side_effect=RuntimeError("API down")):
            # If executor accepts noop -> SUCCEEDED
            executor = MockExecutor()  # default success
            harness = make_harness(jt, executor)
            result = harness.run("test")
        # JsonThinker catches exception -> noop step; executor succeeds
        assert result.status == LoopStatus.SUCCEEDED
        assert result.results[0].step_name == "noop"
