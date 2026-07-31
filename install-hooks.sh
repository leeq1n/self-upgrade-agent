#!/usr/bin/env bash
# install-hooks.sh — install SUA hooks into the CURRENT project's
# .git/hooks/, with script paths rewritten to point INSIDE the SUA
# clone (.sua/.hermes/scripts/). Target project stays clean: no
# .hermes/ dir, no script copies, one command.
#
# WHY: hooks/commit-msg + pre-commit reference .hermes/scripts/*.py
# + hook_principles.json. Copying only the hooks breaks commit-msg
# ("hook_principles_loader.py not found"). Copying scripts into the
# target's .hermes/ pollutes the project and looks alien to codex /
# claude (hermes-specific dir name). Instead: rewrite paths to
# $SUA_DIR (wherever SUA lives), so the target project only gains
# .git/hooks/ entries — nothing else.
#
# Usage (run from the TARGET project):
#   bash .sua/install-hooks.sh            # install (path-rewritten)
#   bash .sua/install-hooks.sh --dry-run  # preview
#   bash .sua/install-hooks.sh --force    # overwrite existing hooks
#   SUA_DIR=/path/to/.sua bash .sua/install-hooks.sh  # explicit source
#
# Requires: bash, git. Python only needed at runtime (commit hooks).

set -e

# MSYS self-bootstrap: when bash is launched from Windows cmd
# (via install-hooks.bat), PATH lacks git's /usr/bin (sed, cp,
# etc. are not found). Derive git root from $BASH (bash always
# points $BASH at itself; `command -v bash` from cmd PATH may
# resolve WSL bash instead — unreliable).
# NOTE: avoid external cmds here (dirname etc. may be missing too).
case "$PATH" in
  */usr/bin*)
    ;;
  *)
    BASH_SELF="${BASH:-$0}"
    BASH_DIR="${BASH_SELF%/*}"          # bash's dir (pure expansion)
    for CAND in "$BASH_DIR" "$BASH_DIR/.." "$BASH_DIR/../.."; do
      if [ -d "$CAND" ] && [ -x "$CAND/sed" ]; then
        export PATH="$CAND:$PATH"
        break
      fi
    done
    ;;
esac

# --- Resolve SUA_DIR (source of hooks) ---
# 1. $SUA_DIR env var
# 2. $1 positional arg (dir containing hooks/)
# 3. This script's own dir IF hooks/ sits beside it (bash .sua/install-hooks.sh)
# 4. Common clone location: ./.sua
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
            echo "  Install SUA hooks into this project's .git/hooks/."
            echo "  Hook script paths are rewritten to point into SUA's"
            echo "  own .hermes/scripts/ — target project stays clean."
            exit 0
            ;;
    esac
done

echo "=== SUA hook installer ==="
echo "  SUA source:   $SUA_DIR"
echo "  Target repo:  $TARGET"
echo "  Dry run:      $DRY_RUN"
echo ""

# --- Path rewrite ---
# Hooks reference $REPO_ROOT/.hermes/scripts/... and
# $REPO_ROOT/.hermes/hook_principles.json. Rewrite to SUA's own dir
# so the target project needs NO .hermes/ at all.
# Windows: SUA_DIR may be an MSYS path (/c/...); hooks run under git
# bash (git for windows), so /c/... paths work. Keep POSIX form.
SUA_SCRIPTS="$SUA_DIR/.hermes/scripts"
SUA_JSON="$SUA_DIR/.hermes/hook_principles.json"

if [ ! -d "$SUA_SCRIPTS" ]; then
    echo "ERROR: $SUA_SCRIPTS not found — is this a SUA clone?" >&2
    exit 1
fi

# --- Install hooks (rewritten) ---
HOOKS=(commit-msg pre-commit prepare-commit-msg pre-push)
for h in "${HOOKS[@]}"; do
    src_hook="$SUA_DIR/hooks/$h"
    dest_hook="$TARGET/.git/hooks/$h"
    if [ ! -f "$src_hook" ]; then
        continue  # optional hook not in this SUA version
    fi
    if [ -f "$dest_hook" ] && [ "$FORCE" != "true" ]; then
        echo "  ⚠️  hook $h already exists — use --force to overwrite"
        continue
    fi
    if [ "$DRY_RUN" = "true" ]; then
        echo "  [dry-run] would install hooks/$h (paths → $SUA_DIR)"
        continue
    fi
    # Rewrite .hermes/scripts references to SUA's own location
    sed -e "s|\$REPO_ROOT/.hermes/scripts|$SUA_SCRIPTS|g" \
        -e "s|\$REPO_ROOT/.hermes/hook_principles.json|$SUA_JSON|g" \
        "$src_hook" > "$dest_hook"
    chmod +x "$dest_hook"
    echo "  ✅ hooks/$h installed (paths → SUA clone)"
done

# --- Validate loader (only when not dry-run) ---
if [ "$DRY_RUN" != "true" ]; then
    echo ""
    echo "=== Validation ==="
    if [ -f "$SUA_SCRIPTS/hook_principles_loader.py" ]; then
        # Windows: python needs a native path, not MSYS /c/... form.
        # Convert via cygpath when available; fall back to POSIX.
        LOADER="$SUA_SCRIPTS/hook_principles_loader.py"
        if command -v cygpath >/dev/null 2>&1; then
            LOADER="$(cygpath -w "$LOADER")"
        fi
        if python "$LOADER" --active-list >/dev/null 2>&1; then
            echo "  ✅ hook_principles_loader.py works (P-n registry loaded)"
        else
            echo "  ⚠️  loader validation failed — python not on PATH?" >&2
            echo "      Hooks need python available when git runs them." >&2
        fi
    fi
fi

echo ""
echo "=== Done. Hooks active on next commit. ==="
echo "  Test: git commit -m \"test (P7)\""
echo "  Remove: rm .git/hooks/commit-msg .git/hooks/pre-commit .git/hooks/prepare-commit-msg .git/hooks/pre-push"
echo "  (Target project has NO .hermes/ — SUA scripts stay in $SUA_DIR)"
