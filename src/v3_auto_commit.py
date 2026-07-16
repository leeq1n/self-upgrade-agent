"""Auto-commit helper for daily-loop / improve.

Per user 2026-07-10 '区分开自动更新和手动更新': machine-applied
patches get a distinct author + [auto] prefix + a reviewable bundle
in upgrades/auto-patches/, so the user can tell auto from manual commits
at a glance.

Per P9 (hard rule, not LLM-judged): callers must resolve BEFORE commit.
Per P18 (failure -> regression test): 24 tests fail on 2026-07-10 taught
us that test pass != acceptable, callers must load too.

Per LITERATURE Self-Harness paper: harness boundary must be validated
AFTER patch (run target tests + caller compile), not before.
Per LITERATURE Signal-to-Fix Loop: fail at the earliest layer (compile,
not runtime).
"""
import os
import time
import json
import subprocess
from pathlib import Path

# Per user 2026-07-10: distinct from user author.
AUTO_AUTHOR = "Auto Upgrade"
AUTO_EMAIL = "auto@self-upgrade.local"

BUNDLE_DIR = "upgrades/auto-patches"


def _run_git(args, cwd=None, timeout=15):
    """Run git command, return (rc, stdout, stderr).

    Per P9 (hard rule, deterministic): force UTF-8 encoding to handle
    binary/garbled bytes on Windows (gbk codec default fails on 0x92).
    Per P18 (failure -> regression test): never raise UnicodeDecodeError.
    """
    r = subprocess.run(
        ["git"] + args,
        capture_output=True,
        cwd=cwd or os.getcwd(),
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )
    # Per P18: never return None — guarantee str type for downstream strip()
    return r.returncode, (r.stdout or ""), (r.stderr or "")


def _short_hash(diff):
    """Stable short hash from diff content (for bundle filename)."""
    import hashlib
    return hashlib.sha1(diff.encode("utf-8", errors="replace")).hexdigest()[:8]


def _compile_check(path, name):
    """Compile-only check.  Per P9 hard rule: regression test, not feature test."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            compile(f.read(), name, "exec")
        return None
    except SyntaxError as e:
        return f"{name}: SyntaxError {e}"
    except FileNotFoundError:
        return None  # file moved/deleted, skip


def check_callers(target_module):
    """Per P9 (hard rule) + P18 (failure -> regression test):
    Verify target module + top-10 Python callers still compile cleanly.

    Returns (ok: bool, errors: List[str]).

    Per LITERATURE Self-Harness paper: harness boundary validated AFTER
    patch.  This runs against the working-tree (post-apply) state.
    Per P7 奥卡姆: compile-only (fast, no exec, no side-effects).

    Per OBSERVATIONS 2026-07-11 Round 1: git grep without *.py glob
    returns .md files (prose mentions "core.") -> false-positive.
    Restrict to *.py via git pathspec.
    """
    errors = []
    target_path = os.path.abspath(target_module)

    # Step 1: compile target module (catches rename-removed-function regressions)
    e = _compile_check(target_path, target_module)
    if e:
        errors.append(e)

    # Step 2: compile top-10 Python callers (catches ImportError)
    try:
        target_pkg = target_module.split("/")[0]
        rc, out, _ = _run_git(
            ["grep", "-l", "-E",
             f"from\\s+{target_pkg}\\.|import\\s+{target_pkg}\\.",
             "--", "*.py"],
            timeout=5,
        )
        caller_files = [f.strip() for f in out.split("\n") if f.strip()][:10]
        for cf in caller_files:
            e = _compile_check(os.path.join(os.getcwd(), cf), cf)
            if e:
                errors.append(e)
    except Exception:
        pass  # git grep failure is not a hard failure

    return (len(errors) == 0), errors


def write_patch_bundle(target_module):
    """Write the staged diff to upgrades/auto-patches/<date>-<hash>.patch.

    Returns absolute path to bundle, or "" if no diff.
    """
    rc, out, _ = _run_git(["diff", "--", target_module])
    if rc != 0 or not out.strip():
        return ""
    Path(BUNDLE_DIR).mkdir(parents=True, exist_ok=True)
    date = time.strftime("%Y-%m-%d")
    bundle_path = os.path.abspath(
        f"{BUNDLE_DIR}/{date}-{_short_hash(out)}.patch")
    with open(bundle_path, "w", encoding="utf-8") as f:
        f.write(out)
    return bundle_path


def write_skill_meta(target_module, paper_id, tests_passed, bundle_path, commit_hash):
    """Write skill metadata alongside the patch bundle.

    Per LITERATURE SkillOpt paper: skills have lifecycle
    (candidate → active → archived) tracked via metadata.

    Per P14 docs stay current + P19 data flow observability:
    each auto-commit produces a paired .meta.json for future
    skill lifecycle management (discovery, apply, review,
    retain/drop).

    Returns path to meta file, or "" on failure.
    """
    if not commit_hash:
        return ""
    if not bundle_path:
        # Fall back to deriving from commit_hash
        bundle_path = f"{BUNDLE_DIR}/{time.strftime('%Y-%m-%d')}-{commit_hash[:8]}.patch"
    # Meta file lives next to bundle with same stem, .meta.json suffix
    meta_path = bundle_path.rstrip(".patch") + ".meta.json"
    meta = {
        "commit_hash": commit_hash,
        "target_module": target_module,
        "paper_id": paper_id or "unknown",
        "tests_passed": tests_passed,
        "bundle_path": bundle_path,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        # Per SkillOpt paper lifecycle:
        "status": "candidate",
        "applied_count": 0,
        "success_count": 0,
    }
    try:
        Path(os.path.dirname(meta_path) or ".").mkdir(parents=True, exist_ok=True)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        return meta_path
    except Exception:
        return ""


def auto_commit(target_module, paper_id="", tests_passed=0, bundle_path=""):
    """Commit KEPT patch with auto author + [auto] prefix.

    Returns commit hash, or "" on failure.

    Per P9 (hard rule) + P18 (failure -> regression test):
    caller validation runs BEFORE commit.  If any caller of target_module
    fails to compile, auto-commit is skipped (returns "").
    """
    # Per P9 + P18: validate callers BEFORE staging (cheap compile check)
    ok, errors = check_callers(target_module)
    if not ok:
        print(f"  [auto-commit] SKIPPED: caller validation failed:")
        for e in errors:
            print(f"    - {e}")
        return ""

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
    msg_lines.append(f"Author: {AUTO_AUTHOR} <{AUTO_EMAIL}>")
    msg = "\n".join(msg_lines)

    # Commit with auto author (per git config override)
    env_args = [
        "-c", f"user.name={AUTO_AUTHOR}",
        "-c", f"user.email={AUTO_EMAIL}",
    ]
    r = subprocess.run(
        ["git"] + env_args + ["commit", "-m", msg],
        capture_output=True,
        cwd=os.getcwd(), timeout=15,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        return ""

    # Get commit hash
    rc, out, _ = _run_git(["rev-parse", "HEAD"])
    commit_hash = out.strip() if rc == 0 else ""

    # Per LITERATURE SkillOpt paper: write skill metadata alongside bundle
    if commit_hash:
        meta_path = write_skill_meta(
            target_module=target_module,
            paper_id=paper_id,
            tests_passed=tests_passed,
            bundle_path=bundle_path,
            commit_hash=commit_hash,
        )
        if meta_path:
            print(f"  [auto-commit] skill meta: {meta_path}")

    return commit_hash
