"""Regression tests for _parse_patch (per P18 + 你 '排除bug' push).

Per user 2026-07-12: ran 10 rounds, all 30 attempts returned NO_PATCH.
Root cause: LLM ignores 'Return JSON' instruction, returns prose + code fences.
Fix: _parse_patch now extracts from ```python fences as fallback.

Per P18 (failure -> regression test):
- Real bug: 0/10 KEPT success rate (user reproduction)
- Fix: _parse_patch markdown fence fallback
- These tests prevent recurrence.
"""
import pytest

from src.v2_agent import _parse_patch


class TestParsePatchRegression:
    """Per P18 regression: _parse_patch handles LLM prose responses."""

    def test_json_response_still_works(self):
        """_parse_patch: JSON response still parses (backward compat)."""
        response = '{"function": "def foo(): pass", "test": "def test_foo(): assert foo() == None", "module": "core/x.py"}'
        result = _parse_patch(response)
        assert result is not None
        assert result.function == "def foo(): pass"
        assert result.test.startswith("def test_foo")
        assert result.module == "core/x.py"

    def test_prose_with_code_fences_extracted(self):
        """_parse_patch: prose + ```python fences (the bug case)."""
        response = """Here is the improved function:

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
        result = _parse_patch(response)
        assert result is not None
        assert "def foo" in result.function
        assert "def test_" in result.test

    def test_single_fence_returns_none(self):
        """_parse_patch: only 1 fence (no test) -> None."""
        response = """Here is code:
```python
def foo(x):
    return x + 1
```
"""
        result = _parse_patch(response)
        assert result is None  # Need 2 fences (fn + test)

    def test_empty_response_returns_none(self):
        """_parse_patch: empty -> None."""
        assert _parse_patch("") is None

    def test_garbage_response_returns_none(self):
        """_parse_patch: garbage -> None."""
        assert _parse_patch("blah blah no code") is None

    def test_json_no_module_returns_patch_with_empty_module(self):
        """_parse_patch: JSON without module returns Patch (module=""),
        caller (improve()) fills target_module via separate parameter.

        Note: This test was updated per P18 after commit 0359908 — the
        real fix uses target_module parameter (not fence fallback) when
        JSON has function+test but no module.
        """
        json_no_module = '{"function": "def foo(): pass", "test": "def test_foo(): pass"}'
        result = _parse_patch(json_no_module)
        # Now returns Patch with empty module (caller fills via target_module)
        assert result is not None
        assert result.module == ""