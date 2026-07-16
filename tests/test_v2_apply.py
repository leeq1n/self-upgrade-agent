"""Tests for src/v2_apply.py — atomic apply Patch to target module.

These tests verify:
  - Unit: snapshot/restore/atomic_write mechanics
  - Unit: AST-based plan_task replacement
  - Joint: apply_patch() to a real file, run smoke test, validate
  - Joint: revert restores original byte-for-byte
  - Edge cases: syntax error in patch → revert; no plan_task → append;
    target file doesn't exist → FAILED
"""
import os
import sys
import tempfile
import subprocess

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)

import pytest

from src.v2_apply import (
    apply_patch, revert, cleanup_snapshot,
    _atomically_write, _snapshot, _restore,
    _replace_plan_task, _append_plan_task, _validate_syntax,
    ApplyResult,
)
from src.v2_agent import Patch


# ─────────────────────────────────────────────────────────────
# Unit tests — pure mechanics
# ─────────────────────────────────────────────────────────────

class TestAtomicWrite:
    def test_writes_correct_content(self, tmp_path):
        path = str(tmp_path / "a.txt")
        _atomically_write(path, "hello world")
        with open(path) as f:
            assert f.read() == "hello world"

    def test_leaves_no_tempfile_on_success(self, tmp_path):
        path = str(tmp_path / "a.txt")
        _atomically_write(path, "content")
        # No .apply_*.tmp file should remain
        leftovers = [p for p in os.listdir(tmp_path) if p.startswith(".apply_")]
        assert not leftovers


class TestSnapshotRestore:
    def test_snapshot_preserves_content(self, tmp_path):
        src = tmp_path / "orig.txt"
        src.write_text("ORIGINAL")
        snap = _snapshot(str(src))
        assert os.path.exists(snap)
        with open(snap) as f:
            assert f.read() == "ORIGINAL"

    def test_restore_overwrites_target(self, tmp_path):
        src = tmp_path / "orig.txt"
        src.write_text("ORIGINAL")
        snap = _snapshot(str(src))
        src.write_text("CHANGED")
        _restore(str(src), snap)
        with open(src) as f:
            assert f.read() == "ORIGINAL"

    def test_revert_returns_true_when_snapshot_exists(self, tmp_path):
        src = tmp_path / "orig.txt"
        src.write_text("ORIGINAL")
        snap = _snapshot(str(src))
        src.write_text("CHANGED")
        assert revert(str(src), snap) is True
        with open(src) as f:
            assert f.read() == "ORIGINAL"

    def test_revert_returns_false_when_snapshot_missing(self, tmp_path):
        assert revert(str(tmp_path / "x"), "/nonexistent/snap") is False


class TestReplacePlanTask:
    def test_replaces_existing_function(self):
        original = (
            "\"\"\"module docstring\"\"\"\n"
            "__version__ = \"1.0\"\n"
            "\n"
            "\n"
            "def plan_task(task: str) -> List[str]:\n"
            "    return [task]\n"
            "\n"
            "def other_func():\n"
            "    pass\n"
        )
        new_func = "def plan_task(task: str) -> List[str]:\n    return [task, 'extra']\n"
        out = _replace_plan_task(original, new_func)
        assert out is not None
        # New function body should be in output
        assert "return [task, 'extra']" in out
        # Other functions preserved
        assert "def other_func" in out
        # Module docstring + version preserved
        assert "__version__ = \"1.0\"" in out

    def test_returns_none_when_not_present(self):
        original = "def other_func():\n    pass\n"
        out = _replace_plan_task(original, "def plan_task(): pass\n")
        assert out is None

    def test_returns_parse_error_string_when_source_broken(self):
        # Source has a syntax error
        bad = "def plan_task(:\n    pass\n"
        out = _replace_plan_task(bad, "def plan_task(): pass\n")
        assert out is not None and out.startswith("PARSE_ERROR:")


class TestAppendPlanTask:
    def test_appends_when_not_present(self):
        out = _append_plan_task("def other(): pass", "def plan_task(): pass")
        assert "def other(): pass" in out
        assert "def plan_task(): pass" in out
        assert out.index("def other") < out.index("def plan_task")


class TestValidateSyntax:
    def test_returns_none_for_valid_source(self, tmp_path):
        path = tmp_path / "good.py"
        path.write_text("def f(): return 1\n")
        assert _validate_syntax(str(path)) is None

    def test_returns_error_for_bad_source(self, tmp_path):
        path = tmp_path / "bad.py"
        path.write_text("def f(:\n")
        err = _validate_syntax(str(path))
        assert err is not None
        assert "SyntaxError" in err


