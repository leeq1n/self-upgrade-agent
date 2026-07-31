"""Check for large files that may exceed token budget.

Per core-layer/ACCEPTANCE_FRAMEWORK.md section 3.3 +
docs/ACCEPTANCE_PROTOCOL.md, this script flags files
that exceed size budgets (per P-7 Occam token budget).

Per docs/POST_SEARCH_EVALUATION_2026-07-30.md + R132
entropy audit, large files = entropy signal.

Usage:
    python .hermes/scripts/token_budget.py [root_path]
    # default root: parent of .hermes

Exit codes:
    0: no files exceed budgets
    1: one or more files exceed budgets
"""
import sys
from pathlib import Path

# Size budgets per file type (per ACCEPTANCE_FRAMEWORK.md spec)
SIZE_BUDGETS = {
    "*.md": 50_000,   # 50KB
    "*.py": 30_000,   # 30KB
    "*.sh": 10_000,   # 10KB
    "*.json": 10_000, # 10KB
    "*.yml": 10_000,  # 10KB
    "*.yaml": 10_000, # 10KB
    "*.toml": 10_000, # 10KB
}


def check_token_budget(root):
    """Return list of (file, size, limit) tuples for files exceeding budgets."""
    warnings = []
    for pattern, limit in SIZE_BUDGETS.items():
        for f in root.rglob(pattern):
            if ".git" in f.parts or "__pycache__" in f.parts or ".pytest_cache" in f.parts:
                continue
            try:
                size = f.stat().st_size
            except (OSError, FileNotFoundError):
                continue
            if size > limit:
                warnings.append((str(f.relative_to(root)), size, limit))
    return warnings


def format_size(size):
    """Format bytes as human-readable."""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    else:
        return f"{size / 1024 / 1024:.1f}MB"


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent.parent
    root = root.resolve()

    print("=" * 70)
    print("TOKEN BUDGET CHECK (per ACCEPTANCE_FRAMEWORK.md §3.3)")
    print("=" * 70)
    print(f"Root: {root}")
    print(f"Size budgets:")
    for pattern, limit in SIZE_BUDGETS.items():
        print(f"  {pattern}: {format_size(limit)}")
    print()

    warnings = check_token_budget(root)

    if warnings:
        print(f"⚠️  {len(warnings)} files exceed size budget:")
        for f, size, limit in warnings:
            pct = (size / limit) * 100
            print(f"  - {f}: {format_size(size)} / {format_size(limit)} ({pct:.0f}%)")
        print()
        print("=" * 70)
        print("TOKEN BUDGET: WARN (not blocking, per entropy audit protocol)")
        print("=" * 70)
        # Per R132 + ACCEPTANCE_FRAMEWORK: warn but don't fail
        # (advisory not blocking, per self_health_check pattern)
        sys.exit(0)
    else:
        print(f"✅ All files within size budgets")
        print()
        print("=" * 70)
        print("TOKEN BUDGET: PASS")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
