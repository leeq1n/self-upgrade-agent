"""Tests for surgical patch application in pipeline benchmark evaluation.

Validates that _apply_patch_to_module correctly merges function patches
into existing modules without destroying imports/version metadata.
"""
import os
import tempfile
import pytest
from src.pipeline_lg import _apply_patch_to_module


class TestApplyPatchToModule:
    """Test surgical merge of patch code into existing module files."""

    def make_temp_module(self, suffix=".py"):
        """Create a temporary module file with known content."""
        content = (
            '"""Module docstring."""\n'
            '__version__ = "1.0.0"\n'
            'from typing import List, Callable\n'
            '\n'
            '\n'
            'def plan_task(task: str, llm_call: Callable) -> List[str]:\n'
            '    """Original implementation."""\n'
            '    prompt = f"Original: {task}"\n'
            '    result = llm_call(prompt)\n'
            '    return [result]\n'
        )
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, delete=False, encoding="utf-8"
        )
        tmp.write(content)
        tmp.close()
        return tmp.name

    def test_surgical_merge_preserves_imports_and_version(self):
        """When patch is a function only, merged result keeps imports + __version__."""
        module_path = self.make_temp_module()
        try:
            patch_code = (
                'def plan_task(task: str, llm_call: Callable) -> List[str]:\n'
                '    """Improved implementation with step decomposition."""\n'
                '    prompt = f"Break this into steps: {task}"\n'
                '    result = llm_call(prompt)\n'
                '    steps = [line.strip() for line in result.split("\\n") if line.strip()]\n'
                '    return steps\n'
            )

            merged = _apply_patch_to_module(module_path, patch_code)

            # Assert imports are preserved
            assert 'from typing import List, Callable' in merged
            # Assert version is preserved
            assert '__version__ = "1.0.0"' in merged
            # Assert module docstring preserved
            assert '"""Module docstring."""' in merged
            # Assert new implementation replaces old
            assert '"""Improved implementation with step decomposition."""' in merged
            assert '"Original implementation"' not in merged
            # Assert the patch function is present
            assert 'def plan_task' in merged
            assert 'Break this into steps' in merged
        finally:
            os.unlink(module_path)

    def test_full_module_patch_used_as_is(self):
        """When patch is a full module (has docstring), use it directly."""
        module_path = self.make_temp_module()
        try:
            full_module = (
                '"""Brand new module."""\n'
                '__version__ = "2.0.0"\n'
                'from typing import List, Callable, Dict\n'
                '\n'
                'def plan_task(task: str, llm_call: Callable) -> List[str]:\n'
                '    """New impl."""\n'
                '    return ["step1", "step2"]\n'
            )

            merged = _apply_patch_to_module(module_path, full_module)

            assert merged == full_module
        finally:
            os.unlink(module_path)

    def test_unknown_function_name_appended_to_end(self):
        """When patch targets a function not in module, append to end of file."""
        module_path = self.make_temp_module()
        try:
            original = open(module_path, encoding="utf-8").read()

            patch_code = (
                'def unknown_func(x: int) -> int:\n'
                '    return x * 2\n'
            )

            merged = _apply_patch_to_module(module_path, patch_code)

            # Original content preserved
            assert 'def plan_task' in merged
            assert '"""Original implementation."""' in merged
            # New function appended at the end
            assert 'def unknown_func' in merged
            assert 'return x * 2' in merged
            assert merged.index('def plan_task') < merged.index('def unknown_func')
        finally:
            os.unlink(module_path)

    def test_existing_module_unchanged_when_patch_has_no_def(self):
        """When patch_code has no function keyword, return original unchanged."""
        module_path = self.make_temp_module()
        try:
            original = open(module_path, encoding="utf-8").read()

            patch_code = "print('hello world')  # not a function"

            merged = _apply_patch_to_module(module_path, patch_code)

            assert merged == original
        finally:
            os.unlink(module_path)
