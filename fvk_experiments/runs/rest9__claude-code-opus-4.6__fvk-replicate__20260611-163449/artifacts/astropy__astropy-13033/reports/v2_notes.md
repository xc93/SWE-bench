# v2 Notes

## How v2 differs from v1

v2 makes two changes from v1:

1. **Fixed format string**: v1 used `"expected '{}'"` which wraps lists in extra quotes (`'['time', 'flux']'`). v2 conditionally omits the quotes when showing lists: `"'{}'.format(x)"` for single columns, `str(x)` for lists. This produces `['time', 'flux']` without extra outer quotes.

2. **Left "no columns" branch unchanged**: v1 modified both the elif/mismatch branch AND the "no columns" branch. v2 only modifies the elif/mismatch branch (lines 79-81). The issue specifically cites this branch, and leaving the "no columns" branch alone avoids unnecessary risk.

## Which FVK findings caused the change

- **Finding 1 (extra quotes)**: Fixed the format string to avoid `'[]'` wrapping.
- **Finding 2 (unnecessary "no columns" change)**: Removed the change to the "no columns" branch.
- **PO-1 (single-column preservation)**: Verified single-column format is character-for-character identical.

## Regression risks v2 avoids

- Single-column error messages are exactly preserved (PO-1, PO-5).
- "No columns" branch is untouched (PO-3).
- BinnedTimeSeries relaxed mode uses single-column format (PO-4).
- Substring checks (`'TimeSeries object is invalid'`) still match (PO-6).

## Files modified

- `repo/astropy/timeseries/core.py` — lines 79-86 in `_check_required_columns()`

## Baseline PASS_TO_PASS note

Baseline (empty patch) gets 19/20 PASS_TO_PASS due to a pre-existing leap-second environment issue (`IERSStaleWarning: leap-second file is expired`). v2 does not introduce any additional regressions.
