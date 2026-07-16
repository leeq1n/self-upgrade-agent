"""Regression test for cron install apply (per P18 + 你 '排除bug' push).

Per user 2026-07-11:
- Ran 'python -m self_upgrade cron --install --apply'
- Got 'Installed: ...xml' but no actual install_command execution
- Bug: dry_run=False only writes file, never runs install command

Per P18 (failure -> regression test):
- Real bug: install command not executed
- Fix: install_cron now subprocess.run(install_cmd) when dry_run=False
- Per LITERATURE Signal-to-Fix: real install behavior verified

Per 自上而下/分治:
- Big: SA v4.0.0 cron execution
- Sub-task 2b: CLI wiring (done in 82790d2)
- Sub-task 2c: actual install execution (this commit)
"""
from unittest.mock import patch, MagicMock

from src.os_cron_installer import install_cron


class TestCronInstallApply:
    """Per P18: dry_run=False actually executes install_command."""

    def test_dry_run_does_not_execute(self, tmp_path):
        """install_cron(dry_run=True): NO install_result in dict."""
        # Don't mock subprocess.run globally — only check return value
        result = install_cron(cron_expr="0 2", dry_run=True,
                               output_dir=str(tmp_path))
        # dry_run=True should NOT have install_result
        assert result["dry_run"] is True
        assert result["install_result"] is None

    def test_apply_executes_install_command(self, tmp_path):
        """install_cron(dry_run=False): subprocess.run called for install command."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "SUCCESS"
        mock_result.stderr = ""
        with patch("src.os_cron_installer.subprocess.run",
                   return_value=mock_result) as mock_run:
            result = install_cron(cron_expr="0 2", dry_run=False,
                                   output_dir=str(tmp_path))
        # dry_run=False should trigger subprocess.run for install command
        assert result["dry_run"] is False
        assert result["install_result"] is not None
        # Verify subprocess.run was called with the install command
        assert mock_run.called
        call_args = mock_run.call_args
        assert "schtasks" in call_args[0][0] or "launchctl" in call_args[0][0] \
               or "crontab" in call_args[0][0]

    def test_apply_handles_install_failure(self, tmp_path):
        """install_cron(dry_run=False): install failure surfaced in result."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Access denied"
        with patch("src.os_cron_installer.subprocess.run",
                   return_value=mock_result):
            result = install_cron(cron_expr="0 2", dry_run=False,
                                   output_dir=str(tmp_path))
        assert result["install_result"]["returncode"] == 1
        assert "Access denied" in result["install_result"]["stderr"]
