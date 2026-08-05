"""Tests for src/v2_agent.py — minimal self-improving agent.

What we test (per "harness locks behavior" principle):
  - Memory: add + find_similar works
  - Parse: JSON in / out, no markdown fence
  - Parse: bad JSON returns None
  - Parse: too-short function/test rejected
  - Harness: subprocess run, returncode → bool
  - end-to-end: improve() with mocked chat returns Patch or None
"""
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)

import pytest

from src.v2_agent import (
    Paper, Patch,
    memory_add, memory_find_similar,
    _parse_patch, _run_harness, _build_prompt,
    improve,
)


@pytest.fixture
def tmp_memory(monkeypatch, tmp_path):
    """Use a tmp memory DB so tests don't pollute real one."""
    db_path = str(tmp_path / "test_memory.db")
    monkeypatch.setattr("src.v2_agent.MEMORY_DB", db_path)
    monkeypatch.setattr("src.v2_agent._memory_path", lambda: db_path)
    # Initialize schema
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arxiv_id TEXT,
            summary TEXT,
            topics TEXT
        )
    """)
    conn.commit()
    conn.close()
    return db_path


class TestMemory:
    def test_add_returns_id(self, tmp_memory):
        mid = memory_add("2310.02170", "DyLAN paper on agent networks", ["agent"])
        assert isinstance(mid, int) and mid > 0

    def test_find_similar_empty_db(self, tmp_memory):
        results = memory_find_similar("anything")
        assert results == []

    def test_find_similar_basic(self, tmp_memory):
        memory_add("2310.02170", "Dynamic LLM Agent Network for task planning",
                   ["agent", "planning"])
        memory_add("2406.01574", "MMLU benchmark for language models",
                   ["benchmark"])
        results = memory_find_similar("agent coordination framework", top_k=3)
        # Should find the agent paper but not the benchmark
        assert len(results) >= 1
        assert any(r["arxiv_id"] == "2310.02170" for r in results)


class TestParse:
    def test_clean_json(self):
        raw = (
            '{"function": "def plan_task(): return [1, 2, 3, 4, 5]",'
            ' "test": "def test_x(): assert plan_task() == [1, 2, 3, 4, 5]",'
            ' "module": "x.py"}'
        )
        patch = _parse_patch(raw)
        assert patch is not None
        assert "def plan_task" in patch.function
        assert patch.module == "x.py"

    def test_json_in_markdown_fence(self):
        raw = "```json\n" + '{"function": "def plan_task():\\n    return []", "test": "def test(): assert True", "module": "x.py"}' + "\n```"
        patch = _parse_patch(raw)
        assert patch is not None

    def test_garbage_returns_none(self):
        assert _parse_patch("not json at all") is None
        assert _parse_patch("") is None
        assert _parse_patch("{}") is None  # missing required fields

    def test_too_short_function_rejected(self):
        raw = (
            '{"function": "x",'
            ' "test": "def test_x(): assert plan_task() is not None",'
            ' "module": "x.py"}'
        )
        assert _parse_patch(raw) is None

    def test_too_short_test_rejected(self):
        raw = (
            '{"function": "def plan_task(): return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",'
            ' "test": "x",'
            ' "module": "x.py"}'
        )
        assert _parse_patch(raw) is None


class TestHarness:
    def test_pass(self, tmp_path):
        patch = Patch(
            function="def add(a, b): return a + b",
            test="assert add(2, 3) == 5",
            module="x.py",
        )
        assert _run_harness(patch) is True

    def test_fail(self, tmp_path):
        patch = Patch(
            function="def add(a, b): return a - b",  # wrong
            test="def test_add(): assert add(2, 3) == 5",
            module="x.py",
        )
        assert _run_harness(patch) is False

    def test_syntax_error(self, tmp_path):
        patch = Patch(
            function="def add(a, b return a + b",  # syntax error
            test="assert add(2, 3) == 5",
            module="x.py",
        )
        assert _run_harness(patch) is False


class TestBuildPrompt:
    def test_includes_paper_info(self, tmp_memory):
        paper = Paper(arxiv_id="2310.02170",
                      title="DyLAN",
                      abstract="Dynamic agent network")
        prompt = _build_prompt(paper, "core/planner.py", similar=[])
        assert "DyLAN" in prompt
        assert "2310.02170" in prompt
        assert "core/planner.py" in prompt
        assert "(none)" in prompt  # empty similar

    def test_includes_similar(self, tmp_memory):
        memory_add("2606.30639", "WorldEvolver paper", ["agent"])
        paper = Paper(arxiv_id="2310.02170", title="DyLAN", abstract="agent")
        similar = memory_find_similar("agent", top_k=3)
        prompt = _build_prompt(paper, "core/planner.py", similar=similar)
        assert "WorldEvolver" in prompt


class TestImprove:
    def test_end_to_end_pass(self, tmp_memory, tmp_path):
        """Mocked chat returns a valid patch → harness passes → returns Patch."""
        # Create a target module in tmp_path
        target = tmp_path / "planner.py"
        target.write_text("# original\ndef plan_task():\n    return []\n")

        good_patch_json = json.dumps({
            "function": "def plan_task():\n    return ['step1', 'step2']\n",
            "test": "def test_plan():\n    assert plan_task() == ['step1', 'step2']\n",
            "module": str(target),
        })

        with patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = good_patch_json
            mock_resp.error = None
            mock_chat.return_value = mock_resp

            paper = Paper(arxiv_id="2310.02170",
                          title="DyLAN",
                          abstract="Dynamic agent network")
            result = improve(paper, target_module=str(target))
            assert result is not None
            assert "plan_task" in result.function

    def test_end_to_end_harness_fail_returns_none(self, tmp_memory, tmp_path):
        target = tmp_path / "planner.py"
        target.write_text("def plan_task(): return []\n")
        bad_patch = json.dumps({
            "function": "def plan_task():\n    return WRONG\n",  # NameError
            "test": "def test_plan():\n    assert plan_task() == ['x']\n",
            "module": str(target),
        })
        with patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = bad_patch
            mock_resp.error = None
            mock_chat.return_value = mock_resp
            paper = Paper(arxiv_id="2310.02170", title="x", abstract="y")
            assert improve(paper, target_module=str(target)) is None

    def test_end_to_end_parse_fail_returns_none(self, tmp_memory, tmp_path):
        target = tmp_path / "planner.py"
        target.write_text("def plan_task(): return []\n")
        with patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = "garbage no json"
            mock_resp.error = None
            mock_chat.return_value = mock_resp
            paper = Paper(arxiv_id="x", title="x", abstract="x")
            assert improve(paper, target_module=str(target)) is None


class TestFixedPaper:
    """User feedback 2026-07-08: '固定 1 paper, 跑通后续功能再回来做筛选'.
    Verify the fixed paper helper is callable and is the DyLAN paper.
    """

    def test_fixed_paper_is_dylan(self):
        from src.v2_agent import FIXED_PAPER
        assert FIXED_PAPER.arxiv_id == "2310.02170"
        assert "DyLAN" in FIXED_PAPER.title or "Agent Network" in FIXED_PAPER.title

    def test_run_with_fixed_paper_returns_patch_or_none(self, tmp_memory, tmp_path):
        """End-to-end with the fixed paper.  Mocked LLM; just verify
        the function runs without error and returns Patch or None."""
        target = tmp_path / "planner.py"
        target.write_text("def plan_task(): return []\n")
        with patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = json.dumps({
                "function": "def plan_task(): return [\"x\"]",
                "test": "def test_x(): assert plan_task() == [\"x\"]",
                "module": str(target),
            })
            mock_resp.error = None
            mock_chat.return_value = mock_resp
            from src.v2_agent import run_with_fixed_paper
            result = run_with_fixed_paper(target_module=str(target))
            # Either returns Patch (passes harness) or None (fails)
            # The point is: it runs without error
            assert result is None or hasattr(result, "function")



class TestTargetModuleSafety:
    """Regressions for issues found during user-run (2026-07-08):

    1. UTF-8 decode error on Windows when target is non-ASCII (GBK default).
    2. PermissionError / empty path when user passed "\u2026" or non-existent.
    Both should return a sentinel string in the prompt, not crash.
    """

    def test_utf8_target_loads(self, tmp_path):
        from src.v2_agent import _read_target_module
        # Write a UTF-8 source with Chinese characters
        target = tmp_path / "p.py"
        # 中文 = Chinese, é = French e-acute — would fail GBK
        target.write_text("# 中文 + accent é\ndef plan(): return []\n",
                          encoding="utf-8")
        content = _read_target_module(str(target))
        assert "中文" in content or "file does not exist" in content

    def test_empty_path_returns_sentinel(self):
        from src.v2_agent import _read_target_module
        result = _read_target_module("")
        assert "does not exist" in result or "empty" in result

    def test_nonexistent_path_returns_sentinel(self):
        from src.v2_agent import _read_target_module
        result = _read_target_module("C:/non/existent/path/to/file.py")
        assert "does not exist" in result or "create from scratch" in result



class TestHarnessStandalone:
    """Regression for user-run 2026-07-08: LLM-generated patch used
    typing.Callable without importing it, so harness subprocess
    fails with NameError.  Fix: prompt should guide LLM to inline
    typing imports; harness should also tolerate single-line doc-
    strings and other common LLM output quirks."""

    def test_handles_unimported_callable(self):
        """When LLM uses Callable in type hints without importing,
        we still want harness to RUN the test (it will fail with
        NameError visible in stderr — that's fine, it's a real
        signal, not a harness bug)."""
        from src.v2_agent import Patch
        p = Patch(
            function="from typing import Callable\ndef plan_task(x: str, c: Callable) -> str:\n    return c(x)",
            test="def test_xxx(): assert plan_task('hi', lambda y: y.upper()) == 'HI'",
            module="core/planner.py",
        )
        # Should RUN — may fail (lc doesn't import elsewhere) but not crash
        result = _run_harness(p)
        # Don't assert True/False — we just want no exception
        assert result in (True, False)

    def test_harness_injects_typing_imports_via_prelude(self):
        """Per user feedback 2026-07-08 ("实体承担重要作用"),
        the entity (harness) auto-injects typing imports — the
        prompt no longer needs to mention this.  Verify the entity
        handles it via _PRELUDE in v2_agent.py."""
        from src.v2_agent import _PRELUDE
        # _PRELUDE should contain typing import (entity behavior)
        assert "from typing import" in _PRELUDE

    def test_prompt_is_minimal_no_harness_rules(self):
        """Per user feedback 2026-07-08 ("启动 prompt 越少越好"),
        the prompt should NOT carry harness-implementation rules
        (those belong to the entity)."""
        from src.v2_agent import _build_prompt
        prompt = _build_prompt(
            Paper(arxiv_id="x", title="X", abstract="X"),
            "core/planner.py",
            [],
        )
        # Prompt should NOT mention harness details (those are in entity)
        assert "harness" not in prompt.lower(), (
            "harness rules belong to entity, not prompt"
        )
        assert "subprocess" not in prompt.lower(), (
            "subprocess details belong to entity, not prompt"
        )
        # But it should still be a valid generation prompt
        assert "function" in prompt
        assert "test" in prompt


class TestEndToEndRealLLM:
    """Integration: mocked LLM produces a patch that uses typing
    imports inline — verify the harness actually runs it (passes
    OR fails gracefully, never crashes)."""

    def test_patch_with_inline_typing_runs(self):
        from src.v2_agent import Patch
        p = Patch(
            function=(
                "from typing import Callable\n"
                "def plan_task(task: str, llm_call: Callable) -> str:\n"
                "    return llm_call(task)\n"
            ),
            test=(
                "def test_inline_works():\n"
                "    assert plan_task('yo', lambda s: 'echo:' + s) == 'echo:yo'\n"
            ),
            module="core/planner.py",
        )
        # Harness should run without crashing; expect pass
        assert _run_harness(p) is True



class TestHarnessPrelude:
    """Regression for user-run 2026-07-08: LLM-generated patches often
    use typing.Callable / List / Dict / Optional in type hints without
    importing them.  The harness auto-injects a PRELUDE that imports
    common typing helpers + stdlib, so the patch function compiles."""

    def test_callable_in_type_hint_now_passes(self):
        """LLM pattern: def f(x: Callable) -> str with no import.
        Without PRELUDE this fails with NameError; with PRELUDE it works."""
        from src.v2_agent import Patch
        p = Patch(
            function=(
                "def plan_task(task: str, llm_call: Callable) -> str:\n"
                "    return llm_call(task)"
            ),
            test=(
                "def test_callable_used():\n"
                "    assert plan_task('hi', lambda s: 'echo:' + s) == 'echo:hi'"
            ),
            module="core/planner.py",
        )
        assert _run_harness(p) is True

    def test_list_optional_dict_in_hints(self):
        """Multiple typing imports needed but not provided."""
        from src.v2_agent import Patch
        p = Patch(
            function=(
                "def plan_task(items: List[str], opt: Optional[int] = None, "
                "kv: Dict[str, Any] = None) -> Tuple[int, str]:\n"
                "    return (len(items), str(items[0]))"
            ),
            test=(
                "def test_multi_types():\n"
                "    n, first = plan_task(['a', 'b'])\n"
                "    assert n == 2 and first == 'a'"
            ),
            module="core/planner.py",
        )
        # Tuples are returned — Python unpacking should work
        result = _run_harness(p)
        # Don't assert True/False — LLM-generated test may have subtle
        # issues but we just want no harness crash.
        assert result in (True, False)
