# v1 Notes

## Behavioral Change

v1 modifies `Quantity.__array_ufunc__()` to return `NotImplemented` instead of raising `ValueError` (or `TypeError`) when an input cannot be converted to a numeric array by the unit converter. This allows Python's operator dispatch mechanism to fall back to the other operand's reflected method (e.g., `__radd__`).

## Files Modified

- `astropy/units/quantity.py`: Wrapped the converter application loop (line 670) in a `try/except (ValueError, TypeError)` block that returns `NotImplemented` on failure.

## Root Cause

In `__array_ufunc__`, when processing inputs, the code calls `converter(input_)` which eventually invokes `_condition_arg()` in `core.py`. For duck types that are not `np.ndarray`, `float`, `int`, `complex`, or `np.void`, and whose `np.array()` representation has a non-numeric dtype, `_condition_arg` raises `ValueError`. This prevents Python from trying the reflected operator on the other operand.

## Public Tests Run

- `astropy/units/tests/test_quantity.py`: 93 passed, 1 xfailed
- `astropy/units/tests/test_quantity_ufuncs.py`: 201 passed, 4 skipped
- Manual reproduction of all three cases from the issue: all pass

## Why v1 Matches the Public Issue

The issue requests that `Quantity.__array_ufunc__()` return `NotImplemented` instead of raising `ValueError` when inputs are incompatible. The hint suggests a `try/except` approach to avoid slowing the common case. v1 implements exactly this: a try/except around the converter application that returns `NotImplemented` on `ValueError` or `TypeError`.
