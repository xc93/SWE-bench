# PROOF OBLIGATIONS

## PO-1: Single-column format preservation

For `len(required_columns) == 1`, the error message must be character-for-character identical to the base commit:
- `"expected 'X' as the first column but found 'Y'"`
- `"expected 'X' as the first column but time series has no columns"`

Tested by: `test_required_columns` in `test_sampled.py` (exact string checks), `test_empty_initialization_invalid` in `test_binned.py` (exact string check).

## PO-2: Multi-column format correctness

For `len(required_columns) > 1`, the error message must show ALL required columns and ALL found first columns:
- `"expected ['time', 'flux'] as the first columns but found ['time']"` (no extra quotes around list)

## PO-3: "No columns" branch unchanged

The "no columns" branch (lines 71-75) must NOT be modified. It is not cited in the issue, and changing it risks breaking tests for BinnedTimeSeries.

## PO-4: Relaxed mode behavior

When `_required_columns_relax=True`, `required_columns` is truncated to `len(self.colnames)`. If this produces `len(required_columns) == 1`, the single-column format must be used.

## PO-5: BinnedTimeSeries relaxed-mode test

`test_empty_initialization_invalid` creates a BinnedTimeSeries in relaxed mode. When `ts['flux'] = [1,2,3]` triggers the check, `required_columns = ['time_bin_start']` (truncated). Must produce: `"expected 'time_bin_start' as the first column but found 'flux'"`.

## PO-6: Substring tests

`test_required_after_stacking` only checks `'TimeSeries object is invalid' in exc.value.args[0]`. Must remain true for both TimeSeries and BinnedTimeSeries.
