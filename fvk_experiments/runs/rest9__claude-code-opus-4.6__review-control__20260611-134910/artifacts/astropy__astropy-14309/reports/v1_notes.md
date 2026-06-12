# v1 Notes

## Behavioral change

v1 fixes an `IndexError: tuple index out of range` in `astropy/io/fits/connect.py:is_fits()`.

When `is_fits()` is called with no positional args (e.g., `args=()`) and `filepath` is a non-FITS string (no `.fits`/`.fit`/`.fts` extension), the function falls through to line 72 which unconditionally accesses `args[0]`. With an empty `args` tuple, this raises `IndexError`.

The fix guards the `args[0]` access with `if args:`, returning `False` when no args are provided.

## Files modified

- `astropy/io/fits/connect.py` — line 72: added guard for empty `args`

## Public tests run

1. `astropy/io/registry/tests/test_registries.py` — 221 passed, 14 skipped
2. `astropy/io/fits/tests/test_connect.py` — 141 passed, 8 skipped, 5 xfailed

All existing tests continue to pass.

## Why v1 matches the public issue

The issue reports that `identify_format("write", Table, "bububu.ecsv", None, [], {})` raises `IndexError` because `is_fits` tries `args[0]` when args is empty. The fix prevents this by checking `args` is non-empty before indexing, exactly addressing the reported crash.
