# v1 Notes

## Behavioral Change

v1 fixes the `_cstack` function in `astropy/modeling/separable.py` so that when the right operand of a `&` (concatenation) operation is an already-computed separability matrix (ndarray), the actual matrix values are preserved instead of being replaced with all 1s.

## Files Modified

- `astropy/modeling/separable.py`: line 245, changed `= 1` to `= right`

## Root Cause

In `_cstack`, when the right operand is a Model, `_coord_matrix` is called to compute the correct separability matrix. But when the right operand is already an ndarray (from a nested compound model that was already recursively processed), the code at line 245 set the submatrix to `1` instead of copying the actual values from `right`. This destroyed the separability information — all right-side outputs appeared coupled to all right-side inputs.

The left operand case (line 240) correctly used `= left`, making this an asymmetric bug affecting only the right operand in nested concatenation.

## Public Tests Run

- `repo/astropy/modeling/tests/test_separable.py`: 11/11 passed before and after the fix

## Why This Matches the Issue

The issue reports that `separability_matrix(m.Pix2Sky_TAN() & cm)` incorrectly shows coupled outputs for the nested compound model `cm`, while the flat equivalent `m.Pix2Sky_TAN() & m.Linear1D(10) & m.Linear1D(5)` is correct. After v1, both produce identical diagonal results for the Linear1D components.
