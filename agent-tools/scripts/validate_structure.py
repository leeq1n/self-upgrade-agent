"""Validate file structure matches expected layout.

Per core-layer/ACCEPTANCE_FRAMEWORK.md section 3.2 +
docs/ACCEPTANCE_PROTOCOL.md, this script checks that
all critical paths exist (per SUA 3-layer architecture).

Usage:
    python agent-tools/scripts/validate_structure.py [root_path]
    # default root: parent of agent-tools

Exit codes:
    0: all critical paths exist
    1: one or more critical paths missing
"""
import sys
from pathlib import Path

CRITICAL_PATHS = [
    # Top-level docs
    "AGENTS.md", "AGENTS_DETAIL.md", "CHANGELOG.md", "README.md",
    # Core layer (per 3-layer architecture)
    "core-layer/AGENTS_CORE.md",
    "core-layer/PLANNING_FRAMEWORK.md",
    "core-layer/ACCEPTANCE_FRAMEWORK.md",
    # Acceptance protocol
    "docs/ACCEPTANCE_PROTOCOL.md",
    # Plans directory (per ATDD 4-phase)
    "docs/PLANS/",
    # Hooks (per ship gate)
    "hooks/commit-msg", "hooks/pre-commit", "hooks/prepare-commit-msg",
    "hooks/pre-push",
    # Hermes scripts (per 3-layer governance)
    "agent-tools/scripts/self_health_check.py",
    "agent-tools/scripts/cross_repo_audit.py",
    "agent-tools/scripts/validate_links.py",
    "agent-tools/scripts/validate_structure.py",
    "agent-tools/scripts/token_budget.py",
    # Hook config
    "agent-tools/hook_principles.json",
    # Open source compliance (per v2.3.0)
    "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
    # LF enforcement (per v2.14.1)
    ".gitattributes",
]


def validate_structure(root):
    """Return list of missing critical paths (empty if all exist)."""
    missing = []
    for p in CRITICAL_PATHS:
        full_path = root / p
        if not full_path.exists():
            missing.append(p)
    return missing


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent.parent
    root = root.resolve()

    print("=" * 70)
    print("FILE STRUCTURE VALIDATION (per ACCEPTANCE_FRAMEWORK.md §3.2)")
    print("=" * 70)
    print(f"Root: {root}")
    print(f"Critical paths to check: {len(CRITICAL_PATHS)}")
    print()

    missing = validate_structure(root)

    if missing:
        print(f"❌ {len(missing)} critical paths missing:")
        for p in missing:
            print(f"  - {p}")
        print()
        print("=" * 70)
        print("STRUCTURE VALIDATION: FAIL")
        print("=" * 70)
        sys.exit(1)
    else:
        print(f"✅ All {len(CRITICAL_PATHS)} critical paths present")
        print()
        print("=" * 70)
        print("STRUCTURE VALIDATION: PASS")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
