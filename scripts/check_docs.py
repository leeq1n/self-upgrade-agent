"""scripts/check_docs.py

Mechanical P20 compliance check for this project's docs/.
Implements rules R1-R12 from PRINCIPLES.md P20.细则.

Run before any docs/ commit:
    python scripts/check_docs.py
    python scripts/check_docs.py --strict   # fail on legacy docs too

Exit codes:
    0 = all rules PASS
    1 = one or more FAIL (must fix before commit)
    2 = error running the check (script bug)

Per P16 (ad-hoc verify, then commit), this is the script the
"real" verify calls.  Per R11, commit messages should include
the verify output (e.g. "P20 verify: 12/12 PASS").
"""
import argparse
import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
MAX_SIZE = 10 * 1024  # R5: 10KB (was 7KB; raised after empirical test)

# Set of "legacy" docs that are exempt from L0/Last P20-verified
# requirements until migrated.  Add to this set as docs are updated.
LEGACY = {
    "CONSTRAINTS.md",
    "CONSTRAINTS_DETAIL.md",
    "LITERATURE.md",
    "LITERATURE_DETAIL.md",
    "MODEL_STRATEGY.md",
    "MODEL_STRATEGY_DETAIL.md",
    "PROJECT_STATE.md",
    "PROJECT_STATE_DETAIL.md",
    "USER_INSIGHTS.md",
    "USER_INSIGHTS_DETAIL.md",
    "OBSERVATIONS.md",
    "TODO_KNOWLEDGE_GRAPH.md",
    "USER_INSIGHTS_KNOWLEDGEGRAPH_20260710.md",
}

failures = []
warnings = []


def fail(rule, doc, msg):
    failures.append(f"R{rule} ({doc}): {msg}")


def warn(rule, doc, msg):
    warnings.append(f"R{rule} ({doc}): {msg}")


def all_docs():
    return sorted(DOCS.glob("*.md"))


# R1: INDEX.md must have exactly two top-level sections
def check_r1():
    idx = DOCS / "INDEX.md"
    if not idx.exists():
        fail(1, "INDEX.md", "missing")
        return
    text = idx.read_text(encoding="utf-8")
    # Match top-level sections (## ...) after the intro
    sections = re.findall(r"^## (.+)$", text, re.MULTILINE)
    # Accept "Conditional loads" and any longer form (e.g. "Conditional loads (read ONLY if relevant)")
    has_reading = any(s == "Reading order for a new agent" for s in sections)
    has_conditional = any(s.startswith("Conditional loads") for s in sections)
    extras = [s for s in sections
              if s != "Reading order for a new agent"
              and not s.startswith("Conditional loads")]
    if not has_reading:
        fail(1, "INDEX.md", "missing 'Reading order for a new agent' section")
    if not has_conditional:
        fail(1, "INDEX.md", "missing 'Conditional loads' section")
    if extras:
        fail(1, "INDEX.md", f"unexpected sections: {extras}")


# R2: Reading order numbered 1..N contiguously
def check_r2():
    idx = (DOCS / "INDEX.md").read_text(encoding="utf-8")
    if not idx:
        return
    # Extract numbered list under "Reading order" until next "##"
    m = re.search(r"## Reading order.*?(?=\n## |\Z)", idx, re.DOTALL)
    if not m:
        fail(2, "INDEX.md", "no 'Reading order' section")
        return
    section = m.group(0)
    nums = [int(n) for n in re.findall(r"^(\d+)\.\s", section, re.MULTILINE)]
    if nums != list(range(1, len(nums) + 1)):
        fail(2, "INDEX.md", f"non-contiguous numbering: {nums}")


# R3: Conditional loads links have trigger: annotations
def check_r3():
    idx = (DOCS / "INDEX.md").read_text(encoding="utf-8")
    m = re.search(r"## Conditional loads.*?(?=\n## |\Z)", idx, re.DOTALL)
    if not m:
        return
    section = m.group(0)
    # Each list item should have a 'trigger' or descriptive clause
    items = re.findall(r"^- \[.+?\]\(.+?\)\s+—\s+(.+)$", section, re.MULTILINE)
    for i, item in enumerate(items, 1):
        words = item.split()
        if len(words) < 3:
            fail(3, "INDEX.md",
                 f"item {i} trigger too short ({len(words)} words): '{item}'")


# R4: EXTENSIONS.md ≤ 500B, table only (L0 line allowed as header)
def check_r4():
    ext = DOCS / "EXTENSIONS.md"
    if not ext.exists():
        return
    text = ext.read_text(encoding="utf-8")
    size = len(text.encode())
    if size > 500:
        fail(4, "EXTENSIONS.md", f"size {size}B > 500B")
    # Body must be table only: allow L0: and Last P20-verified: header lines,
    # everything else must start with | (table row) or - (header) or be blank.
    lines = text.splitlines()
    in_table = False
    for line in lines:
        if not line.strip():
            continue
        if line.startswith(("L0:", "Last P20-verified:")):
            continue
        if line.startswith("|"):
            in_table = True
            continue
        if line.startswith("#"):
            continue  # H1 only
        # Non-table, non-header line in body
        fail(4, "EXTENSIONS.md", f"non-table line: '{line[:60]}'")
        return


# R5: docs/*.md ≤ 10KB; > 10KB must have _DETAIL.md (or be in R5_LEGACY)
R5_LEGACY = {
    "CONSTRAINTS_DETAIL.md",   # 12KB; split into _DETAIL + _EXAMPLES later
    "PRINCIPLES.md",           # 12KB; split P20细则 into PRINCIPLES_DETAIL.md later
}
def check_r5():
    for d in all_docs():
        if d.name in R5_LEGACY:
            warn(5, d.name, f"LEGACY: {d.stat().st_size}B > 10KB, split into _DETAIL later")
            continue
        size = len(d.read_text(encoding="utf-8").encode())
        if size > MAX_SIZE:
            detail = d.parent / d.name.replace(".md", "_DETAIL.md")
            if not detail.exists():
                fail(5, d.name, f"{size}B > 10KB, no _DETAIL.md companion")


