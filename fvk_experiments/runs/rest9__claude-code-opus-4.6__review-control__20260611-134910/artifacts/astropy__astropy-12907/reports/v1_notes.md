# v1 Notes

## Behavioral Change

v1 fixes the `separability_matrix` function so that nested `CompoundModel` instances (created with `&`) correctly preserve the separability information of their sub-expressions.

Before the fix, `separability_matrix(m.Pix2Sky_TAN() & cm)` where `cm = m.Linear1D(10) & m.Linear1D(5)` incorrectly returned a matrix showing the two Linear1D outputs as mutually dependent (all True in the bottom-right 2x2 block). After the fix, it correctly shows them as independent (diagonal True in the bottom-right 2x2 block).

## Files Modified

- `astropy/modeling/separable.py`: Line 245, changed `= 1` to `= right` in the `_cstack` function.

## Root Cause

In `_cstack`, when the `right` operand is an ndarray (i.e., an already-computed separability matrix from a recursive call on a nested compound model), the code was setting all values in the bottom-right block to `1` instead of copying the actual separability matrix values. This destroyed the separability information computed for the nested sub-expression.

## Public Tests Run

- `repo/astropy/modeling/tests/test_separable.py`: 11 tests, all passed both before and after the fix.
- Manual reproduction of the bug from the issue: confirmed the fix produces the expected output.

## Why v1 Matches the Public Issue

The issue reports that `separability_matrix(m.Pix2Sky_TAN() & cm)` produces incorrect results when `cm` is itself a compound model. The fix ensures that nested compound model separability information is preserved during the `&` (cstack) operation, which is exactly the scenario described in the issue.
