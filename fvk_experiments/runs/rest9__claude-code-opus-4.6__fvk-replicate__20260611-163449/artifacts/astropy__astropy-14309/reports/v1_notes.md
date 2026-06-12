# v1 Notes

## Behavioral Change

The `is_fits()` function in `astropy/io/fits/connect.py` crashes with `IndexError: tuple index out of range` when called with an empty `args` tuple. This happens when `identify_format()` is called with a filepath that doesn't have a FITS extension and no positional arguments (e.g., `identify_format("write", Table, "bububu.ecsv", None, [], {})`).

The fix adds a `bool(args)` guard before accessing `args[0]`, so that `is_fits()` returns `False` when there are no positional arguments and the filepath doesn't match a FITS extension.

## Files Modified

- `astropy/io/fits/connect.py` (line 72): Changed `return isinstance(args[0], ...)` to `return bool(args) and isinstance(args[0], ...)`

## Public Tests Run

- `astropy/io/registry/tests/test_registries.py`: 221 passed, 14 skipped
- `astropy/io/fits/tests/test_connect.py`: 141 passed, 8 skipped, 5 xfailed

## Why This Matches the Public Issue

The issue reports that `identify_format("write", Table, "bububu.ecsv", None, [], {})` raises `IndexError` because `is_fits()` unconditionally accesses `args[0]` even when `args` is empty. The fix prevents the IndexError by short-circuit evaluating with `bool(args)`.
