# v1 Notes

## Behavioral Change

The `_regexp_csv_transfomer` function in `pylint/config/argument.py` previously used `_csv_transformer` which naively splits on all commas. This breaks regex patterns containing commas in quantifiers like `{1,3}`.

v1 replaces the naive comma split with a new `_regexp_csv_split` function that tracks brace depth and does not split on commas inside `{...}` blocks.

## Files Modified

- `pylint/config/argument.py`: Modified `_regexp_csv_transfomer` to use new `_regexp_csv_split` instead of `_csv_transformer`. Added `_regexp_csv_split` function.

## Public Tests Run

- `repo/tests/config/test_config.py`: 15 passed, 1 failed
  - The failing test `test_csv_regex_error` expects the old broken behavior where `(foo{1,3})` is mangled by comma splitting. Our fix makes this a valid regex.

## Why v1 Matches the Public Issue

The issue reports that `bad-names-rgxs` mangles regular expressions containing commas (e.g., `(foo{1,3})`). The root cause is `_regexp_csv_transfomer` splitting on all commas. v1 fixes this by only splitting on commas that are outside curly braces.