# ─────────────────────────────────────────────────────────────
# Joint tests — apply_patch() end-to-end
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def planner_target(tmp_path):
    """An isolated copy of core/planner.py in a tmp dir."""
    src = tmp_path / "planner.py"
    src.write_text(
        "\"\"\"Task planner.\"\"\"\n"
        "__version__ = \"1.0\"\n"
        "from typing import List, Callable\n"
        "\n"
        "\n"
        "def plan_task(task: str, llm_call: Callable) -> List[str]:\n"
        "    \"\"\"Old implementation.\"\"\"\n"
        "    result = llm_call('do: ' + task)\n"
        "    return [result]\n"
    )
    return str(src)


class TestApplyPatch:
    """Joint test: apply_patch() exercises the full deployment path."""

    def test_replaces_plan_task_atomically(self, planner_target):
        """Happy path: existing plan_task gets replaced with patch fn."""
        new_fn = (
            "def plan_task(task: str, llm_call: Callable) -> List[str]:\n"
            "    \"\"\"New implementation.\"\"\"\n"
            "    return [step + '_a' for step in llm_call(task).split()]\n"
        )
        patch = Patch(function=new_fn, test="# unused", module=planner_target)
        result = apply_patch(patch, target_module=planner_target)

        assert result.status == "APPLIED", f"got {result.status}: {result.error}"
        # New implementation should be in the file
        with open(planner_target) as f:
            content = f.read()
        assert "New implementation" in content
        assert "Old implementation" not in content
        # __version__ preserved
        assert "__version__" in content
        # Snapshot left for manual revert
        assert result.snapshot_path
        assert os.path.exists(result.snapshot_path)

        # Cleanup
        cleanup_snapshot(result.snapshot_path)

    def test_revert_restores_original(self, planner_target):
        """If we revert, the file goes back to exactly what it was."""
        original_content = open(planner_target, encoding="utf-8").read()
        new_fn = "def plan_task(task: str) -> str:\n    return 'NEW'\n"
        patch = Patch(function=new_fn, test="# unused", module=planner_target)
        result = apply_patch(patch, target_module=planner_target)
        assert result.status == "APPLIED"
        snapshot = result.snapshot_path

        # Now manually revert
        revert_ok = revert(planner_target, snapshot)
        assert revert_ok is True

        with open(planner_target, encoding="utf-8") as f:
            assert f.read() == original_content

        cleanup_snapshot(snapshot)

    def test_syntax_error_in_patch_reverts(self, planner_target):
        """If the merged file has a syntax error, we revert."""
        # Patch with a function that has unclosed parentheses —
        # genuine syntax error caught by compile()
        bad_fn = "def plan_task(task: str) -> str:\n    return task + ("
        patch = Patch(function=bad_fn, test="# unused", module=planner_target)
        result = apply_patch(patch, target_module=planner_target,
                             run_harness_after=False)

        assert result.status == "REVERTED", f"got {result.status}: {result.error}"
        assert "syntax" in result.error.lower()

        # The file should be back to original
        with open(planner_target) as f:
            content = f.read()
        assert "Old implementation" in content

        cleanup_snapshot(result.snapshot_path)

    def test_no_plan_task_appends(self, tmp_path):
        """If target doesn't have plan_task, we append."""
        target = tmp_path / "no_plan_task.py"
        target.write_text("def other(): pass\n")

        fn = (
            "def plan_task(task: str) -> List[str]:\n"
            "    \"\"\"Newly added.\"\"\"\n"
            "    return [task]\n"
        )
        patch = Patch(function=fn, test="# unused", module=str(target))
        result = apply_patch(patch, target_module=str(target),
                             run_harness_after=False)

        assert result.status == "APPLIED"
        with open(target) as f:
            content = f.read()
        assert "def other" in content
        assert "def plan_task" in content
        assert "Newly added" in content

        cleanup_snapshot(result.snapshot_path)

    def test_missing_target_returns_failed(self, tmp_path):
        nonexistent = str(tmp_path / "does_not_exist.py")
        fn = "def plan_task(): return []\n"
        patch = Patch(function=fn, test="# unused", module=nonexistent)
        result = apply_patch(patch, target_module=nonexistent)
        assert result.status == "FAILED"
        assert "does not exist" in result.error.lower()

    def test_smoke_import_after_apply(self, planner_target):
        """Smoke-import test verifies the new module is importable."""
        fn = (
            "from typing import Callable, List\n"
            "\n"
            "def plan_task(task: str, llm_call: Callable) -> List[str]:\n"
            "    \"\"\"New fn from test.\"\"\"\n"
            "    return [step for step in llm_call(task).split('\\n') if step]\n"
        )
        patch = Patch(function=fn, test="# unused", module=planner_target)
        result = apply_patch(patch, target_module=planner_target)

        assert result.status == "APPLIED", f"{result.error}"
        # Should pass the smoke import because the file compiles and
        # has a callable plan_task
        with open(planner_target) as f:
            assert "New fn from test" in f.read()

        cleanup_snapshot(result.snapshot_path)


