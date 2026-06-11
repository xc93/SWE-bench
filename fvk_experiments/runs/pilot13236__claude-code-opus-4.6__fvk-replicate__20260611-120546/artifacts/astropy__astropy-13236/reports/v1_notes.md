# v1 Notes

## Behavioral Change

Removes the auto-transform of structured `np.ndarray` into `NdarrayMixin` when adding to an Astropy `Table`. Structured arrays are now added directly as `Column` objects.

## Files Modified

- `astropy/table/table.py`: Removed 6 lines (the conditional block at lines 1242-1247 that converted structured ndarrays to NdarrayMixin view)

## Public Tests Run

- `repo/astropy/table/tests/test_table.py`: 367 passed, 1 failed (pre-existing, unrelated to patch)
- `repo/astropy/table/tests/test_mixin.py::test_ndarray_mixin`: Fails because it asserts old NdarrayMixin behavior (expected, since we changed the behavior)
- `repo/astropy/table/tests/test_mixin.py`: 163 passed, 1 failed (pre-existing skycoord issue), 6 skipped

## Why This Matches the Public Issue

The issue explicitly proposes removing the auto-transform clause. The discussion thread reached consensus that the change should be made directly (no FutureWarning needed), since:
1. Structured dtype `Column` now works properly after PR #12644
2. `NdarrayMixin` was a workaround that is no longer needed
3. All `NdarrayMixin` functionality is compatible with `Column` (both are ndarray subclasses)
