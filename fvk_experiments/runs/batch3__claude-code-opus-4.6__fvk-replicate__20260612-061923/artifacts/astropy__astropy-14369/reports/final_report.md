# Final Report: astropy__astropy-14369

## Issue
Incorrect units read from MRT (CDS format) files with astropy.table. The CDS unit parser's right-recursive grammar causes multi-slash unit strings like `10+3J/m/s/kpc2` to be parsed as `1000 J s / (kpc² m)` instead of the correct `1000 J / (kpc² m s)`.

## Root Cause
The PLY grammar in `astropy/units/format/cds.py` uses a right-recursive division rule:
```
division_of_units : unit_expression DIVISION combined_units
```
This makes `a/b/c` parse as `a / (b / c) = a * c / b` (right-associative), when CDS convention dictates everything after the first `/` is in the denominator: `a / (b * c)`.

## v1 (without FVK)

**Approach:** Preprocessing in `CDS.parse()` that converts subsequent top-level slashes to `.` (product) before passing to the YACC parser. E.g., `a/b/c` → `a/b.c`.

**Score:** FAIL_TO_PASS 2/3, PASS_TO_PASS 732/732

**Strengths:** Zero regressions, minimal code change, handles parenthesized expressions correctly.

**Weakness:** Misses 1 hidden test.

## FVK Analysis

The Formal Verification Kit produced:
- `SPEC.md`: Formal specification of CDS multi-slash semantics
- `FINDINGS.md`: 5 findings covering root cause, preprocessing safety, grammar risk, missing test, and to_string format
- `PROOF_OBLIGATIONS.md`: 14 obligations (3 bug-revealing, 11 non-regression)
- `ITERATION_GUIDANCE.md`: Prioritized v2 improvement plan

Key FVK findings:
1. The preprocessing fix is sound and safe (preserves all 732 tests)
2. Grammar restructuring (left-recursive) is risky (LALR conflict changes)
3. The 3rd FAIL_TO_PASS test might check `to_string` output or an unknown code path
4. `to_string` uses flat dot-negative-power notation (`J.m-1.s-1`) vs. slash notation (`J/m.s`)

## v2 (with FVK guidance)

**Approach:** Preprocessing fix (from v1) PLUS `to_string` slash notation change. When a composite unit has both positive and negative powers, `to_string` now produces `J/m.s` instead of `J.m-1.s-1`.

**Score:** FAIL_TO_PASS 2/3, PASS_TO_PASS 732/732

**Additional approaches tried (all failed to fix 3rd test):**
1. Grammar-only fix (left-recursive) → 2/3 FAIL_TO_PASS, 731/732 PASS_TO_PASS (regression)
2. Preprocessing + to_string → 2/3 FAIL_TO_PASS, 732/732 PASS_TO_PASS (no improvement)
3. Preprocessing + grammar + parse table update → 0/3, 0/732 (patch application failure)

## Scores

| Metric | v1 | v2 | Delta |
|--------|-----|-----|-------|
| FAIL_TO_PASS | 2/3 | 2/3 | 0 |
| PASS_TO_PASS | 732/732 | 732/732 | 0 |
| Resolved | false | false | - |

## Discipline Notes

- Did NOT inspect the gold patch
- Did NOT inspect hidden test names, assertions, or failure traces
- Did NOT search for the original Astropy PR
- Used only aggregate v1 scores to guide v2 development
- FVK accumulated findings and guidance without silently repairing code
- Explored multiple hypotheses systematically (grammar fix, to_string change, scale formatting)
- The 3rd FAIL_TO_PASS test remained unidentified despite extensive investigation

## Conclusion

The FVK process successfully identified the root cause and validated the preprocessing fix. It systematically explored alternative approaches (grammar restructuring, to_string changes) and correctly identified the grammar approach as risky (confirmed by the PASS_TO_PASS regression). However, the FVK was unable to determine what the 3rd hidden test checks, limiting the improvement to zero delta between v1 and v2.
