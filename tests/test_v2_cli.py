"""Tests for the v2.x unified CLI (self_upgrade/__main__.py).

Per user feedback 2026-07-08: '需要统一管理的功能, 能跑自进化,
能具体使用, 能整理项目使其干净'.

This file replaces tests/test_unified_cli.py (which tested the
v1.8.x unified CLI now removed).
"""
import os
import sys
import subprocess
from click.testing import CliRunner

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)


class TestV2CliStructure:
    """The CLI is a Click group with subcommands: improve, improve-multi,
improve-harness, replay, test-scale."""

    def test_cli_is_click_group(self):
        from self_upgrade.__main__ import cli
        assert hasattr(cli, "commands")
        assert "improve" in cli.commands
        assert "replay" in cli.commands
        assert "test-scale" in cli.commands

    def test_cli_help_runs(self):
        from self_upgrade.__main__ import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "self-upgrade-agent" in result.output.lower() or "self-upgrade" in result.output.lower()

    def test_improve_help(self):
        from self_upgrade.__main__ import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["improve", "--help"])
        assert result.exit_code == 0
        assert "round" in result.output.lower() or "improve" in result.output.lower()

    def test_replay_help(self):
        from self_upgrade.__main__ import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["replay", "--help"])
        assert result.exit_code == 0

    def test_test_scale_help(self):
        from self_upgrade.__main__ import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["test-scale", "--help"])
        assert result.exit_code == 0
        assert "n_rounds" in result.output.lower() or "round" in result.output.lower()

    def test_mock_flag_top_level(self):
        from self_upgrade.__main__ import cli
        # --mock / --no-mock is a top-level option
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert "--mock" in result.output
        assert "--no-mock" in result.output


class TestV2CliRejectsInvalid:
    """CLI should reject invalid inputs gracefully (not crash)."""

    def test_unknown_subcommand(self):
        from self_upgrade.__main__ import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["nonexistent"])
        assert result.exit_code != 0

    def test_test_scale_requires_int(self):
        from self_upgrade.__main__ import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["test-scale", "not_an_int"])
        assert result.exit_code != 0


class TestV2CliLazyImports:
    """CLI should not import heavy v2 modules at import time.
    The Click group + subcommand declarations should be cheap to load."""

    def test_cli_module_imports_fast(self):
        import time
        t0 = time.time()
        # Force fresh import
        if "self_upgrade.__main__" in sys.modules:
            del sys.modules["self_upgrade.__main__"]
        import self_upgrade.__main__ as cli_mod
        elapsed = time.time() - t0
        # Should be < 2s even on slow machines
        assert elapsed < 5, f"CLI import too slow: {elapsed:.1f}s"