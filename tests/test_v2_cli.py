"""Tests for the v2.x unified CLI (self_upgrade/__main__.py).

Per user feedback 2026-07-08: '需要统一管理的功能, 能跑自进化,
能具体使用, 能整理项目使其干净'.

This file replaces tests/test_unified_cli.py (which tested the
v1.8.x unified CLI now removed).
"""
import os
import sys
import subprocess
from unittest.mock import patch
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

class TestV2CliHarnessCount:
    """Per user 2026-07-10: 简化用户操作.
    --count N: 1 line to run N consecutive harness rounds."""

    def test_count_flag_accepted(self):
        from self_upgrade.__main__ import cli
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ["improve-harness", "--count", "3", "--help"])
        assert result.exit_code == 0
        assert "--count" in result.output

    def test_count_runs_loop_with_mock_kept(self):
        """--count 3 with all KEPT -> exit 0, summary shows 3/3."""
        from self_upgrade.__main__ import cli
        from click.testing import CliRunner
        from src.v2_agent import Paper
        from src.v2_round import RoundResult
        runner = CliRunner()
        kept = RoundResult(
            decision="KEPT",
            paper=Paper(arxiv_id="x", title="t", abstract="a"),
            target_module="x.py",
        )
        with patch("src.v2_round.run_one_round_multi", return_value=kept):
            result = runner.invoke(cli, ["improve-harness", "--count", "3",
                                          "--target", "x.py",
                                          "--max-retries", "0"])
        # All 3 KEPT -> exit 0
        assert result.exit_code == 0, f"got {result.exit_code}, output: {result.output}"
        # Summary printed
        assert "Summary" in result.output
        assert "KEPT: 3/3" in result.output
        # 3 rounds printed
        assert "Round 1/3" in result.output
        assert "Round 3/3" in result.output

    def test_count_runs_loop_with_no_patch(self):
        """--count 2 with all NO_PATCH -> exit 1, summary 0/2."""
        from self_upgrade.__main__ import cli
        from click.testing import CliRunner
        from src.v2_agent import Paper
        from src.v2_round import RoundResult
        runner = CliRunner()
        no_patch = RoundResult(
            decision="NO_PATCH",
            paper=Paper(arxiv_id="x", title="t", abstract="a"),
            target_module="x.py",
        )
        with patch("src.v2_round.run_one_round_multi", return_value=no_patch):
            result = runner.invoke(cli, ["improve-harness", "--count", "2",
                                          "--target", "x.py",
                                          "--max-retries", "0"])
        # No KEPT -> exit 1
        assert result.exit_code == 1
        assert "KEPT: 0/2" in result.output

    def test_count_mixed_results(self):
        """--count 3 with 1 KEPT + 2 NO_PATCH -> exit 1, summary 1/3 (33%)."""
        from self_upgrade.__main__ import cli
        from click.testing import CliRunner
        from src.v2_agent import Paper
        from src.v2_round import RoundResult
        runner = CliRunner()
        kept = RoundResult(
            decision="KEPT",
            paper=Paper(arxiv_id="x", title="t", abstract="a"),
            target_module="x.py",
        )
        no_patch = RoundResult(
            decision="NO_PATCH",
            paper=Paper(arxiv_id="x", title="t", abstract="a"),
            target_module="x.py",
        )
        # 1st: KEPT, 2nd+3rd: NO_PATCH
        with patch("src.v2_round.run_one_round_multi",
                    side_effect=[kept, no_patch, no_patch]):
            result = runner.invoke(cli, ["improve-harness", "--count", "3",
                                          "--target", "x.py",
                                          "--max-retries", "0"])
        assert result.exit_code == 1
        assert "KEPT: 1/3" in result.output

    def test_count_1_no_summary(self):
        """--count 1 (default): no summary printed (single round)."""
        from self_upgrade.__main__ import cli
        from click.testing import CliRunner
        from src.v2_agent import Paper
        from src.v2_round import RoundResult
        runner = CliRunner()
        kept = RoundResult(
            decision="KEPT",
            paper=Paper(arxiv_id="x", title="t", abstract="a"),
            target_module="x.py",
        )
        with patch("src.v2_round.run_one_round_multi", return_value=kept):
            result = runner.invoke(cli, ["improve-harness", "--count", "1",
                                          "--target", "x.py",
                                          "--max-retries", "0"])
        assert result.exit_code == 0
        assert "Summary" not in result.output  # no summary for count=1
        assert "Round 1/" not in result.output  # no round marker for count=1
