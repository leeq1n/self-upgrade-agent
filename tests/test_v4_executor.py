"""Tests for src/v4_executor.py - Executor abstraction (v3.0.2 step 2.2)."""
import pytest

from src.v4_executor import (
    Result, Executor, MockExecutor, FunctionExecutor,
)
from src.v4_thinker import Step


# ── Result dataclass ───────────────────────────────────────────

class TestResult:
    def test_result_success(self):
        r = Result(success=True, value=42)
        assert r.success is True
        assert r.value == 42
        assert r.error is None
        assert r.step_name == ""

    def test_result_error(self):
        r = Result(success=False, error="boom")
        assert r.success is False
        assert r.value is None
        assert r.error == "boom"

    def test_result_step_name(self):
        r = Result(success=True, value="ok", step_name="read")
        assert r.step_name == "read"

    def test_result_to_dict(self):
        r = Result(success=True, value="ok", step_name="read")
        d = r.to_dict()
        assert d == {"success": True, "value": "ok",
                     "error": None, "step_name": "read"}


# ── Abstract Executor ──────────────────────────────────────────

class TestAbstractExecutor:
    def test_abstract_execute_raises(self):
        e = Executor()
        with pytest.raises(NotImplementedError):
            e.execute(Step(name="x"))

    def test_executor_call_log_starts_empty(self):
        e = Executor()
        assert e.call_log == []


# ── MockExecutor ───────────────────────────────────────────────

class TestMockExecutor:
    def test_default_success(self):
        m = MockExecutor()
        r = m.execute(Step(name="read"))
        assert r.success is True
        assert r.value == "ok"
        assert r.step_name == "read"

    def test_records_call(self):
        m = MockExecutor()
        s = Step(name="write", args={"file": "x.py"})
        m.execute(s)
        assert m.call_log == [s]

    def test_records_multiple_calls(self):
        m = MockExecutor()
        m.execute(Step(name="a"))
        m.execute(Step(name="b"))
        m.execute(Step(name="c"))
        assert [s.name for s in m.call_log] == ["a", "b", "c"]

    def test_fail_on(self):
        m = MockExecutor(fail_on=["bad_step"])
        r = m.execute(Step(name="bad_step"))
        assert r.success is False
        assert "mock failure" in r.error

    def test_fail_on_doesnt_affect_other_steps(self):
        m = MockExecutor(fail_on=["bad"])
        r1 = m.execute(Step(name="good"))
        r2 = m.execute(Step(name="bad"))
        assert r1.success is True
        assert r2.success is False

    def test_custom_default_value(self):
        m = MockExecutor(default_value={"data": [1, 2, 3]})
        r = m.execute(Step(name="fetch"))
        assert r.value == {"data": [1, 2, 3]}


# ── FunctionExecutor ───────────────────────────────────────────

class TestFunctionExecutor:
    def test_dispatches_to_handler(self):
        def read_handler(step):
            return Result(success=True, value=f"read: {step.args.get('path', '')}",
                         step_name=step.name)
        fe = FunctionExecutor({"read": read_handler})
        r = fe.execute(Step(name="read", args={"path": "/etc/hosts"}))
        assert r.success is True
        assert r.value == "read: /etc/hosts"

    def test_unknown_step_fails(self):
        fe = FunctionExecutor({})
        r = fe.execute(Step(name="unknown"))
        assert r.success is False
        assert "unknown step" in r.error

    def test_handler_exception_caught(self):
        def bad_handler(step):
            raise ValueError("nope")
        fe = FunctionExecutor({"bad": bad_handler})
        r = fe.execute(Step(name="bad"))
        assert r.success is False
        assert "handler exception" in r.error
        assert "nope" in r.error

    def test_register_adds_handler(self):
        fe = FunctionExecutor({})
        assert "new_step" not in fe.known_steps
        fe.register("new_step", lambda s: Result(success=True, value="x",
                                                  step_name=s.name))
        assert "new_step" in fe.known_steps

    def test_register_replaces_handler(self):
        calls = []
        def handler1(step):
            calls.append("h1")
            return Result(success=True, step_name=step.name)
        def handler2(step):
            calls.append("h2")
            return Result(success=True, step_name=step.name)
        fe = FunctionExecutor({"x": handler1})
        fe.register("x", handler2)  # replace
        fe.execute(Step(name="x"))
        assert calls == ["h2"]

    def test_known_steps_sorted(self):
        fe = FunctionExecutor({
            "z": lambda s: Result(success=True),
            "a": lambda s: Result(success=True),
            "m": lambda s: Result(success=True),
        })
        assert fe.known_steps == ["a", "m", "z"]

    def test_records_call(self):
        fe = FunctionExecutor({})
        s = Step(name="x", args={"k": 1})
        fe.execute(s)
        assert s in fe.call_log


# ── Joint with v4_thinker ──────────────────────────────────────

class TestJointWithThinker:
    """Joint: use Thinker + Executor together (small integration)."""

    def test_thinker_plan_then_executor_runs(self):
        from src.v4_thinker import MockThinker
        # 1. Thinker produces plan
        thinker = MockThinker()
        plan = thinker.plan("read: /etc/foo\nwrite: /tmp/out")
        assert len(plan) == 2

        # 2. Executor runs plan
        results = []
        fe = FunctionExecutor({
            "read": lambda s: Result(success=True, value="file content",
                                       step_name=s.name),
            "write": lambda s: Result(success=True, value=f"wrote {s.args.get('input')}",
                                        step_name=s.name),
        })
        for step in plan:
            results.append(fe.execute(step))

        # 3. All succeeded
        assert all(r.success for r in results)
        assert results[0].value == "file content"
        assert results[1].value == "wrote /tmp/out"

    def test_mock_executor_with_mock_thinker(self):
        from src.v4_thinker import MockThinker
        thinker = MockThinker()
        plan = thinker.plan("step1: x\nstep2: y")
        m = MockExecutor()
        results = [m.execute(s) for s in plan]
        assert all(r.success for r in results)
        # MockExecutor records every step
        assert [s.name for s in m.call_log] == ["step1", "step2"]
