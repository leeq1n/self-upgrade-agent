#!/usr/bin/env bash
# uninstall.sh — cleanly remove SUA hooks + audit artifacts from a repo.
#
# Use case: User installed SUA into a project via `install_sua.sh`
# (which installed commit-msg + pre-commit hooks). This script
# removes them + optional audit scripts.
#
# Per A4 "Uninstaller angle" (per AGENTS.md "Multi-perspective audit angles"):
# "does uninstall clean remove everything?"
#
# Usage:
#   bash agent-tools/scripts/uninstall.sh             # remove hooks only
#   bash agent-tools/scripts/uninstall.sh --full      # remove hooks + agent-tools/ + AGENTS.md + core-layer/
#   bash agent-tools/scripts/uninstall.sh --dry-run   # show what would be removed

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo 'NOT_A_GIT_REPO')"
DRY_RUN=false
FULL=false

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --full) FULL=true ;;
        --help|-h)
            echo "Usage: $0 [--full] [--dry-run]"
            echo ""
            echo "Default: remove SUA hooks from .git/hooks/"
            echo "--full: also remove agent-tools/, AGENTS.md, core-layer/, hooks/"
            echo "--dry-run: show what would be removed without doing it"
            exit 0
            ;;
    esac
done

remove_file() {
    local f="$1"
    if [ -e "$f" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "[DRY-RUN] would remove: $f"
        else
            rm -f "$f"
            echo "  removed: $f"
        fi
    fi
}

remove_dir() {
    local d="$1"
    if [ -d "$d" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "[DRY-RUN] would remove dir: $d"
        else
            rm -rf "$d"
            echo "  removed dir: $d"
        fi
    fi
}

echo "===SUA Uninstall==="
echo "Repo: $REPO_ROOT"
echo "Mode: $([ "$FULL" = true ] && echo 'full' || echo 'hooks-only')"
echo "Dry run: $DRY_RUN"
echo ""

if [ "$REPO_ROOT" = "NOT_A_GIT_REPO" ]; then
    echo "ERROR: not a git repo. Cannot determine hooks location." >&2
    exit 1
fi

cd "$REPO_ROOT"

# Always: remove hooks
echo "--- Hooks ---"
remove_file ".git/hooks/commit-msg"
remove_file ".git/hooks/pre-commit"
remove_file ".git/hooks/prepare-commit-msg"

# Full mode: remove SUA infrastructure
if [ "$FULL" = true ]; then
    echo ""
    echo "--- SUA infrastructure ---"
    remove_dir "agent-tools"
    remove_file "AGENTS.md"
    remove_file "AGENTS_DETAIL.md"
    remove_dir "core-layer"
    remove_dir "hooks"
fi

echo ""
if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN] No changes made. Re-run without --dry-run to apply."
else
    echo "✅ SUA uninstall complete."
fi