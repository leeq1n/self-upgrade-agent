"""Auto-commit helper for daily-loop / improve (per user 2026-07-10).

Per user '区分开自动更新和手动更新':
- Auto commits use a distinct author (`Auto Upgrade <auto@self-upgrade.local>`)
- Commit message prefix: `[auto]`
- Patch bundle also written to `upgrades/auto-patches/<date>-<short-hash>.patch`
  for human review / selective apply / rejection.

This module is OPT-IN via `--auto-commit` flag on improve / daily-loop.
Default behavior unchanged: KEPT patches stay in working tree (or auto-revert
per existing v2_round logic).
"""
import os
import subprocess
import time
from pathlib import Path


AUTO_AUTHOR = "Auto Upgrade"
AUTO_EMAIL = "auto@self-upgrade.local"
BUNDLE_DIR = "upgrades/auto-patches"


def _run_git(args, cwd=None, timeout=15):
    """Run git command, return (rc, stdout, stderr)."""
    r = subprocess.run(
        ["git"] + args,
        capture_output=True, text=True,
        cwd=cwd or os.getcwd(),
        timeout=timeout,
    )
    return r.returncode, r.stdout, r.stderr


def _short_hash(diff):
    """Stable short hash from diff content (for bundle filename)."""
    import hashlib
    return hashlib.sha1(diff.encode("utf-8", errors="replace")).hexdigest()[:8]


def write_patch_bundle(target_module: str) -> str:
    """Write the staged diff to upgrades/auto-patches/<date>-<hash>.patch.

    Returns absolute path to bundle, or "" if no diff.
    """
    rc, out, _ = _run_git(["diff", "--", target_module])
    if rc != 0 or not out.strip():
        # No diff (already reverted?)
        return ""
    Path(BUNDLE_DIR).mkdir(parents=True, exist_ok=True)
    date = time.strftime("%Y-%m-%d")
    bundle_path = os.path.abspath(
        os.path.join(BUNDLE_DIR, f"{date}-{_short_hash(out)}.patch")
    )
    with open(bundle_path, "w", encoding="utf-8") as f:
        f.write(out)
    return bundle_path


def auto_commit(target_module: str, paper_id: str = "", tests_passed: int = 0,
                bundle_path: str = "") -> str:
    """Commit KEPT patch with auto author + [auto] prefix.

    Returns commit hash, or "" on failure.
    """
    # Stage the target file
    _run_git(["add", "--", target_module])

    # Build commit message
    msg_lines = [f"[auto] KEPT patch to {target_module}"]
    if paper_id:
        msg_lines.append(f"Paper: {paper_id}")
    if tests_passed:
        msg_lines.append(f"Tests: {tests_passed} passed")
    if bundle_path:
        msg_lines.append(f"Bundle: {bundle_path}")
    msg_lines.append("")
    msg_lines.append("Auto-committed by self-upgrade daily-loop/improve.")
    msg_lines.append("Per user 2026-07-10 '区分开自动更新和手动更新'.")
    msg_lines.append("Author: Auto Upgrade <auto@self-upgrade.local>")
    msg = "\n".join(msg_lines)

    # Commit with auto author (per git config override)
    env_args = [
        "-c", f"user.name={AUTO_AUTHOR}",
        "-c", f"user.email={AUTO_EMAIL}",
    ]
    r = subprocess.run(
        ["git"] + env_args + ["commit", "-m", msg],
        capture_output=True, text=True,
        cwd=os.getcwd(), timeout=15,
    )
    if r.returncode != 0:
        return ""

    # Get commit hash
    rc, out, _ = _run_git(["rev-parse", "HEAD"])
    return out.strip() if rc == 0 else ""
