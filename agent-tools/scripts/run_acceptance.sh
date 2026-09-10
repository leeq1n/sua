#!/usr/bin/env bash
# run_acceptance.sh — single entrypoint for regression evidence.
#
# Per docs/ACCEPTANCE_PROTOCOL.md, this script is the SINGLE
# ENTRYPOINT for bounded regression checks. It runs:
# 1. p30_acceptance.py (non-terminal authority boundary)
# 2. validate_links.py (markdown cross-refs)
# 3. validate_structure.py (critical paths)
# 4. token_budget.py (file size budgets)
# 5. self_health_check.py (SUA self-audit)
# 6. cross_repo_audit.py (cross-repo audit)
# 7. pytest (test suite)
#
# Two modes:
#   Default (advisory): Runs all, prints regression evidence, exits 0
#   --gate (STRICT_EVAL=1): Blocks on technical regression failure only
#
# Per M-n 29 regression evidence + P30 + docs/ACCEPTANCE_PROTOCOL.md.

set +e  # Don't exit on error — we want to run all checks

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS="$REPO_ROOT/agent-tools/scripts"

if [ "$1" = "--terminal-acceptance" ]; then
    echo "ACCEPTANCE BLOCKED / INDEPENDENT AUDIT REQUIRED"
    echo "run_acceptance.sh emits regression evidence only."
    exit 2
fi

echo "================================================================"
echo "REGRESSION EVIDENCE — run_acceptance.sh"
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

# 1. P30 shared boundary (must remain non-terminal)
if [ -f "$SCRIPTS/p30_acceptance.py" ]; then
    run_check "p30_regression_boundary" python "$SCRIPTS/p30_acceptance.py" \
        --regression-evidence --role "${SUA_ROLE:-UNSPECIFIED}" \
        --regression-status "REGRESSION PASS"
else
    echo "--- p30_regression_boundary (BLOCKED: not found) ---"
    total_checks=$((total_checks + 1))
    failed_checks=$((failed_checks + 1))
fi

# 2. validate_links.py
if [ -f "$SCRIPTS/validate_links.py" ]; then
    run_check "validate_links" python "$SCRIPTS/validate_links.py"
else
    echo "--- validate_links (SKIPPED: not found) ---"
    echo
fi

# 3. validate_structure.py
if [ -f "$SCRIPTS/validate_structure.py" ]; then
    run_check "validate_structure" python "$SCRIPTS/validate_structure.py"
else
    echo "--- validate_structure (SKIPPED: not found) ---"
    echo
fi

# 4. token_budget.py
if [ -f "$SCRIPTS/token_budget.py" ]; then
    run_check "token_budget" python "$SCRIPTS/token_budget.py"
else
    echo "--- token_budget (SKIPPED: not found) ---"
    echo
fi

# 5. self_health_check.py (advisory regression evidence)
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

# 6. cross_repo_audit.py (advisory regression evidence)
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

# 7. pytest
if [ -d "$REPO_ROOT/tests" ]; then
    run_check "pytest" python -m pytest "$REPO_ROOT/tests" -q
else
    echo "--- pytest (SKIPPED: no tests dir) ---"
    echo
fi

# Summary
echo "================================================================"
echo "REGRESSION EVIDENCE SUMMARY"
echo "================================================================"
echo "Total checks: $total_checks"
echo "Passed: $passed_checks"
echo "Failed: $failed_checks"
echo

# Gate mode: exit 1 on technical regression failure; it never accepts the artifact.
if [ "${STRICT_EVAL:-0}" = "1" ] || [ "$1" = "--gate" ]; then
    if [ "$failed_checks" -gt 0 ]; then
        echo "REGRESSION GATE: INCOMPLETE (per pre-push gate)"
        exit 1
    else
        echo "REGRESSION GATE: COMPLETE (no artifact acceptance issued)"
        exit 0
    fi
else
    if [ "$failed_checks" -gt 0 ]; then
        echo "ADVISORY: $failed_checks failure(s) reported (not blocking)"
    fi
    exit 0
fi