class TestApplyEdgeCases:
    """Edge cases: malformed patch, target with decorators, etc."""

    def test_handles_target_with_decorator(self, tmp_path):
        """Decorators above plan_task should be preserved/replaced as a unit."""
        target = tmp_path / "deco.py"
        target.write_text(
            "from functools import lru_cache\n"
            "\n"
            "\n"
            "@lru_cache(maxsize=128)\n"
            "def plan_task(task: str) -> str:\n"
            "    return task\n"
        )

        new_fn = (
            "@lru_cache(maxsize=256)\n"
            "def plan_task(task: str) -> str:\n"
            "    return task + '_v2'\n"
        )
        patch = Patch(function=new_fn, test="# x", module=str(target))
        result = apply_patch(patch, target_module=str(target),
                             run_harness_after=False)
        assert result.status == "APPLIED", result.error

        with open(target) as f:
            content = f.read()
        assert "maxsize=256" in content
        assert "task + '_v2'" in content
        # No leftover from old decorator
        assert "maxsize=128" not in content

        cleanup_snapshot(result.snapshot_path)



"""Replacement block for tests/test_v2_apply.py - TestApplyAndRunHarness class."""

class TestApplyAndRunHarness:
    """Joint test: apply_patch() + v2_agent._run_harness() cooperate.

    The self-improving loop closes when:
      1. v2_agent.improve() produces a Patch
      2. v2_apply.apply_patch() deploys it
      3. v2_agent._run_harness() validates the merged module runs

    This test exercises the full path with a hand-rolled patch (we
    don't drive the real LLM in tests - that requires network + cost).
    """

    def test_apply_then_harness(self, planner_target):
        from src.v2_agent import _run_harness
        # Patch: replaces plan_task. Uses chr(10) for newline to avoid
        # quote-escape gymnastics. Comment-only "docstring" on plan_task.
        new_fn_lines = [
            "from typing import Callable, List",
            "",
            "",
            "def plan_task(task, llm_call):",
            "    # Replaced by TestApplyAndRunHarness",
            "    return [line for line in llm_call(task).split(chr(10)) if line.strip()]",
        ]
        new_fn = "\n".join(new_fn_lines) + "\n"
        target_escaped = planner_target.replace("\\", "\\\\").replace('"', '\\"')
        test_code_lines = [
            "def test_applied_callable():",
            "    import importlib.util",
            f'    spec = importlib.util.spec_from_file_location("p", "{target_escaped}")',
            "    m = importlib.util.module_from_spec(spec)",
            "    spec.loader.exec_module(m)",
            "    fn = getattr(m, 'plan_task', None)",
            "    assert fn is not None",
            "    assert callable(fn)",
        ]
        test_code = "\n".join(test_code_lines) + "\n"

        patch = Patch(function=new_fn, test=test_code, module=planner_target)
        result = apply_patch(patch, target_module=planner_target)
        assert result.status == "APPLIED", f"apply: {result.status} {result.error}"
        assert _run_harness(patch) is True, "harness failed on merged file"
        revert(planner_target, result.snapshot_path)
        cleanup_snapshot(result.snapshot_path)

    def test_apply_round_trip(self, planner_target):
        """Apply, observe behavior change, revert, observe restored."""
        original_content = open(planner_target, encoding="utf-8").read()
        new_fn = (
            "def plan_task(task: str, llm_call=lambda x: x) -> list:\n"
            "    return ['MARKER_FROM_APPLY']\n"
        )
        patch = Patch(function=new_fn, test="# unused", module=planner_target)
        result = apply_patch(patch, target_module=planner_target,
                             run_harness_after=False)
        assert result.status == "APPLIED"
        with open(planner_target) as f:
            assert "MARKER_FROM_APPLY" in f.read()
        assert revert(planner_target, result.snapshot_path) is True
        cleanup_snapshot(result.snapshot_path)
        with open(planner_target, encoding="utf-8") as f:
            assert f.read() == original_content



class TestApplyPatchDefensive:
    """Defensive input validation — apply_patch must never raise
    on caller mistakes (None patch, missing fields, empty fields).
    This is what v2_agent returns None patch calls into."""
    
    def test_patch_none_returns_failed(self):
        from src.v2_apply import apply_patch
        result = apply_patch(None, target_module="anywhere")
        assert result.status == "FAILED"
        assert "None" in result.error
    
    def test_empty_function_returns_failed(self):
        from src.v2_apply import apply_patch
        from src.v2_agent import Patch
        p = Patch(function="", test="# x", module="anywhere")
        result = apply_patch(p, target_module="anywhere")
        assert result.status == "FAILED"
        assert "empty" in result.error.lower()
    
    def test_whitespace_function_returns_failed(self):
        from src.v2_apply import apply_patch
        from src.v2_agent import Patch
        p = Patch(function="   \n   ", test="# x", module="anywhere")
        result = apply_patch(p, target_module="anywhere")
        assert result.status == "FAILED"
