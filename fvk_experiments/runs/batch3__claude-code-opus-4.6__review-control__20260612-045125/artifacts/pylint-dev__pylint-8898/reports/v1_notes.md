# v1 Notes

## Behavioral change

v1 modifies `_regexp_csv_transfomer` in `pylint/config/argument.py` to not split on commas inside curly braces when parsing comma-separated regex patterns. This fixes the `bad-names-rgxs` (and `good-names-rgxs`) options so that regex quantifiers like `{1,3}` are preserved.

## Files modified

- `pylint/config/argument.py`: Added `_regexp_csv_split` helper function; changed `_regexp_csv_transfomer` to use it instead of `_csv_transformer`.

## Approach

Added a new `_regexp_csv_split` function that:
- Tracks brace depth while iterating through the string
- Only splits on commas when brace depth is 0
- Strips whitespace from each part and discards empty parts

## Public tests run

- `tests/config/test_config.py`: 15 passed, 1 failed
  - `test_csv_regex_error` fails because it expected the old broken behavior where `(foo{1,3})` would be split on the comma and produce an invalid regex error. The fix correctly makes this a valid single regex.

## Why this matches the issue

The issue reports that `bad-names-rgxs = "(foo{1,3})"` causes pylint to crash because the comma in the regex quantifier is treated as a CSV separator, splitting the regex into invalid fragments. v1 fixes this by using a smarter splitting function that respects curly braces.
