"""Tests for src/v4_loop.py - Loop controller (v3.0.2 step 2.3)."""
import pytest

from src.v4_loop import Loop, LoopResult, LoopStatus
from src.v4_thinker import MockThinker, Step, Thinker
from src.v4_executor import MockExecutor, FunctionExecutor, Result


# ── LoopStatus + LoopResult ────────────────────────────────────

class TestLoopStatus:
    def test_status_values(self):
        assert LoopStatus.SUCCEEDED.value == "SUCCEEDED"
        assert LoopStatus.FAILED.value == "FAILED"
        assert LoopStatus.PARTIAL.value == "PARTIAL"


class TestLoopResult:
    def test_default(self):
        r = LoopResult(status=LoopStatus.SUCCEEDED, plan=[])
        assert r.status == LoopStatus.SUCCEEDED
        assert r.results == []
        assert r.attempts == 1
        assert r.elapsed_s == 0.0

    def test_to_dict(self):
        r = LoopResult(
            status=LoopStatus.SUCCEEDED,
            plan=[Step("a"), Step("b")],
            results=[Result(success=True, value="ok", step_name="a"),
                     Result(success=True, value="ok", step_name="b")],
            attempts=1,
            elapsed_s=0.5,
        )
        d = r.to_dict()
        assert d["status"] == "SUCCEEDED"
        assert d["attempts"] == 1
        assert d["elapsed_s"] == 0.5
        assert len(d["plan"]) == 2
        assert len(d["results"]) == 2


# ── Basic Loop.run ──────────────────────────────────────────────

class TestBasicLoop:
    def test_empty_plan(self):
        """Thinker returns no plan -> FAILED."""
        thinker = MockThinker(fixed_plan=[])
        executor = MockExecutor()
        loop = Loop(thinker, executor)
        r = loop.run("anything")
        assert r.status == LoopStatus.FAILED
        assert r.attempts == 1

    def test_all_succeed(self):
        """All steps succeed -> SUCCEEDED."""
        thinker = MockThinker(fixed_plan=[Step("a"), Step("b")])
        executor = MockExecutor()
        loop = Loop(thinker, executor)
        r = loop.run("anything")
        assert r.status == LoopStatus.SUCCEEDED
        assert len(r.results) == 2
        assert all(rs.success for rs in r.results)

    def test_fail_fast_on_first_error(self):
        """First step fails -> stop, no more steps run."""
        thinker = MockThinker(fixed_plan=[Step("bad"), Step("never")])
        executor = MockExecutor(fail_on=["bad"])
        loop = Loop(thinker, executor)
        r = loop.run("anything")
        assert r.status == LoopStatus.FAILED
        # Only "bad" was executed; "never" was not
        assert len(r.results) == 1
        assert r.results[0].step_name == "bad"

    def test_partial_status(self):
        """Mixed success/fail with fail-fast: status=FAILED, results partial."""
        # ok succeeds, then bad fails -> fail-fast
        # results = [ok_success, bad_fail]; status = FAILED
        thinker = MockThinker(fixed_plan=[Step("ok"), Step("bad")])
        executor = MockExecutor(fail_on=["bad"])
        loop = Loop(thinker, executor)
        r = loop.run("anything")
        # Fail-fast: both ran, bad failed
        assert r.status == LoopStatus.FAILED
        assert len(r.results) == 2
        assert r.results[0].step_name == "ok"
        assert r.results[1].step_name == "bad"

    def test_function_executor_dispatch(self):
        """Loop + FunctionExecutor (joint)."""
        thinker = MockThinker(fixed_plan=[Step("read"), Step("write")])
        fe = FunctionExecutor({
            "read": lambda s: Result(success=True, value="content", step_name=s.name),
            "write": lambda s: Result(success=True, value="wrote", step_name=s.name),
        })
        loop = Loop(thinker, fe)
        r = loop.run("anything")
        assert r.status == LoopStatus.SUCCEEDED
        assert r.results[0].value == "content"
        assert r.results[1].value == "wrote"


# ── Retry / re-plan ────────────────────────────────────────────

class TestRetry:
    def test_no_retry_by_default(self):
        """Default max_retries=0 means single pass."""
        thinker = MockThinker(fixed_plan=[Step("bad")])
        executor = MockExecutor(fail_on=["bad"])
        loop = Loop(thinker, executor)
        r = loop.run("anything")
        assert r.attempts == 1

    def test_retry_max_2(self):
        """max_retries=2 means up to 3 attempts total."""
        # Use a counter to simulate 'fix' on retry
        plan_calls = [0]

        class FlakyThinker(Thinker):
            def plan(self, prompt):
                plan_calls[0] += 1
                if plan_calls[0] >= 2:
                    return [Step("ok")]  # succeed on retry
                return [Step("bad")]

        executor = MockExecutor(fail_on=["bad"])
        loop = Loop(FlakyThinker(), executor)
        r = loop.run("anything", max_retries=2)
        # First attempt failed, second attempt succeeded
        assert r.attempts == 2
        assert r.status == LoopStatus.SUCCEEDED

    def test_retry_exhausted(self):
        """max_retries=2 with persistent failure -> 3 attempts, FAILED."""
        class AlwaysBad(Thinker):
            def plan(self, prompt):
                return [Step("bad")]

        executor = MockExecutor(fail_on=["bad"])
        loop = Loop(AlwaysBad(), executor)
        r = loop.run("anything", max_retries=2)
        assert r.attempts == 3  # 1 + 2 retries
        assert r.status == LoopStatus.FAILED


# ── History + observability ─────────────────────────────────────

class TestHistory:
    def test_history_grows(self):
        thinker = MockThinker(fixed_plan=[Step("a")])
        executor = MockExecutor()
        loop = Loop(thinker, executor)
        assert len(loop.history) == 0
        loop.run("first")
        assert len(loop.history) == 1
        loop.run("second")
        assert len(loop.history) == 2

    def test_history_records_outcomes(self):
        thinker = MockThinker(fixed_plan=[Step("a")])
        executor = MockExecutor()
        loop = Loop(thinker, executor)
        loop.run("a")
        loop.run("b")
        assert loop.history[0].plan[0].name == "a"
        assert loop.history[1].plan[0].name == "a"
        # Same plan both times, but history distinct
        assert loop.history[0] is not loop.history[1]


# ── Joint end-to-end ───────────────────────────────────────────

class TestJointEndToEnd:
    """Full MockThinker + MockExecutor + Loop (no LLM, no IO)."""

    def test_real_world_simulation(self):
        # Thinker: produces a 3-step plan
        thinker = MockThinker(fixed_plan=[
            Step("read", args={"file": "x.py"}),
            Step("analyze"),
            Step("write", args={"output": "result.md"}),
        ])
        # Executor: all succeed with custom values
        executor = MockExecutor(default_value="done")
        loop = Loop(thinker, executor)
        r = loop.run("analyze x.py and write result")

        # Verify
        assert r.status == LoopStatus.SUCCEEDED
        assert len(r.results) == 3
        assert [rs.step_name for rs in r.results] == ["read", "analyze", "write"]
        assert all(rs.value == "done" for rs in r.results)
        # History grew
        assert len(loop.history) == 1
