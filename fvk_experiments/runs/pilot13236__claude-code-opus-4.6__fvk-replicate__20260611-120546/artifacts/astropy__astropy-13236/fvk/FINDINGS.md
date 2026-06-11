# FINDINGS — astropy__astropy-13236

## Finding 1 — v1 patch is minimal and correctly scoped

**Classification**: Positive confirmation

The v1 patch removes exactly the 6-line block that auto-transforms structured ndarrays into NdarrayMixin. After removal, structured ndarrays flow through the normal `_convert_data_to_col` path and reach the `else: col_cls = self.ColumnClass` branch, which constructs a `Column`. This is exactly the behavior the issue requests.

**Evidence**: After the patch, `Table([structured_array], names=['a'])` produces a `Column` rather than `NdarrayMixin`, and all data values are preserved.

## Finding 2 — No risk from explicit NdarrayMixin inputs

**Classification**: Positive confirmation

The removed code only triggers when `not isinstance(data, Column) and not data_is_mixin`. An explicitly constructed `NdarrayMixin` passes `self._is_mixin_for_table(data)` (since `NdarrayMixin` is an ndarray subclass with an `info` attribute), so `data_is_mixin` would be True, and the removed block would never have applied. Therefore, explicit NdarrayMixin columns are unaffected.

## Finding 3 — Record arrays (np.recarray) behavior changes

**Classification**: Expected behavior change (aligned with intent)

`np.rec.fromrecords(...)` produces an `np.recarray`, which is an ndarray subclass with structured dtype. Before the patch, this would be auto-converted to NdarrayMixin. After the patch, it flows to the `else` branch and becomes a `Column`. This is the correct behavior per the issue discussion.

## Finding 4 — Existing test `test_ndarray_mixin` asserts old behavior

**Classification**: Expected test change needed

The existing test at `test_mixin.py:700` asserts `isinstance(t['a'], NdarrayMixin)` etc. for structured arrays added to a table. These assertions will fail after the patch. The hidden test_patch is expected to update these assertions.

## Finding 5 — No serialization/I/O regression risk

**Classification**: Positive confirmation

The `serialize.py` reference to `NdarrayMixin` (line 38) is in a lookup table for I/O handling. This handles existing NdarrayMixin columns that might be loaded from files. Since `Column` already supports structured dtypes (per PR #12644 mentioned in the issue), new columns will serialize correctly as `Column` objects. No change to serialization code is needed.

## Finding 6 — conftest.py test fixtures explicitly construct NdarrayMixin

**Classification**: No regression risk

The test fixtures in `conftest.py:151-153` explicitly construct `NdarrayMixin` via `.view(NdarrayMixin)`. These will continue to work because the auto-transform was not the only path to create NdarrayMixin columns — explicit construction still works.

## Finding 7 — v1 does not overgeneralize

**Classification**: Positive confirmation

The patch only removes the auto-transform. It does not:
- Remove the NdarrayMixin class itself
- Remove NdarrayMixin from imports
- Change the serialize.py handler
- Change how other mixin columns are handled
- Add any new code

This is the most conservative possible change for the requested behavior.

## Proof-derived findings from /verify

No additional findings. The change is a pure deletion of a conditional branch. The resulting code path (structured ndarray -> Column via ColumnClass) is already well-exercised for non-structured ndarrays. The only new element is that structured dtype ndarrays now take this same path, which is explicitly what the issue requests and what PR #12644 enabled.
