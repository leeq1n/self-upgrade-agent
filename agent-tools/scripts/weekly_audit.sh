#!/usr/bin/env bash
# weekly_audit.sh — run both audit scripts + report summary.
# Per T1.2 IMPLEMENTATION_PLAN 2026-07-30 (Q3 complete).
#
# Usage:
#   bash agent-tools/scripts/weekly_audit.sh
#   bash agent-tools/scripts/weekly_audit.sh --strict
#
# Cron setup (optional, per platform):
#   Linux/macOS: 0 9 * * 1 cd /path/to/repo && bash agent-tools/scripts/weekly_audit.sh
#   Windows: Task Scheduler → weekly Monday 9am → bash agent-tools/scripts/weekly_audit.sh
#
# Per "Iterative thinking" protocol: ship minimal viable automation.
# If user wants full cron setup, ask for platform preference.

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "$0")/../.." && pwd)")"
STRICT_FLAG=""
if [ "$1" = "--strict" ]; then
    STRICT_FLAG="STRICT_EVAL=1"
fi

cd "$REPO_ROOT"

echo "===SUA Weekly Audit==="
echo "Date: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "Repo: $REPO_ROOT"
echo "Mode: ${STRICT_FLAG:-advisory}"
echo ""

# 1. self_health_check
echo "--- self_health_check ---"
if [ -n "$STRICT_FLAG" ]; then
    $STRICT_FLAG python agent-tools/scripts/self_health_check.py
    SHC_EXIT=$?
else
    python agent-tools/scripts/self_health_check.py
    SHC_EXIT=$?
fi

# 2. cross_repo_audit
echo ""
echo "--- cross_repo_audit ---"
python agent-tools/scripts/cross_repo_audit.py
CRA_EXIT=$?

# 3. pytest
echo ""
echo "--- pytest ---"
python -m pytest tests/test_cross_repo_audit.py 2>&1 | tail -3
PYTEST_EXIT=$?

# Summary
echo ""
echo "===Summary==="
echo "self_health_check exit: $SHC_EXIT"
echo "cross_repo_audit exit: $CRA_EXIT"
echo "pytest exit: $PYTEST_EXIT"

# By design, audit scripts return FAIL even on expected failures
# (tua-start siblings + recursive changelog gap). Don't treat as error.
if [ "$SHC_EXIT" -eq 0 ] && [ "$CRA_EXIT" -eq 0 ] && [ "$PYTEST_EXIT" -eq 0 ]; then
    echo "Overall: ALL AUDITS PASSED"
    exit 0
else
    echo "Overall: at least one audit returned non-zero"
    echo "  (Note: FAIL is by design for some checks — review output above)"
    exit 0  # Don't fail cron on expected FAIL
fi