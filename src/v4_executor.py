"""src/v4_executor.py - Executor abstract base.

Per LITERATURE (SkillOpt Microsoft 2026: 'skills as external state,
+20% accuracy'): the executor is the skill dispatcher.  It takes
a Step and returns a Result.  In production, the executor would
dispatch to file/IO/LLM/MCP tools.  In tests, MockExecutor
records calls without side effects.

This module is step 2.2 of v3.0.2 (think-execute harness).
Thinker (step 2.1) produces a Plan = List[Step].
Executor (step 2.2) executes each step.
Loop (step 2.3) drives Thinker -> Executor -> Observe.

Public API:
  Result(success, value=None, error=None)   -> dataclass
  Executor                                   -> abstract base
    .execute(step) -> Result                (subclass implements)
  MockExecutor                               -> records calls, no side effects
  FunctionExecutor(handlers: Dict[str, Callable])  -> dispatches by name
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Any, List

from src.v4_thinker import Step


@dataclass
class Result:
    """One step execution result.  Either success or error (not both)."""
    success: bool
    value: Any = None
    error: Optional[str] = None
    # Per P19: intermediate state should be observable.
    step_name: str = ""

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "value": self.value,
            "error": self.error,
            "step_name": self.step_name,
        }


# ── Abstract base ───────────────────────────────────────────────

class Executor:
    """Abstract Executor.  Subclasses implement execute()."""

    def __init__(self):
        self.call_log: List[Step] = []

    def execute(self, step: Step) -> Result:
        """Execute one Step.  Returns Result.

        Subclasses MUST implement.  Default raises NotImplementedError.
        """
        raise NotImplementedError("Executor subclasses must implement execute()")


# ── MockExecutor ────────────────────────────────────────────────

class MockExecutor(Executor):
    """MockExecutor records every step, no side effects.

    Use for tests + dry-run mode.  Returns success=True for any step
    unless `fail_on` matches the step name (per-step failure injection).
    """

    def __init__(self, fail_on: Optional[List[str]] = None,
                 default_value: Any = "ok"):
        super().__init__()
        self._fail_on = set(fail_on or [])
        self._default_value = default_value

    def execute(self, step: Step) -> Result:
        self.call_log.append(step)
        if step.name in self._fail_on:
            return Result(
                success=False,
                error=f"mock failure for {step.name}",
                step_name=step.name,
            )
        return Result(
            success=True,
            value=self._default_value,
            step_name=step.name,
        )


# ── FunctionExecutor ───────────────────────────────────────────

class FunctionExecutor(Executor):
    """FunctionExecutor dispatches by step name to a handler function.

    handler_dict: {step_name: callable(Step) -> Result}
    Unknown step name -> Result(success=False, error="unknown step").
    Handler exception  -> Result(success=False, error=str(exc)).
    """

    def __init__(self, handlers: Dict[str, Callable[[Step], Result]]):
        super().__init__()
        self._handlers = dict(handlers)

    def register(self, name: str, handler: Callable[[Step], Result]) -> None:
        """Add or replace a handler."""
        self._handlers[name] = handler

    def execute(self, step: Step) -> Result:
        self.call_log.append(step)
        if step.name not in self._handlers:
            return Result(
                success=False,
                error=f"unknown step: {step.name}",
                step_name=step.name,
            )
        try:
            return self._handlers[step.name](step)
        except Exception as e:
            return Result(
                success=False,
                error=f"handler exception: {e}",
                step_name=step.name,
            )

    @property
    def known_steps(self) -> List[str]:
        return sorted(self._handlers.keys())
