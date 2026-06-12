# Iteration Guidance: v1 → v2

## Root Cause of v1 Failure

v1 unconditionally changed the error message format from single-quoted column names to Python list format. This broke existing tests that assert exact error message equality for the standard single-required-column case (`TimeSeries` with `['time']`, `BinnedTimeSeries` with `['time_bin_start', 'time_bin_size']`).

## v2 Strategy

Make the format **conditional** on the number of required columns:

### For `len(required_columns) == 1` (standard TimeSeries):
Keep the old format exactly:
```
expected 'time' as the first column but found 'flux'
```

### For `len(required_columns) > 1` (custom required columns):
Use list format:
```
expected ['time', 'flux'] as the first columns but found ['time']
```

## Exact Changes

In `astropy/timeseries/core.py`, `_check_required_columns` method:

### No-columns branch (line 73-75):
Add conditional: if single required column, use `"'{}'"` format with `required_columns[0]`; if multiple, use `"{}"` format with `required_columns`.

### Column-mismatch branch (line 79-81):
Add conditional: if single required column, use `"'{}'"` format with `required_columns[0]` and `self.colnames[0]`; if multiple, use `"{}"` format with `required_columns` and `self.colnames[:len(required_columns)]`.

## Regression Risks

- The single-column format must match EXACTLY what existing tests expect — no extra spaces, no list brackets
- The multi-column format should match what the issue proposes — Python list repr format
- No other behavioral changes should be made
