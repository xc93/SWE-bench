# v1 Notes

## What behavior v1 changes

When a `TimeSeries` (or subclass) has multiple required columns and the required-column check fails, the error message now shows all required column names and all found first-column names, instead of only the first one.

Before (misleading): `expected 'time' as the first columns but found 'time'`
After: `expected '['time', 'flux']' as the first columns but found '['time']'`

When there is only a single required column (the default `time`-only case), the existing message format is preserved unchanged.

## Files modified

- `repo/astropy/timeseries/core.py` — lines 73-81 in `_check_required_columns()`

## Public tests run

- `repo/astropy/timeseries/tests/` — 82 passed, 1 failed (pre-existing leap-second staleness in `test_binned.py::test_initialization_time_bin_size`), 3 skipped.

## Why v1 matches the public issue

The issue asks for the error message to include all required columns and all found columns when a TimeSeries with additional required columns fails validation. v1 does exactly that, while preserving the existing format for the default single-required-column case.
