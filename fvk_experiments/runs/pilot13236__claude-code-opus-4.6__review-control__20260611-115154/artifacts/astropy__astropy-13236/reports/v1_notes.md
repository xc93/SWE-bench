# v1 Notes

## Behavioral Change

Removed the auto-transformation of structured `np.ndarray` objects into `NdarrayMixin` when added to an Astropy `Table`. After this patch, structured arrays are stored as regular `Column` objects instead.

## Files Modified

- `astropy/table/table.py`: Removed 6 lines (the conditional block at lines 1242-1247) that checked for structured ndarrays and converted them to `NdarrayMixin` via `.view()`.

## Public Tests Run

- `astropy/table/tests/test_table.py`: 458 passed, 19 skipped, 1 xfailed (1 pre-existing failure excluded: `test_values_equal_part1`).
- `astropy/table/tests/test_mixin.py`: 185 passed, 6 skipped (1 pre-existing failure excluded: `test_skycoord_representation`; 1 expected-to-change test excluded: `test_ndarray_mixin`).
- Manual verification: structured arrays added to Table now produce `Column` objects with correct data access.

## Why v1 Matches the Issue

The issue requests removing the auto-transform of structured `np.array` into `NdarrayMixin`. The discussion consensus (including from @mhvk) is to "just change it — part of the improvement brought by structured columns." The patch removes exactly the code block cited in the issue, with no other changes.
