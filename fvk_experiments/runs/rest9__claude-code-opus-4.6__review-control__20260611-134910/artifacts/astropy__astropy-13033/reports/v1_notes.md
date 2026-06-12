# v1 Notes

## Behavioral Change

v1 changes the error message in `BaseTimeSeries._check_required_columns()` (line 79-81 of `core.py`) so that when the required column check fails, the full list of required columns and the full list of found columns are shown, instead of only the first element of each.

Before: `TimeSeries object is invalid - expected 'time' as the first columns but found 'time'`
After: `TimeSeries object is invalid - expected ['time', 'flux'] as the first columns but found ['time']`

## Files Modified

- `astropy/timeseries/core.py`: Changed the error message format in the `elif` branch of `_check_required_columns` (line 79-81) to use `required_columns` (full list) instead of `required_columns[0]`, and `self.colnames[:len(required_columns)]` instead of `self.colnames[0]`.

## Public Tests Run

- All 22 tests in `test_common.py` pass (excluding `test_join` which has a pre-existing IERS leap-second stale data failure unrelated to the patch).
- Manually verified the reproduction case from the issue produces the improved error message.

## Why v1 Matches the Issue

The issue reports that the error message is misleading when a TimeSeries has multiple required columns and one is removed. The message said "expected 'time' ... but found 'time'" which is confusing. v1 fixes this by showing the full lists, matching the proposal in the issue discussion.
