# v1 Notes

## Behavioral Change

v1 wraps the input conversion loop in `Quantity.__array_ufunc__()` with a `try/except` for `(TypeError, ValueError)`. When a converter fails because the input value is not a recognized numeric type (e.g., a duck-type array), it now returns `NotImplemented` instead of raising `ValueError`. This allows Python's operator dispatch to fall through to the other operand's reflected operator.

## Files Modified

- `astropy/units/quantity.py`: Lines 667-670, wrapped the converter call in try/except

## Public Tests Run

- `astropy/units/tests/test_quantity.py`: 93 passed, 1 xfailed
- `astropy/units/tests/test_quantity_ufuncs.py`: 201 passed, 4 skipped
- Manual test with the DuckArray example from the issue: all 3 cases pass

## Why v1 Matches the Public Issue

The issue states that `Quantity.__array_ufunc__()` should return `NotImplemented` instead of raising `ValueError` when inputs are incompatible duck types. The fix catches `ValueError` (from `_condition_arg` when the value can't be converted to a numeric array) and `TypeError` (for other type mismatches) in the input conversion loop and returns `NotImplemented`, allowing Python's operator dispatch to try reflected operators.
