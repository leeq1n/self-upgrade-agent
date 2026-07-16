"""Regression test for cron CLI subcommand (per P18 + 你 '排除bug' push).

Per LITERATURE Signal-to-Fix: real bug found when user ran
'python -m self_upgrade cron --install' and got 'No such command cron'.
Root cause: cron subcommand was not wired into CLI despite module existing.

Per 自上而下/分治:
- Big: SA v4.0.0 cron execution
- Sub-task 2 (c7998fa): OS cron integration (module exists)
- Sub-task 2b (this commit): CLI wiring (the bug fix)

Per P18 (failure -> regression test):
- Real bug: user reported 'No such command cron'
- Fix: wired cron subcommand into self_upgrade/__main__.py
- This test serves as regression coverage
"""
from click.testing import CliRunner

from self_upgrade.__main__ import cli


class TestCronCLI:
    """Per P18 regression test: cron subcommand exists."""

    def test_cron_command_in_help(self):
        """cron command appears in CLI."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "cron" in result.output

    def test_cron_help(self):
        """cron --help shows expected options."""
        runner = CliRunner()
        result = runner.invoke(cli, ["cron", "--help"])
        assert result.exit_code == 0
        assert "--show" in result.output
        assert "--install" in result.output
        assert "--apply" in result.output
        assert "--cron-expr" in result.output

    def test_cron_show(self):
        """cron --show generates config (dry-run, safe per P9)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["cron", "--show"])
        assert result.exit_code == 0
        # Should contain OS info + dry run message
        assert "OS:" in result.output
        assert "Dry run" in result.output

    def test_cron_install_dry_run(self):
        """cron --install defaults to dry-run (safe per P9)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["cron", "--install"])
        assert result.exit_code == 0
        # Default dry_run=True
        assert "Dry run: True" in result.output

    def test_cron_no_action_shows_message(self):
        """cron without flags shows usage hint."""
        runner = CliRunner()
        result = runner.invoke(cli, ["cron"])
        assert result.exit_code == 0
        assert "Use --show" in result.output
