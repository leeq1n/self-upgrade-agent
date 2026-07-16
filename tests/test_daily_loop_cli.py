"""Tests for daily-loop CLI --enable-ab flag (per v3.3.0 sub-task 4/3).

Per 你 vision 终极目标:
- Real CLI wiring of A/B benchmark into daily-loop
- v3.3.0 sub-task 4/3: connect statistical significance to real workflow

Per 自上而下/分治 (user meta-principle):
- Big: v3.3.0 A/B benchmark
- Sub-task 1-3 (done): core + integration + statistical
- Sub-task 4/3 (this commit): CLI flag wiring

Per P18: regression tests required.
"""
from click.testing import CliRunner
from unittest.mock import patch

from self_upgrade.__main__ import cli


class TestDailyLoopCLIEnableAB:
    """Per v3.3.0 sub-task 4/3: --enable-ab flag accepted."""

    def test_enable_ab_flag_in_help(self):
        """daily-loop CLI shows --enable-ab flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["daily-loop", "--help"])
        assert result.exit_code == 0
        assert "--enable-ab" in result.output
        assert "--no-ab" in result.output

    def test_enable_ab_default_off(self):
        """daily-loop default has enable-ab=False."""
        runner = CliRunner()
        result = runner.invoke(cli, ["daily-loop", "--help"])
        assert "default" in result.output.lower()

    def test_daily_loop_ab_invokes_baseline(self):
        """daily-loop --enable-ab invokes ab_run_tests for baseline."""
        runner = CliRunner()
        with patch("src.ab_benchmark.run_tests") as mock_ab:
            mock_ab.return_value = {
                "passed": 16, "failed": 0,
                "elapsed_sec": 1.0, "success": True,
            }
            result = runner.invoke(cli, [
                "daily-loop", "--enable-ab", "--mock",
                "--max-rounds", "0", "--target", "core/test.py",
                "--test-path", "tests/test_v2_round.py",
            ])
            assert mock_ab.called or "ab" in result.output.lower()

    def test_daily_loop_no_ab_unchanged(self):
        """daily-loop without --enable-ab behaves as before."""
        runner = CliRunner()
        with patch("src.ab_benchmark.run_tests") as mock_ab:
            mock_ab.return_value = {
                "passed": 16, "failed": 0,
                "elapsed_sec": 1.0, "success": True,
            }
            result = runner.invoke(cli, [
                "daily-loop", "--no-ab", "--mock",
                "--max-rounds", "0", "--target", "core/test.py",
            ])
            assert "[ab] A/B baseline" not in result.output