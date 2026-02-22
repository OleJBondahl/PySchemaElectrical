---
name: library-health-check
description: Use when the user asks to check library quality, run a health check, audit the codebase, or detect regressions - runs metrics, structural audits, rendering validation, and auto-fixes simple issues
---

# Library Health Check

## Overview

Comprehensive on-demand quality audit for PySchemaElectrical. Collects metrics, audits structure, validates rendering, auto-fixes simple issues, and writes a timestamped report.

**Core principle:** Detect regressions and inconsistencies before they compound. Fix what's safe, report what needs human judgment.

## When to Use

- User runs `/qc` or asks for a quality check / health check / audit
- Before a release or version bump
- After a large refactor or feature branch merge
- Periodically to catch drift

## Execution

Run all 5 phases in order. Use parallel subagents within each phase where indicated.

### Phase 1: Metrics Collection

Read baselines from `.claude/qc-baselines.json` in the project root. Then run these **in parallel** via Bash:

| Command | Extract | Compare to baseline |
|---------|---------|-------------------|
| `uv run pytest -q --tb=no 2>/dev/null \| tail -1` | Tests collected, passed, failed | `tests.collected`, `tests.passing` |
| `uv run pytest --cov=src --cov-report=term -q --tb=no 2>/dev/null \| grep "^TOTAL"` | Coverage % | `tests.coverage_pct` |
| `uv run ty check 2>&1 \| tail -1` | Diagnostic count | `ty.diagnostics` |
| `uv run ruff check 2>/dev/null \| tail -3` | Error count | `ruff.errors` |

**Flag regressions:** If any metric is worse than baseline (more failures, lower coverage, more diagnostics/errors), mark as REGRESSION in the report.

**Flag improvements:** If metrics improved, note it — the user may want to update baselines.

### Phase 2: Structural Audit

Run these checks **in parallel** using Explore subagents:

#### 2a. API Signature Consistency
Check if `src/pyschemaelectrical/std_circuits/` exists. If it does, verify all public functions:
- Accept `state: dict[str, Any]` as first parameter
- Accept `x: float, y: float` for positioning
- Return `BuildResult`
- Have `wire_labels` parameter

If `std_circuits/` does not exist, check whether CLAUDE.md still references it and flag the documentation as stale.

Also check `builder.py` for the `CircuitBuilder` class — verify `build()` returns `BuildResult`.

Flag deviations with file:line and the actual signature.

#### 2b. Symbol Port Validation
Search `src/pyschemaelectrical/symbols/` for all `*_symbol()` factory functions. For each:
- Check that `pins` parameter uses `tuple[str, ...] = ()` (not `None`)
- Flag inconsistencies (e.g., `pins: tuple[str, ...] | None = None`)

#### 2c. Public API Completeness
Compare exports in `src/pyschemaelectrical/__init__.py` against actual public symbols in each submodule. Flag:
- Symbols defined in modules but not exported
- Exports that no longer exist in source

#### 2d. Tech Debt Scan
Search entire `src/` for `TODO`, `FIXME`, `HACK`, `XXX`, `WORKAROUND` comments. List each with file:line and content.

### Phase 3: Rendering Validation

Run via Bash:

```bash
# Snapshot tests are run as part of the regular test suite (via snapshot_svg fixture).
# The pytest results from Phase 1 already cover them.
# Check if any snapshot-related failures appeared in the test output.

# Example scripts (should exit 0) — skip __init__.py and constants.py
for f in examples/example_*.py; do
  echo "--- $f ---"
  uv run python "$f" 2>&1 | tail -2
done
```

Flag any example script failures — these indicate broken API compatibility.

### Phase 4: Auto-Fix

Only fix issues that are **safe and mechanical**:

| Fix | How | Condition |
|-----|-----|-----------|
| Ruff auto-fixable | `uv run ruff check --fix` | Only if `--fix` flag applies (safe rules only) |
| Trailing whitespace | `uv run ruff format` | Only on files with issues |

**Do NOT auto-fix:**
- API signature changes (needs human review)
- Missing tests (needs human design)
- Type annotation additions (may change semantics)
- Anything in `__init__.py` import order (sensitive to circular imports)

After auto-fixing, re-run Phase 1 metrics to get "after" numbers.

### Phase 5: Report

#### Console Summary
Print a compact summary:

```
=== Library Health Check (YYYY-MM-DD) ===

METRICS:
  Tests:    940/953 passing (baseline: 940/953) ✓
  Coverage: 90% (baseline: 90%) ✓
  ty:       91 diagnostics (baseline: 91) ✓
  ruff:     33 errors (baseline: 33) ✓

STRUCTURAL:
  API consistency: 2 deviations found
  Symbol ports:    1 inconsistency
  Public API:      OK
  Tech debt:       12 markers found

RENDERING:
  Snapshots: OK
  Examples:  OK

AUTO-FIXED:
  1 ruff violation fixed

REGRESSIONS: None
```

#### Report File
Write detailed report to `.claude/qc-reports/YYYY-MM-DD.md` (create directory if needed). Include:
- Full metrics with before/after if auto-fixes were applied
- Each structural finding with file:line reference
- Tech debt marker list
- Rendering validation results
- List of auto-fixes applied
- Recommendations for manual fixes

#### Baseline Update Prompt
If metrics improved (e.g., fewer ty diagnostics), ask the user if they want to update `.claude/qc-baselines.json` with the new numbers.

## Common Issues This Catches

| Issue | Phase | Example |
|-------|-------|---------|
| Test count regression | 1 | New code broke existing tests |
| Coverage drop | 1 | New code without tests |
| Type check regression | 1 | New code introduced type errors |
| Lint regression | 1 | New code has style violations |
| Factory signature drift | 2a | New factory missing `wire_labels` param |
| Inconsistent pin defaults | 2b | `None` instead of `()` for pins |
| Missing export | 2c | New public class not in `__init__.py` |
| Accumulated tech debt | 2d | Growing TODO count |
| SVG rendering change | 3 | Unintentional visual changes |

## Red Flags

- Coverage dropped more than 2% → likely untested new code
- ty diagnostics increased by 5+ → likely new type issues introduced
- Snapshot tests failing → rendering changed, may be intentional or not
- Example scripts failing → API broke backward compatibility
