"""Tests for OS cron installer (per v4.0.0 sub-task 2/3).

Per 你 vision 2026-07-08 '我希望这个项目之后可以自己独立运行':
- Generate cross-platform cron configs

Per 自上而下/分治:
- Big: SA v4.0.0 cron execution
- Sub-task 1 done (b350609): cron logic + CLI
- Sub-task 2 (this): OS cron integration

Per P18: regression tests required.
Per P9 (hard rule): dry_run=True by default (safe).
"""
from pathlib import Path
from unittest.mock import patch

import pytest

from src.os_cron_installer import (
    detect_os,
    generate_windows_task_xml,
    generate_macos_plist,
    generate_crontab_line,
    install_cron,
)


class TestDetectOS:
    """Test OS detection (per LITERATURE cross-platform)."""

    def test_detect_os_returns_string(self):
        """detect_os: returns 'windows' | 'macos' | 'linux' | 'unknown'."""
        result = detect_os()
        assert result in ("windows", "macos", "linux", "unknown")


class TestGenerateWindowsTaskXml:
    """Test Windows Task Scheduler XML generation."""

    def test_generate_windows_default(self):
        """generate_windows_task_xml: contains task definition."""
        xml = generate_windows_task_xml(
            "test-task", "/usr/bin/python", "/path/to/script.py",
            cron_expr="0 2")
        assert "<?xml" in xml
        assert "Task" in xml
        assert "test-task" in xml
        assert "CalendarTrigger" in xml
        assert "/usr/bin/python" in xml
        assert "self_upgrade" in xml

    def test_generate_windows_custom_time(self):
        """generate_windows_task_xml: custom cron time."""
        xml = generate_windows_task_xml(
            "test", "python", "/script.py", cron_expr="14 30")
        assert "T14:30:00" in xml


class TestGenerateMacosPlist:
    """Test macOS launchd plist generation."""

    def test_generate_macos_default(self):
        """generate_macos_plist: contains plist definition."""
        plist = generate_macos_plist(
            "test-task", "/usr/bin/python", "/path/to/script.py",
            cron_expr="0 2")
        assert "<?xml" in plist
        assert "plist" in plist
        assert "test-task" in plist
        assert "ProgramArguments" in plist
        assert "/usr/bin/python" in plist

    def test_generate_macos_custom_time(self):
        """generate_macos_plist: custom hour/minute."""
        plist = generate_macos_plist(
            "test", "python", "/script.py", cron_expr="14 30")
        assert "<integer>14</integer>" in plist
        assert "<integer>30</integer>" in plist


class TestGenerateCrontabLine:
    """Test Linux crontab line generation."""

    def test_generate_crontab_default(self):
        """generate_crontab_line: standard cron syntax."""
        line = generate_crontab_line(
            "/usr/bin/python", "/path/to/script.py", cron_expr="0 2")
        # Format: M H * * * command
        assert line.startswith("2 0 * * *")
        assert "/usr/bin/python" in line
        assert "self_upgrade" in line
        assert "daily-loop" in line

    def test_generate_crontab_custom_time(self):
        """generate_crontab_line: custom cron time."""
        line = generate_crontab_line(
            "python", "/script.py", cron_expr="14 30")
        assert line.startswith("30 14 * * *")


class TestInstallCron:
    """Test full install_cron flow."""

    def test_install_cron_dry_run(self, tmp_path):
        """install_cron dry_run=True: returns config without writing."""
        result = install_cron(task_name="test-task", cron_expr="0 2",
                               dry_run=True, output_dir=tmp_path)
        assert "os" in result
        assert "config_path" in result
        assert "config_content" in result
        assert "install_command" in result
        assert result["dry_run"] is True
        # No file written in dry_run
        assert not Path(result["config_path"]).exists()

    def test_install_cron_writes_file(self, tmp_path):
        """install_cron dry_run=False: writes config file."""
        result = install_cron(task_name="test-task", cron_expr="0 2",
                               dry_run=False, output_dir=tmp_path)
        assert result["dry_run"] is False
        # File written
        assert Path(result["config_path"]).exists()
        # Content matches
        content = Path(result["config_path"]).read_text(encoding="utf-8")
        assert content == result["config_content"]

    def test_install_cron_unsupported_os(self):
        """install_cron: unsupported OS returns error."""
        with patch("src.os_cron_installer.detect_os", return_value="unknown"):
            result = install_cron(task_name="test", dry_run=True)
        assert result["os"] == "unknown"
        assert "error" in result