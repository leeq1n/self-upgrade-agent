#!/usr/bin/env python3
"""SUA self-health audit (L1 layer; does NOT modify L0 thinking layer).

Why this exists:
  SUA hooks enforce P-n cite in commit messages, but SUA does not
  enforce that the *agent itself* reflects on its reasoning quality.
  This script audits the most common form-vs-effect failures (per
  R137 + R75 + M-n 32) without modifying L0 thinking content.

What it audits (read-only, output as JSON):
  1. Recent commits cite P-n in *body*, not just title.
  2. CHANGELOG.md mentions the most recent git tag
     (post-release discipline check).
  3. agent-tools/scripts/ exists and contains eval_before +
     verify_after (hooks plumbing intact).
  4. No 'this repository IS the canonical X' sentence in
     user-facing files (R137 self-referential noise).
  5. No 'I promise / I will remember' in recent commit
     messages (R159 verbal-only commitment detector).

Output: JSON to stdout. CI integration: nonzero exit if any
check fails. By default the audit is *advisory*; fail-nonzero
is informational and the calling hook decides enforcement.

Run: python agent-tools/scripts/self_health_check.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path

SUA = Path(__file__).resolve().parents[2]


def _git(*args, cwd=SUA):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    ).stdout


def audit_recent_commits_pn_in_body(n=5):
    """Recent commits must cite a P-n in body, not just title.
    Parsing note: `git log --pretty=%H%n%s%n---BODY---%n%B`
    produces blocks separated by `---BODY---`. block[0] is
    sha+title; each subsequent block contains title (line 0)
    + body (lines[1:]). We split body from title this way.
    """
    failed = []
    out = _git("log", f"-{n}", "--pretty=%H%n%s%n---BODY---%n%B")
    blocks = out.split("---BODY---")
    for block in blocks[1:]:  # skip preamble (sha + title of most recent)
        lines = block.strip().splitlines()
        # Body is everything after the title (line 0).
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""
        sha_match = re.search(r"\b([a-f0-9]{7,40})\b", lines[0]) if lines else None
        sha = sha_match.group(1)[:10] if sha_match else "?"
        # Look for P-n cite: "P11", "P-11", "(P11"
        if not re.search(r"\bP-?\d+\b", body):
            failed.append(sha)
    return {"recent_commits_without_pn_in_body": failed}


def audit_changelog_covers_recent_tags():
    """CHANGELOG must mention every tag in `git tag`."""
    out = _git("tag", "--sort=-creatordate")
    tags = [t.strip() for t in out.splitlines() if t.strip().startswith("v")]
    if not tags:
        return {"missing_in_changelog": []}
    cl = (SUA / "CHANGELOG.md").read_text(encoding="utf-8", errors="replace")
    missing = [t for t in tags[:5] if t not in cl]
    return {"missing_in_changelog": missing}


def audit_sua_scripts_intact():
    p = SUA / "agent-tools" / "scripts"
    expected = ["eval_before.py", "verify_after.py"]
    missing = [e for e in expected if not (p / e).exists()]
    return {"missing_sua_scripts": missing}


def audit_no_self_referential_noise():
    """No 'this repo IS the canonical X' sentence in user-facing files."""
    bad_files = []
    bad_phrases = [
        "this repository is the canonical",
        "this repo is the canonical",
    ]
    for fname in ["README.md", "CONTRIBUTING.md", "CHANGELOG.md"]:
        p = SUA / fname
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace").lower()
        if any(b in text for b in bad_phrases):
            bad_files.append(fname)
    return {"files_with_self_referential_phrase": bad_files}


def audit_no_verbal_commitment_in_commits(n=10):
    """Detect 'I will/promise' phrases in recent commit messages."""
    pat = re.compile(
        r"\bi\s+(will|won't|shall|am going to)\s+"
        r"(remember|commit|ensure|promise|never\s+(forget|miss))",
        re.IGNORECASE,
    )
    out = _git("log", f"-{n}", "--pretty=%B")
    hits = []
    for line in out.splitlines():
        if pat.search(line):
            hits.append(line.strip()[:140])
    return {"commit_lines_with_verbal_commitment": hits}


def audit_recent_commits_cite_tradeoff(n=10):
    """Detect commits that claim delivery without trade-off language.

    Per SUA working principle: most decisions are gain-vs-loss trades.
    A commit body that asserts the change is good (delivered/shipped/fixed)
    without naming the trade-off (gain/lose/cost/reversibility) is a signal
    of the formal-but-substantive trap (R137). This check is *advisory*
    only — it does not block commits.
    """
    claim_pat = re.compile(
        r"\b(shipped|delivered|fixed|done|complete|solved|applied)\b",
        re.IGNORECASE,
    )
    tradeoff_pat = re.compile(
        r"\b(gain|loss|lose|trade[-\s]?off|cost|risk|reversib|downside|"
        r"vs\.|versus|优缺点|得与失)\b",
        re.IGNORECASE,
    )
    out = _git("log", f"-{n}", "--pretty=%H%n%s%n---BODY---%n%B")
    blocks = out.split("---BODY---")
    suspicious = []
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        body = "\n".join(lines[1:])
        if claim_pat.search(body) and not tradeoff_pat.search(body):
            sha_match = re.search(r"\b([a-f0-9]{7,40})\b", lines[0])
            sha = sha_match.group(1)[:10] if sha_match else "?"
            suspicious.append({
                "sha": sha,
                "title": lines[0],
                "snippet": next(
                    (ln.strip()[:120] for ln in lines[1:] if ln.strip()),
                    ""
                ),
            })
    return {"commits_claim_without_tradeoff_language": suspicious}


def audit_recent_commits_cite_mn34_pre_task(n=10):
    """Detect commits that lack M-n 34 pre-task scan language.

    Per early SUA AGENTS_CORE.md M-n 34, agent must document
    pre-task scan result (relevant P-n / M-n + 1-line reason)
    in plan / commit message before any "task done" claim.
    This check surfaces commits whose body omits the canonical
    M-n 34 vocabulary. Advisory, not blocking.
    """
    mn34_pat = re.compile(
        r"\b(M-?n\s*34|pre-?task|scan\s+result|5\s+primitives|"
        r"PRINCIPLES\.md|OPERATING_RULES\.md|preflight)\b",
        re.IGNORECASE,
    )
    out = _git("log", f"-{n}", "--pretty=%H%n%s%n---BODY---%n%B")
    blocks = out.split("---BODY---")
    missing = []
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        body = "\n".join(lines[1:])
        if not mn34_pat.search(body):
            sha_match = re.search(r"\b([a-f0-9]{7,40})\b", lines[0])
            sha = sha_match.group(1)[:10] if sha_match else "?"
            missing.append({
                "sha": sha,
                "title": lines[0],
            })
    return {"commits_without_mn34_pre_task_vocabulary": missing}


def main():
    report = {
        "audit_target": str(SUA),
        "audit_timestamp_utc": _git("-C", str(SUA), "log", "-1", "--pretty=%cI").strip() or "unknown",
        "checks": {
            "recent_commits_pn_in_body": audit_recent_commits_pn_in_body(),
            "changelog_covers_recent_tags": audit_changelog_covers_recent_tags(),
            "sua_scripts_intact": audit_sua_scripts_intact(),
            "no_self_referential_noise": audit_no_self_referential_noise(),
            "no_verbal_commitment_in_commits": audit_no_verbal_commitment_in_commits(),
            "recent_commits_cite_tradeoff": audit_recent_commits_cite_tradeoff(),
            "recent_commits_cite_mn34_pre_task": audit_recent_commits_cite_mn34_pre_task(),
        },
    }
    failures = []
    for name, c in report["checks"].items():
        for k, v in c.items():
            if isinstance(v, list) and v:
                failures.append(f"{name}.{k}")
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
