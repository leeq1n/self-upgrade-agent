#!/usr/bin/env bash
# install-hooks.sh — install SUA hooks + their script dependencies
# into the CURRENT project's .git/hooks/ + .hermes/.
#
# WHY: hooks/commit-msg and hooks/pre-commit reference
# .hermes/scripts/*.py + .hermes/hook_principles.json. Copying
# only the hooks (as older README suggested) breaks commit-msg
# with "hook_principles_loader.py not found". This script
# installs hooks AND dependencies atomically.
#
# Usage (run from the TARGET project, not from SUA):
#   bash .sua/install-hooks.sh            # install hooks + deps
#   bash .sua/install-hooks.sh --dry-run  # preview only
#   bash .sua/install-hooks.sh --force    # overwrite existing hooks
#
# Requires: bash, git, python (for loader validation)

set -e

# SUA_DIR: source of hooks + scripts. Resolve order:
#   1. $SUA_DIR env var (explicit, e.g. SUA_DIR=/path/to/.sua)
#   2. $1 positional arg (bash install-hooks.sh /path/to/.sua)
#   3. Parent of this script IF hooks/ exists beside it
#      (running from inside SUA: bash .sua/install-hooks.sh)
#   4. Common clone location: ./.sua
if [ -n "$SUA_DIR" ]; then
    SUA_DIR="$(cd "$SUA_DIR" && pwd)"
elif [ -n "${1:-}" ] && [ -d "${1%/}/hooks" ]; then
    SUA_DIR="$(cd "$1" && pwd)"
    shift
elif [ -d "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/hooks" ]; then
    SUA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -d "$(pwd)/.sua/hooks" ]; then
    SUA_DIR="$(cd "$(pwd)/.sua" && pwd)"
else
    echo "ERROR: cannot locate SUA source (hooks/ dir)." >&2
    echo "  Usage: bash <sua-path>/install-hooks.sh   (run from target project)" >&2
    echo "  Or:    SUA_DIR=/path/to/.sua bash install-hooks.sh" >&2
    exit 1
fi

TARGET="$(git rev-parse --show-toplevel 2>/dev/null || echo '')"

if [ -z "$TARGET" ]; then
    echo "ERROR: run this script inside a git repository (target project)." >&2
    exit 1
fi

DRY_RUN=false
FORCE=false
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --force) FORCE=true ;;
        --help|-h)
            echo "Usage: $0 [--dry-run] [--force]"
            echo "  Install SUA hooks + script dependencies into this project."
            exit 0
            ;;
    esac
done

echo "=== SUA hook installer ==="
echo "  SUA source:   $SUA_DIR"
echo "  Target repo:  $TARGET"
echo "  Dry run:      $DRY_RUN"
echo ""

# 1. Install hook scripts (commit-msg / pre-commit / prepare-commit-msg / pre-push)
HOOKS=(commit-msg pre-commit prepare-commit-msg pre-push)
for h in "${HOOKS[@]}"; do
    if [ -f "$SUA_DIR/hooks/$h" ]; then
        dest="$TARGET/.git/hooks/$h"
        if [ -f "$dest" ] && [ "$FORCE" != "true" ]; then
            echo "  ⚠️  hook $h already exists — use --force to overwrite"
            continue
        fi
        if [ "$DRY_RUN" = "true" ]; then
            echo "  [dry-run] would copy hooks/$h → .git/hooks/$h"
        else
            cp "$SUA_DIR/hooks/$h" "$dest"
            chmod +x "$dest"
            echo "  ✅ hooks/$h installed"
        fi
    fi
done

# 2. Install script dependencies (.hermes/scripts/*.py referenced by hooks)
NEEDED_SCRIPTS=(
    hook_principles_loader.py
    eval_before.py
    self_health_check.py
    cross_repo_audit.py
    validate_links.py
    verify_after.py
    m_n29_5step.py
    release_audit.py
)
mkdir -p "$TARGET/.hermes/scripts"
for s in "${NEEDED_SCRIPTS[@]}"; do
    src="$SUA_DIR/.hermes/scripts/$s"
    dest="$TARGET/.hermes/scripts/$s"
    if [ -f "$src" ]; then
        # Skip if source and dest are the same file (running from SUA itself)
        if [ "$src" = "$dest" ] || [ "$(cd "$(dirname "$src")" && pwd)/$(basename "$src")" = "$dest" ]; then
            echo "  ✅ .hermes/scripts/$s (already in place)"
            continue
        fi
        if [ "$DRY_RUN" = "true" ]; then
            echo "  [dry-run] would copy .hermes/scripts/$s"
        else
            cp "$src" "$dest"
            echo "  ✅ .hermes/scripts/$s installed"
        fi
    fi
done

# 3. Install principles registry (single source of truth per Q2 closure)
if [ -f "$SUA_DIR/.hermes/hook_principles.json" ]; then
    if [ "$DRY_RUN" = "true" ]; then
        echo "  [dry-run] would copy .hermes/hook_principles.json"
    else
        cp "$SUA_DIR/.hermes/hook_principles.json" "$TARGET/.hermes/hook_principles.json"
        echo "  ✅ .hermes/hook_principles.json installed"
    fi
fi

# 4. Validate loader works (skip in dry-run)
if [ "$DRY_RUN" != "true" ]; then
    echo ""
    echo "=== Validation ==="
    if python "$TARGET/.hermes/scripts/hook_principles_loader.py" --active-list >/dev/null 2>&1; then
        echo "  ✅ hook_principles_loader.py works (P-n registry loaded)"
    else
        echo "  ⚠️  loader validation failed — check python availability" >&2
    fi
fi

echo ""
echo "=== Done. Hooks active on next commit. ==="
echo "  Test: git commit -m \"test (P7)\""
echo "  Remove: bash .hermes/scripts/uninstall.sh (in target project)"
