"""v1.8.0: real unit tests for core/planner.py.

These are the HARNESS — independent Python tests that verify
plan_task behavior.  They do NOT call any LLM.  They use a
fake llm_call (deterministic function) to drive the planner.

Why these exist: v1.7.0's evaluate was 100% LLM-judged.  That
is "LLM grading LLM" — not a real harness.  These tests are
the FIRST independent signal.  should_promote in src/evaluate.py
will be updated to weight harness >= LLM benchmark.

Tests are simple, fast, and cover the documented contract:
  - plan_task returns a list of strings
  - plan_task handles empty/short/long/unicode input
  - plan_task handles llm_call returning various formats
  - plan_task doesn't crash on edge inputs
"""
import os, sys
import pytest

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)


def fake_llm(prompt: str) -> str:
    """Deterministic stand-in for an LLM call.  Returns 3 numbered steps."""
    return "1. First step\n2. Second step\n3. Third step"


def test_plan_task_returns_list_of_strings():
    """The contract: plan_task returns a list[str]."""
    from core.planner import plan_task
    result = plan_task("Plan a trip", fake_llm)
    assert isinstance(result, list), f"expected list, got {type(result)}"
    for s in result:
        assert isinstance(s, str), f"each item must be str, got {type(s)}"


def test_plan_task_handles_empty_task():
    """Empty string task must not crash, must return a list."""
    from core.planner import plan_task
    result = plan_task("", fake_llm)
    assert isinstance(result, list)
    # When the input is empty, we still expect a fallback (e.g. "Do: ")
    assert len(result) >= 1


def test_plan_task_handles_very_long_input():
    """10K character input must not hang or crash (timeout safety)."""
    from core.planner import plan_task
    long_task = "step " * 5000  # 25K chars
    # Must complete in reasonable time
    import time
    t0 = time.time()
    result = plan_task(long_task[:10000], fake_llm)
    elapsed = time.time() - t0
    assert elapsed < 2.0, f"too slow on 10K input: {elapsed:.2f}s"
    assert isinstance(result, list)


def test_plan_task_handles_unicode():
    """Unicode (CJK, emoji) must not crash."""
    from core.planner import plan_task
    unicode_task = "计划一次东京之旅 🗼 で Tokyo に行く"
    result = plan_task(unicode_task, fake_llm)
    assert isinstance(result, list)


def test_plan_task_handles_llm_returning_nonsense():
    """If llm_call returns empty/whitespace, plan_task must fall back gracefully."""
    from core.planner import plan_task

    def empty_llm(prompt):
        return ""

    result = plan_task("do the thing", empty_llm)
    # Should fall back to "Do: <task>" (per current implementation)
    assert isinstance(result, list)
    assert len(result) >= 1
    # The fallback is a string starting with "Do: "
    assert any("Do: " in s for s in result), f"expected 'Do: ' fallback, got {result}"


def test_plan_task_handles_llm_returning_unstructured_text():
    """LLM returns a paragraph, not numbered steps.  Should still extract something."""
    from core.planner import plan_task

    def verbose_llm(prompt):
        return "Well, I'd suggest you do a few things. First, think about it. Then act."

    result = plan_task("do the thing", verbose_llm)
    # Should not crash; whatever it returns must be a list of strings
    assert isinstance(result, list)
    for s in result:
        assert isinstance(s, str)


def test_plan_task_extracts_numbered_steps():
    """LLM returns '1. step one\\n2. step two\\n3. step three' — should extract all 3."""
    from core.planner import plan_task

    def numbered_llm(prompt):
        return "1. Plan the route\n2. Book transport\n3. Reserve hotel"

    result = plan_task("plan a trip", numbered_llm)
    assert len(result) == 3, f"expected 3 steps, got {len(result)}: {result}"
    assert "Plan the route" in result[0]


def test_plan_task_handles_special_characters():
    """Code blocks, URLs, JSON in input must not break the parser."""
    from core.planner import plan_task
    special = """
    Implement this:
    ```python
    def hello(): return "world"
    ```
    See https://example.com/path?q=1&r=2
    {"key": "value", "list": [1, 2, 3]}
    """
    result = plan_task(special, fake_llm)
    assert isinstance(result, list)
