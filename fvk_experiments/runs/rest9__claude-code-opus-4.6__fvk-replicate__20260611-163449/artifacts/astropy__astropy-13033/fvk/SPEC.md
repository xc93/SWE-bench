# SPEC: TimeSeries required column check error messages

## Intended behavior change

When `_check_required_columns()` raises a `ValueError` because the first N columns don't match the required columns, the error message should show ALL required column names and ALL found first-column names, not just the first one of each.

## Current behavior (base commit)

`_check_required_columns()` in `astropy/timeseries/core.py` has two error branches:

1. **No columns branch** (line 71-75): fires when `_required_columns_relax=False` and `len(self.colnames)==0`.
   - Message: `"expected '{required_columns[0]}' as the first column{plural} but time series has no columns"`

2. **Mismatch branch** (line 77-81): fires when `self.colnames[:len(required_columns)] != required_columns`.
   - Message: `"expected '{required_columns[0]}' as the first column{plural} but found '{self.colnames[0]}'"`

Both show only the first required column and the first found column, regardless of how many required columns exist.

## Postcondition (what v2 must achieve)

For the mismatch branch (line 77-81):
- When `len(required_columns) == 1`: preserve existing format exactly (e.g., `"expected 'time' as the first column but found 'flux'"`)
- When `len(required_columns) > 1`: show all required columns and all found first columns (e.g., `"expected ['time', 'flux'] as the first columns but found ['time']"`)

## Non-regression obligations

1. Single-column error messages must be character-for-character identical to the original.
2. The "no columns" branch (line 71-75) should NOT be changed unless required — it's not the focus of the issue and changing it risks breaking existing tests.
3. The `_required_columns_relax` logic must not change.
4. `BinnedTimeSeries` (which has 2 required columns by default) error messages in relaxed mode must be preserved.
