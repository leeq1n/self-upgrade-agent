"""hook_principles_loader.py — load principles registry from JSON.

Single source of truth for:
- active P-n whitelist (for commit-msg hook)
- L4 boundary tiers (for audit scripts)
- pre-task vocabulary (for self_health_check)

Replaces hardcoded whitelists in hooks/commit-msg + scripts.
"""
import json
import os
import sys
from pathlib import Path

# Find repo root (script lives in agent-tools/scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
REGISTRY_PATH = REPO_ROOT / "agent-tools" / "hook_principles.json"


def load_registry():
    """Load hook_principles.json. Fail loud if missing."""
    if not REGISTRY_PATH.exists():
        print(f"ERROR: registry not found at {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(2)

    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_active_principles():
    """Return sorted list of active P-n values (e.g., ['P1', 'P2', ...])."""
    reg = load_registry()
    return reg["principles"]["active"]


def get_p_regex():
    """Return grep-compatible regex for active P-n values.

    Excludes merged P6 + P24; includes demoted P15/P16 + lifted P28/P29.
    """
    active = get_active_principles()
    # Strip 'P' prefix for regex
    nums = [int(p[1:]) for p in active]
    # Build alternation
    return f"P({'|'.join(str(n) for n in sorted(nums, key=int))})"


def get_l4_boundary():
    """Return L4 boundary tier definitions."""
    reg = load_registry()
    return reg["l4_boundary"]


def main():
    """CLI entry: print active P-n regex for use by shell hooks."""
    if len(sys.argv) > 1 and sys.argv[1] == "--p-regex":
        print(get_p_regex())
    elif len(sys.argv) > 1 and sys.argv[1] == "--active-list":
        print(" ".join(get_active_principles()))
    else:
        # Default: dump full registry
        reg = load_registry()
        print(json.dumps(reg, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()