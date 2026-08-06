#!/usr/bin/env python3
"""release_audit.py — pre-release check (M-n 36, per user message 2026-07-16
retrospective audit).

Per user message "判断下问题在哪，怎么处理":
- 5 checks codified for release preparation:
  1. Commit history cleanliness (suggest squash)
  2. Tag points at HEAD (suggest move forward)
  3. CHANGELOG.md exists + records pre-release
  4. Build artifact (zip) matches tag tree
  5. Documentation cross-refs + integrity

Usage:
    python agent-tools/scripts/release_audit.py [target_repo]

Default target: SUA itself.  For sibling repos:
    python agent-tools/scripts/release_audit.py ../agent-reflection-skill

Exit codes:
    0 — PASS (all 5 checks OK, or warnings only)
    1 — FAIL (at least 1 check found a hard issue)
"""

from __future__ import annotations
import argparse
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path


def git(*args, cwd: Path) -> tuple[int, str, str]:
    """Run git command in cwd, return (rc, stdout, stderr)."""
    r = subprocess.run(
        ["git", *args],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=cwd, timeout=15,
    )
    return r.returncode, r.stdout, r.stderr


def check_1_history_cleanliness(repo: Path, max_commits: int = 5) -> tuple[bool, str]:
    """Check main branch commit count is reasonable for release."""
    rc, out, _ = git("log", "--oneline", cwd=repo)
    if rc != 0:
        return False, "git log failed"
    commits = [l for l in out.strip().splitlines() if l]
    if len(commits) > max_commits:
        return False, (
            f"main has {len(commits)} commits (threshold {max_commits}); "
            f"consider squash for clean release"
        )
    return True, f"main has {len(commits)} commits (≤ {max_commits}, OK)"


def check_2_tag_at_head(repo: Path, tag: str) -> tuple[bool, str]:
    """Check tag dereferences to HEAD."""
    rc, head, _ = git("rev-parse", "HEAD", cwd=repo)
    if rc != 0:
        return False, "git rev-parse HEAD failed"
    rc, tag_hash, _ = git("rev-parse", f"{tag}^{{commit}}", cwd=repo)
    if rc != 0:
        return False, f"tag {tag} not found or invalid"
    if head.strip() != tag_hash.strip():
        return False, (
            f"tag {tag} ({tag_hash[:8]}) != HEAD ({head.strip()[:8]}); "
            f"consider 'git tag -f {tag}' to move forward"
        )
    return True, f"tag {tag} points at HEAD"


def check_3_changelog_exists(repo: Path) -> tuple[bool, str]:
    """Check CHANGELOG.md exists at root."""
    cl = repo / "CHANGELOG.md"
    if not cl.exists():
        return False, "CHANGELOG.md not found at repo root"
    text = cl.read_text(encoding="utf-8")
    has_pre = "Pre-1.0.0" in text or "pre-release" in text.lower()
    if not has_pre:
        return False, "CHANGELOG.md exists but lacks pre-release history"
    return True, f"CHANGELOG.md exists with pre-release history ({len(text)} chars)"


def check_4_artifact_matches_tag(repo: Path, tag: str) -> tuple[bool, str]:
    """Check zip artifact (if exists) matches tag tree."""
    # Find zip files in parent dir (typical: ../{repo_name}.zip)
    zip_candidates = list(repo.parent.glob("*.zip"))
    repo_name = repo.name
    matching_zips = [z for z in zip_candidates if repo_name in z.name]

    if not matching_zips:
        # No zip yet (no release built) — not a failure, just skipped
        return True, "no zip artifact found (skip)"

    # Get tag tree file list
    rc, out, _ = git("ls-tree", "-r", "--name-only", tag, cwd=repo)
    if rc != 0:
        return False, f"git ls-tree {tag} failed"
    tag_files = sorted(out.strip().splitlines())

    # Check first matching zip
    zpath = matching_zips[0]
    with zipfile.ZipFile(zpath) as zf:
        zip_names = sorted(
            n[len(f"{repo_name}/"):] if n.startswith(f"{repo_name}/") else n
            for n in zf.namelist()
        )

    if tag_files != zip_names:
        return False, (
            f"zip {zpath.name} file list differs from tag {tag}: "
            f"{len(zip_names)} in zip, {len(tag_files)} in tag"
        )
    return True, f"zip {zpath.name} matches tag {tag} ({len(tag_files)} files)"


def check_5_docs_cross_refs(repo: Path) -> tuple[bool, str]:
    """Check AGENTS.md / README.md / VERIFICATION.md exist + reference version."""
    issues = []
    for fname in ["AGENTS.md", "README.md", "VERIFICATION.md"]:
        f = repo / fname
        if not f.exists():
            issues.append(f"{fname} missing")
            continue
        text = f.read_text(encoding="utf-8")
        # Version reference: vX.Y.Z or "Version" OR P-n / M-n refs (for SUA)
        has_v = bool(re.search(
            r"v?\d+\.\d+\.\d+|version|Version|P\d+|M-n \d+",
            text
        ))
        if not has_v:
            issues.append(f"{fname} no version reference")

    if issues:
        return False, f"docs issues: {', '.join(issues)}"
    return True, "AGENTS.md + README.md + VERIFICATION.md have version refs"


def main() -> int:
    parser = argparse.ArgumentParser(description="M-n 36 release audit")
    parser.add_argument("target", nargs="?",
                        help="target repo path (default: SUA)")
    args = parser.parse_args()

    target = Path(args.target).resolve() if args.target else Path(__file__).resolve().parents[2]
    tag = "v1.0.0"  # TODO: detect from package metadata or arg

    print("=" * 60)
    print(f"M-N 36 RELEASE AUDIT (target: {target.name})")
    print("=" * 60)

    checks = [
        ("1. History cleanliness", check_1_history_cleanliness(target)),
        ("2. Tag at HEAD", check_2_tag_at_head(target, tag)),
        ("3. CHANGELOG.md", check_3_changelog_exists(target)),
        ("4. Artifact matches tag", check_4_artifact_matches_tag(target, tag)),
        ("5. Docs cross-refs", check_5_docs_cross_refs(target)),
    ]

    print("\nChecks:")
    all_pass = True
    for label, (ok, detail) in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label}: {detail}")
        if not ok:
            all_pass = False

    print("\n" + "=" * 60)
    if all_pass:
        print(f"RESULT: PASS (all 5 checks for {target.name})")
        return 0
    print(f"RESULT: FAIL (1+ checks failed for {target.name})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
