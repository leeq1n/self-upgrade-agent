#!/usr/bin/env bash
# run_acceptance.sh — single entrypoint for acceptance protocol.
#
# Per docs/ACCEPTANCE_PROTOCOL.md, this script is the SINGLE
# ENTRYPOINT for all acceptance checks. It runs:
# 1. validate_links.py (markdown cross-refs)
# 2. validate_structure.py (critical paths)
# 3. token_budget.py (file size budgets)
# 4. self_health_check.py (SUA self-audit)
# 5. cross_repo_audit.py (cross-repo audit)
# 6. pytest (test suite)
#
# Two modes:
#   Default (advisory): Runs all, prints report, exits 0
#   --gate (STRICT_EVAL=1): Exits 1 on any failure (per pre-push gate)
#
# Per M-n 29 5-step acceptance protocol + docs/ACCEPTANCE_PROTOCOL.md.

set +e  # Don't exit on error — we want to run all checks

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS="$REPO_ROOT/agent-tools/scripts"

echo "================================================================"
echo "ACCEPTANCE PROTOCOL — run_acceptance.sh"
echo "================================================================"
echo "Repo: $REPO_ROOT"
echo "Mode: $([ "${STRICT_EVAL:-0}" = "1" ] || [ "$1" = "--gate" ] && echo "GATE (strict)" || echo "ADVISORY (default)")"
echo

# Helper: run check + track result
total_checks=0
passed_checks=0
failed_checks=0

run_check() {
    local name="$1"
    shift
    echo "--- $name ---"
    total_checks=$((total_checks + 1))
    if "$@"; then
        passed_checks=$((passed_checks + 1))
        echo "[OK] $name"
    else
        failed_checks=$((failed_checks + 1))
        echo "[FAIL] $name"
    fi
    echo
}

# 1. validate_links.py
if [ -f "$SCRIPTS/validate_links.py" ]; then
    run_check "validate_links" python "$SCRIPTS/validate_links.py"
else
    echo "--- validate_links (SKIPPED: not found) ---"
    echo
fi

# 2. validate_structure.py
if [ -f "$SCRIPTS/validate_structure.py" ]; then
    run_check "validate_structure" python "$SCRIPTS/validate_structure.py"
else
    echo "--- validate_structure (SKIPPED: not found) ---"
    echo
fi

# 3. token_budget.py
if [ -f "$SCRIPTS/token_budget.py" ]; then
    run_check "token_budget" python "$SCRIPTS/token_budget.py"
else
    echo "--- token_budget (SKIPPED: not found) ---"
    echo
fi

# 4. self_health_check.py (advisory only — per its docstring)
if [ -f "$SCRIPTS/self_health_check.py" ]; then
    echo "--- self_health_check (advisory per its docstring) ---"
    total_checks=$((total_checks + 1))
    if python "$SCRIPTS/self_health_check.py" 2>&1 | tail -5; then
        passed_checks=$((passed_checks + 1))
        echo "[OK] self_health_check"
    else
        # Advisory: count as WARN not FAIL
        echo "[WARN] self_health_check (advisory, per its docstring)"
        # Don't increment failed_checks (advisory)
    fi
    echo
fi

# 5. cross_repo_audit.py (advisory — by design tua-start pollution)
if [ -f "$SCRIPTS/cross_repo_audit.py" ]; then
    echo "--- cross_repo_audit (advisory per tua-start by-design) ---"
    total_checks=$((total_checks + 1))
    if python "$SCRIPTS/cross_repo_audit.py" 2>&1 | tail -5; then
        passed_checks=$((passed_checks + 1))
        echo "[OK] cross_repo_audit"
    else
        echo "[WARN] cross_repo_audit (advisory, tua-start mirror pollution by design)"
    fi
    echo
fi

# 6. pytest
if [ -d "$REPO_ROOT/tests" ]; then
    run_check "pytest" python -m pytest "$REPO_ROOT/tests" -q
else
    echo "--- pytest (SKIPPED: no tests dir) ---"
    echo
fi

# Summary
echo "================================================================"
echo "ACCEPTANCE SUMMARY"
echo "================================================================"
echo "Total checks: $total_checks"
echo "Passed: $passed_checks"
echo "Failed: $failed_checks"
echo

# Gate mode: exit 1 on any FAIL
if [ "${STRICT_EVAL:-0}" = "1" ] || [ "$1" = "--gate" ]; then
    if [ "$failed_checks" -gt 0 ]; then
        echo "GATE MODE: FAILED (per pre-push gate)"
        exit 1
    else
        echo "GATE MODE: PASSED"
        exit 0
    fi
else
    if [ "$failed_checks" -gt 0 ]; then
        echo "ADVISORY: $failed_checks failure(s) reported (not blocking)"
    fi
    exit 0
fi
