# Review Findings: v1 Patch for astropy__astropy-13033

## 1. Intended Public Behavior Change

When a `TimeSeries` (or subclass) with multiple required columns fails the required-column check, the error message should show the full list of required columns and the full list of found columns, instead of only the first element of each. This eliminates the confusing "expected 'time' ... but found 'time'" message.

## 2. Current Behavior in Implicated Code Paths

`BaseTimeSeries._check_required_columns()` in `core.py` has two error-raising branches:

- **Line 73-75 (no columns)**: Raises when `len(self.colnames) == 0`. Message: `"expected '{required_columns[0]}' as the first column{plural} but time series has no columns"`. Shows only the first required column name.

- **Line 79-81 (column mismatch)**: Raises when `self.colnames[:len(required_columns)] != required_columns`. Message: `"expected '{required_columns[0]}' ... but found '{self.colnames[0]}'"`. Shows only first required and first found column names.

For single required column (`TimeSeries: ['time']`), both messages are clear because required_columns[0] and self.colnames[0] always differ when the check fails.

For multiple required columns (`BinnedTimeSeries: ['time_bin_start', 'time_bin_size']`, or user-set), the messages can be misleading because `required_columns[0]` and `self.colnames[0]` can be the same value.

## 3. Public Issue Implications

The issue only asks for the error message to be less confusing when there are multiple required columns. It proposes list format: `required ['time', 'flux'] as the first columns but found ['time']`. It does NOT ask for changes to single-required-column behavior.

## 4-7. What Must Remain Unchanged

### For single required column cases:
- `TimeSeries` with `_required_columns = ['time']`: error messages must keep the old format `"expected 'time' as the first column but found 'X'"` because existing tests check exact message equality.
- Key tests:
  - `test_sampled.py:37-38`: checks `"expected 'time' as the first column but found 'flux'"`
  - `test_sampled.py:369-396`: six tests checking exact error messages for add_column, add_columns, keep_columns, remove_column, remove_columns, rename_column
  - `test_binned.py:30-31`: checks `"expected 'time_bin_start' as the first column but found 'flux'"`

### For the no-columns branch (line 73-75):
- No public tests check exact format for this branch, but it works correctly for the single-column case and doesn't trigger the confusing scenario (since "has no columns" is unambiguous).

### For related code paths:
- `_delay_required_column_checks()` context manager must not be altered
- `autocheck_required_columns` decorator logic must not be altered
- `_required_columns_relax` toggle logic must not be altered

## 8. What v1 Got Right

- Correctly identified the `elif` branch (line 79-81) as the location to fix
- Changed the format to show full lists of required and found columns
- Only modified one file (`core.py`)
- The new format matches the proposal in the issue

## 9. What v1 Is Missing or Overgeneralizing

**Critical bug**: v1 changes the message format for ALL cases, including single required column. This breaks existing tests that check exact error message equality:
- `test_sampled.py:37-38` expects `"expected 'time' as the first column but found 'flux'"` but now gets `"expected ['time'] as the first column but found ['flux']"`
- `test_sampled.py:369-396` — six tests with same problem
- `test_binned.py:30-31` expects `"expected 'time_bin_start' as the first column but found 'flux'"` but now gets `"expected ['time_bin_start'] as the first column but found ['flux']"`

This explains the v1 PASS_TO_PASS regression (18/20 instead of 20/20).

**Missing**: v1 may also need to fix the no-columns branch (line 73-75) for the multi-column case, though this is less certain.

## 10. Exact Minimal Changes Justified for v2

In the `elif` branch (line 79-81), use conditional formatting:
- When `len(required_columns) == 1`: keep old format with single-quoted column names
- When `len(required_columns) > 1`: use list format showing all required and found columns

Similarly for the no-columns branch (line 73-75), apply the same conditional:
- When `len(required_columns) == 1`: keep old format
- When `len(required_columns) > 1`: show full list

## 11. Forbidden Changes

- Do NOT change the format for single-required-column cases — this breaks at least 8 existing tests
- Do NOT modify `autocheck_required_columns`, `_delay_required_column_checks`, or `_required_columns_relax`
- Do NOT change which exceptions are raised or add new exception types
- Do NOT modify any other files