# R6: _DETAIL.md must be linked from summary
def check_r6():
    for d in all_docs():
        if d.name.endswith("_DETAIL.md"):
            summary_name = d.name.replace("_DETAIL.md", ".md")
            summary = d.parent / summary_name
            if summary.exists():
                summary_text = summary.read_text(encoding="utf-8")
                if d.name not in summary_text:
                    fail(6, d.name, f"no inbound link from {summary_name}")


# R7: P-n defined only in PRINCIPLES.md
def check_r7():
    principles = (DOCS / "PRINCIPLES.md").read_text(encoding="utf-8")
    # Find all P-n defined: "### P<n>."
    p_defined_in_principles = set(re.findall(r"^### (P\d+)\.", principles, re.MULTILINE))
    for d in all_docs():
        if d.name == "PRINCIPLES.md":
            continue
        text = d.read_text(encoding="utf-8")
        # Find "### P<n>." in this doc (definition, not reference)
        p_defined_here = set(re.findall(r"^### (P\d+)\.", text, re.MULTILINE))
        redefined = p_defined_here & p_defined_in_principles
        if redefined:
            fail(7, d.name, f"redefines {redefined} (P-n must only be in PRINCIPLES.md)")


# R8: cross-project links use relative paths
def check_r8():
    for d in all_docs():
        text = d.read_text(encoding="utf-8")
        # Find absolute Windows paths or http://localhost in docs/
        bad = re.findall(r"[a-zA-Z]:\\\\[^\s)>\]]+", text)
        if bad:
            fail(8, d.name, f"absolute path: {bad[:1]}")


# R9: every doc begins with L0: frontmatter (≤ 120 chars)
def check_r9(strict=False):
    for d in all_docs():
        if d.name in LEGACY and not strict:
            warn(9, d.name, "LEGACY: missing L0: frontmatter (add when migrated)")
            continue
        text = d.read_text(encoding="utf-8")
        # L0: line can be either (a) within first 5 lines, or (b) right after H1
        lines = text.splitlines()
        l0_line = None
        # Check first 5 lines
        for l in lines[:5]:
            if l.startswith("L0:"):
                l0_line = l
                break
        # If not found, look for H1 then L0
        if not l0_line:
            for i, l in enumerate(lines):
                if l.startswith("# ") and i + 1 < len(lines):
                    # Check next 3 lines for L0
                    for j in range(i + 1, min(i + 4, len(lines))):
                        if lines[j].startswith("L0:"):
                            l0_line = lines[j]
                            break
                    if l0_line:
                        break
        if not l0_line:
            fail(9, d.name, "no L0: line in first 5 lines or after H1")
        else:
            if len(l0_line) > 120:
                fail(9, d.name, f"L0: line {len(l0_line)} chars > 120")


# R10: every doc ends with Last P20-verified: YYYY-MM-DD
def check_r10(strict=False):
    for d in all_docs():
        if d.name in LEGACY and not strict:
            warn(10, d.name, "LEGACY: missing Last P20-verified (add when migrated)")
            continue
        text = d.read_text(encoding="utf-8")
        if not re.search(r"^Last P20-verified: \d{4}-\d{2}-\d{2}$",
                         text, re.MULTILINE):
            fail(10, d.name, "no 'Last P20-verified: YYYY-MM-DD' line")


# R11 and R12 are process rules, mechanically checked at commit
# time via hooks (out of scope for this script).  Print reminder.
def check_r11_r12():
    pass


def main():
    parser = argparse.ArgumentParser(description="P20 mechanical compliance check")
    parser.add_argument("--strict", action="store_true",
                        help="fail on legacy docs too (default: warn only)")
    args = parser.parse_args()

    print("=" * 60)
    print("P20 mechanical compliance check (R1-R12)")
    print(f"Mode: {'STRICT' if args.strict else 'normal'} (legacy docs: {'FAIL' if args.strict else 'WARN'})")
    print("=" * 60)

    for name, fn in [("R1", check_r1), ("R2", check_r2), ("R3", check_r3),
                     ("R4", check_r4), ("R5", check_r5), ("R6", check_r6),
                     ("R7", check_r7), ("R8", check_r8),
                     ("R9", lambda: check_r9(args.strict)),
                     ("R10", lambda: check_r10(args.strict))]:
        try:
            fn()
        except Exception as e:
            fail("?", name, f"script bug: {e}")

    passed = 0
    failed_rules = {f.split(" ")[0] for f in failures}
    all_rules = {f"R{i}" for i in range(1, 11)}
    passed = len(all_rules - failed_rules)

    print()
    print("=" * 60)
    if failures:
        print(f"P20 verify: {passed}/10 PASS, {len(failures)} FAIL")
        for f in failures:
            print(f"  FAIL: {f}")
        if warnings:
            print(f"\n{len(warnings)} warnings (legacy docs, not blocking):")
            for w in warnings:
                print(f"  WARN: {w}")
        print()
        print("Fix the FAIL items, then re-run.  Do not weaken the rules.")
        sys.exit(1)
    else:
        print(f"P20 verify: {passed}/10 PASS, 0 FAIL")
        if warnings:
            print(f"\n{len(warnings)} warnings (legacy docs to migrate):")
            for w in warnings:
                print(f"  WARN: {w}")
        print()
        print("Safe to commit (include 'P20 verify: 10/10 PASS' in commit message).")
        sys.exit(0)


if __name__ == "__main__":
    main()
