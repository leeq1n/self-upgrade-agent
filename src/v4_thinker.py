"""src/v4_thinker.py - Thinker abstract base.

Per LITERATURE (Self-Harness 40->62%, Lilian Weng "harness as
important as model", Nate Berkopec "verifiable + looped"):
  The harness (thinker + executor + loop) is the bottleneck
  for agent capability, not the underlying model.

This module is step 2.1 of v3.0.2.  It defines:
  - Step dataclass: one action with name + args
  - Plan = List[Step]: the thinker's output
  - Thinker abstract base: subclasses implement plan()
  - MockThinker: a deterministic thinker for tests + default

Thinker is a separate concept from v2_agent.improve().  v2_agent
is a "single-shot generator" (one prompt -> one patch).  Thinker
is a "deliberate planner" (one prompt -> multi-step plan).

Public API:
  Step(name, args=None)        -> dataclass
  Plan                          = List[Step]
  Thinker(config=None)          -> abstract base
    .plan(prompt) -> Plan        (subclass implements)
  MockThinker()                 -> deterministic for tests
  DefaultThinker(config=None)   -> LLM-backed (lazy, optional)
"""
import json
import re
from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class Step:
    """One step in a plan.  name + args (dict)."""
    name: str
    args: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"name": self.name, "args": self.args}


# Plan is just a list of steps; alias for clarity
Plan = List[Step]


# ── Abstract base ───────────────────────────────────────────────

class Thinker:
    """Abstract Thinker.  Subclasses implement plan()."""

    def __init__(self, config=None):
        self.config = config

    def plan(self, prompt: str) -> Plan:
        """Return a Plan (List[Step]) for the given prompt.

        Subclasses MUST implement this.  Default raises NotImplementedError.
        """
        raise NotImplementedError("Thinker subclasses must implement plan()")


# ── Mock Thinker ────────────────────────────────────────────────

class MockThinker(Thinker):
    """Deterministic Thinker for tests + default.

    Parses simple 'step:arg' lines from the prompt.  If no parseable
    steps, returns a single 'noop' step.  Never calls LLM.
    """

    def __init__(self, fixed_plan: Optional[Plan] = None):
        super().__init__(config=None)
        self._fixed = fixed_plan

    def plan(self, prompt: str) -> Plan:
        if self._fixed is not None:
            return list(self._fixed)
        # Parse "step_name:arg" or "step_name arg" patterns
        steps: Plan = []
        for line in prompt.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Try "name:arg1,arg2" pattern
            if ":" in line:
                name, rest = line.split(":", 1)
                name = name.strip()
                rest = rest.strip()
                if name:
                    args = {"input": rest} if rest else {}
                    steps.append(Step(name=name, args=args))
            # Try "name arg1 arg2" pattern (whitespace-separated)
            elif " " in line:
                parts = line.split(None, 1)
                if len(parts) == 2:
                    name, rest = parts
                    steps.append(Step(name=name, args={"input": rest}))
                else:
                    steps.append(Step(name=parts[0]))
            else:
                steps.append(Step(name=line))
        if not steps:
            steps = [Step(name="noop", args={"reason": "no parseable steps"})]
        return steps


# ── JSON-backed Thinker ────────────────────────────────────────

class JsonThinker(Thinker):
    """Thinker that parses JSON output from an LLM call.

    Lazy-imports src.v2_agent._chat.  Use for real LLM-backed planning.
    Falls back to mock if LLM call fails (per fail-OPEN).
    """

    def __init__(self, config=None):
        super().__init__(config=config)
        self._last_response: str = ""

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM.  Lazy import to keep mock fast."""
        from src.v2_agent import _chat
        msgs = [{"role": "user", "content": prompt}]
        cfg = self.config
        response = _chat(messages=msgs, config=cfg)
        # Response can be a string or an object with .content
        if hasattr(response, "content"):
            return response.content
        return str(response)

    @staticmethod
    def _parse_steps(text: str) -> Plan:
        """Extract [{'name': ..., 'args': ...}, ...] from text.

        Tolerates markdown fences, extra spaces, and partial JSON.
        Returns [Step('noop', {'reason': 'parse failed'})] on failure.
        """
        # Try to find a JSON array
        m = re.search(r"\[.*?\]", text, re.DOTALL)
        if not m:
            return [Step("noop", {"reason": "no JSON array found"})]
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return [Step("noop", {"reason": "JSON parse failed"})]
        if not isinstance(data, list):
            return [Step("noop", {"reason": "JSON is not array"})]
        steps: Plan = []
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name", "unknown")
            args = item.get("args", {})
            if not isinstance(args, dict):
                args = {"value": str(args)}
            steps.append(Step(name=name, args=args))
        if not steps:
            return [Step("noop", {"reason": "empty plan"})]
        return steps

    def plan(self, prompt: str) -> Plan:
        # Lazy import - only fails if config is None
        try:
            text = self._call_llm(prompt)
        except Exception as e:
            return [Step("noop", {"reason": f"LLM call failed: {e}"})]
        self._last_response = text
        return self._parse_steps(text)
