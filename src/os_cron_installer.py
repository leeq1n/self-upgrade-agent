"""OS-specific cron installer (per v4.0.0 sub-task 2/3).

Per 你 vision 2026-07-08 '我希望这个项目之后可以自己独立运行':
- Generate OS-specific cron config (XML for Windows / plist for macOS / crontab for Linux)
- Install via schtasks/launchctl/crontab
- Per LITERATURE Signal-to-Fix: real OS integration

Per 自上而下/分治 (user meta-principle):
- Big: SA v4.0.0 cron execution
- Sub-task 1 (b350609): cron logic + CLI
- Sub-task 2 (this commit): OS cron integration (cross-platform config gen + install)
- Sub-task 3 (future): failure escalation

Per P23 doc-first: spec exists (PROJECT_STATE + LITERATURE).
Per P18: regression tests required.
"""
import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict


def detect_os():
    """Detect OS family (Windows / macOS / Linux).

    Per LITERATURE: minimal, 奥卡姆.
    Returns: 'windows' | 'macos' | 'linux' | 'unknown'.
    """
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    return "unknown"


def generate_windows_task_xml(task_name, python_path, script_path,
                              cron_expr="0 2"):
    """Generate Windows Task Scheduler XML.

    Per LITERATURE: standard XML format for Task Scheduler.
    Returns XML string.
    """
    # Parse 'H M' cron (default '0 2' = 02:00 daily)
    parts = cron_expr.strip().split()
    hour = parts[0] if len(parts) >= 1 else "0"
    minute = parts[1] if len(parts) >= 2 else "2"
    xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>SA v4.0.0 cron: {task_name}</Description>
    <Author>self-upgrade-agent</Author>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-07-11T{hour.zfill(2)}:{minute.zfill(2)}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
  </Settings>
  <Actions>
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>-m self_upgrade daily-loop --max-rounds 1 --target core/planner.py</Arguments>
      <WorkingDirectory>{os.path.dirname(script_path)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
    return xml


def generate_macos_plist(task_name, python_path, script_path,
                          cron_expr="0 2"):
    """Generate macOS launchd plist.

    Per LITERATURE: standard plist format.
    Returns plist XML string.
    """
    parts = cron_expr.strip().split()
    hour = parts[0] if len(parts) >= 1 else "0"
    minute = parts[1] if len(parts) >= 2 else "2"
    plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.self-upgrade-agent.{task_name}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{python_path}</string>
    <string>-m</string>
    <string>self_upgrade</string>
    <string>daily-loop</string>
    <string>--max-rounds</string>
    <string>1</string>
    <string>--target</string>
    <string>core/planner.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>{os.path.dirname(script_path)}</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>{hour}</integer>
    <key>Minute</key>
    <integer>{minute}</integer>
  </dict>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>'''
    return plist


def generate_crontab_line(python_path, script_path, cron_expr="0 2"):
    """Generate Linux crontab line.

    Per LITERATURE: standard cron syntax.
    Returns single line (no comments).
    """
    parts = cron_expr.strip().split()
    hour = parts[0] if len(parts) >= 1 else "0"
    minute = parts[1] if len(parts) >= 2 else "2"
    return (f"{minute} {hour} * * * "
            f"cd {os.path.dirname(script_path)} && "
            f"{python_path} -m self_upgrade daily-loop "
            f"--max-rounds 1 --target core/planner.py "
            f">> {os.path.dirname(script_path)}/cron.log 2>&1")


def install_cron(task_name="self-upgrade-daily", cron_expr="0 2",
                 dry_run=True, output_dir=None):
    """Install OS-specific cron config.

    Per LITERATURE Signal-to-Fix: real OS integration.
    Per P9 (hard rule): dry_run=True by default (safe).

    Returns: dict {os, config_path, config_content, install_command}.
    """
    os_type = detect_os()
    python_path = sys.executable
    script_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    if output_dir is None:
        output_dir = script_path
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if os_type == "windows":
        config_content = generate_windows_task_xml(
            task_name, python_path, script_path, cron_expr)
        config_path = output_dir / f"{task_name}.xml"
        install_cmd = (
            f'schtasks /create /tn "{task_name}" '
            f'/xml "{config_path}"'
        )
    elif os_type == "macos":
        config_content = generate_macos_plist(
            task_name, python_path, script_path, cron_expr)
        config_path = output_dir / f"com.self-upgrade-agent.{task_name}.plist"
        install_cmd = (
            f'launchctl load -w "{config_path}"'
        )
    elif os_type == "linux":
        config_content = generate_crontab_line(
            python_path, script_path, cron_expr)
        config_path = output_dir / f"{task_name}.cron"
        install_cmd = (
            f'(crontab -l 2>/dev/null; cat "{config_path}") | crontab -'
        )
    else:
        return {"os": os_type, "error": "unsupported OS"}
    if not dry_run:
        config_path.write_text(config_content, encoding="utf-8")
    # Per P18 + 你 '排除bug' push: when dry_run=False, actually execute
    # the install command (register with OS scheduler).
    install_result = None
    if not dry_run:
        import subprocess
        try:
            install_result = subprocess.run(
                install_cmd, shell=True, capture_output=True,
                text=True, timeout=30,
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            install_result = {"error": str(e)}
    return {
        "os": os_type,
        "config_path": str(config_path),
        "config_content": config_content,
        "install_command": install_cmd,
        "install_result": (vars(install_result) if hasattr(install_result, "returncode")
                          else install_result),
        "dry_run": dry_run,
    }


def main():
    """CLI: generate + show cron config (dry-run by default)."""
    print("=== SA v4.0.0 OS Cron Installer ===")
    print(f"Per 你 vision 2026-07-08 '希望这个项目之后可以自己独立运行'")
    print()
    result = install_cron(task_name="self-upgrade-daily", cron_expr="0 2",
                          dry_run=True)
    print(f"OS: {result['os']}")
    print(f"Config path: {result['config_path']}")
    print(f"Install command (run manually):")
    print(f"  {result['install_command']}")
    print()
    print(f"Config preview (first 20 lines):")
    lines = result["config_content"].split("\n")
    for line in lines[:20]:
        print(f"  {line}")
    print()
    print("Per LITERATURE Signal-to-Fix: dry_run=True by default.")
    print("Re-run with dry_run=False to write config file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())