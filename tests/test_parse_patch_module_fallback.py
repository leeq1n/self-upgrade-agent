"""Regression: _parse_patch handles real LLM shape (no module field).

Per user 2026-07-12: re-ran daily-loop, 10 rounds 0/10 KEPT.
Per 我 first fix (004f47b): added markdown fence fallback — INSUFFICIENT.
Per real LLM investigation: LLM returns valid JSON {function, test}, NO 'module'.
Per 你 '排除bug' push (2nd round): fix target_module fallback.

Per P18: real failure -> real fix -> real regression test.
"""
from src.v2_agent import _parse_patch


class TestParsePatchModuleFallback:
    """Per P18: _parse_patch handles real LLM shape (no module)."""

    def test_real_llm_shape_json_no_module(self):
        """_parse_patch: JSON with {function, test} but no module.
        Real LLM (MiniMax-M2) returns this shape → fallback to target_module.
        This is the bug behind 0/10 KEPT.
        """
        response = '''{"function": "def plan_task(): pass", "test": "def test_plan_task(): assert True"}'''
        result = _parse_patch(response, target_module="core/planner.py")
        assert result is not None, "Should NOT return None (the bug)"
        assert result.module == "core/planner.py", \
            f"module should fallback to target_module, got: {result.module!r}"
        assert "def plan_task" in result.function
        assert "def test_plan_task" in result.test

    def test_json_with_module_unchanged(self):
        """_parse_patch: JSON with module → backward compat (uses JSON module)."""
        response = '''{"function": "def foo(): pass", "test": "def test_foo(): pass", "module": "core/foo.py"}'''
        result = _parse_patch(response, target_module="core/other.py")
        assert result is not None
        # JSON.module wins when present (per LITERATURE)
        assert result.module == "core/foo.py"

    def test_empty_target_module_with_no_json_module(self):
        """_parse_patch: no JSON.module + empty target_module → still valid Patch."""
        response = '''{"function": "def foo(): pass", "test": "def test_foo(): pass"}'''
        result = _parse_patch(response, target_module="")
        # module is empty string but Patch returned (downstream may fill it)
        assert result is not None
        assert result.module == ""

    def test_prose_with_fences_uses_target_module(self):
        """_parse_patch: prose + fences → fallback to target_module."""
        response = """Here is the fix:

```python
def foo(x):
    return x + 1
```

And the test:

```python
def test_foo():
    assert foo(2) == 3
```
"""
        result = _parse_patch(response, target_module="core/x.py")
        assert result is not None
        assert result.module == "core/x.py"
