# PROOF OBLIGATIONS — pylint-dev__pylint-8898

## Bug-fix obligation (FAIL_TO_PASS)

1. **O-BUG-1**: `_regexp_csv_transfomer("(foo{1,3})")` must return `[re.compile("(foo{1,3})")]` without raising an error.
   - Status: SATISFIED by v1.

## Non-regression obligations (PASS_TO_PASS, 18 tests)

### Core behavior preservation

2. **O-REG-1**: Simple comma-separated regexes without braces must split correctly.
   - `"a,b,c"` -> `["a", "b", "c"]`
   - Status: SATISFIED — `brace_depth == 0` for all chars, so commas are separators as before.

3. **O-REG-2**: Single regex without commas must be returned as-is.
   - `"foo"` -> `["foo"]`
   - Status: SATISFIED.

4. **O-REG-3**: Empty/whitespace-only input must return empty list.
   - `""` -> `[]`
   - Status: SATISFIED.

5. **O-REG-4**: Whitespace around patterns must be stripped.
   - `" a , b "` -> `["a", "b"]`
   - Status: SATISFIED — uses `.strip()`.

6. **O-REG-5**: Invalid regex patterns must still raise `argparse.ArgumentTypeError`.
   - `"[invalid"` -> error
   - Status: SATISFIED — `_regex_transformer` is unchanged.

### No side effects on other transformers

7. **O-REG-6**: `_csv_transformer` is unchanged.
   - Status: SATISFIED — not modified.

8. **O-REG-7**: `_regexp_paths_csv_transfomer` is unchanged.
   - Status: SATISFIED — not modified, still uses `_csv_transformer`.

9. **O-REG-8**: `_regex_transformer` is unchanged.
   - Status: SATISFIED — not modified.

10. **O-REG-9**: `_check_csv` and `_splitstrip` are unchanged.
    - Status: SATISFIED — not modified.

### Option-specific preservation

11. **O-REG-10**: `ignore-patterns` option must continue to work.
    - Status: SATISFIED — uses `regexp_csv`, now with brace-aware split.

12. **O-REG-11**: `good-names-rgxs` option must continue to work.
    - Status: SATISFIED.

13. **O-REG-12**: `bad-names-rgxs` option must continue to work.
    - Status: SATISFIED.

14. **O-REG-13**: `exclude-too-few-public-methods` option must continue to work.
    - Status: SATISFIED.

### Existing test compatibility

15. **O-REG-14**: The existing test `test_csv_regex_error` changes behavior (was testing broken behavior).
    - The hidden test_patch is expected to update or replace this test.
    - Status: ACCEPTABLE — the test tested the broken behavior that this fix corrects.

## Forbidden changes

- **F-1**: Do NOT modify `_csv_transformer` or its dependencies.
- **F-2**: Do NOT modify `_regexp_paths_csv_transfomer`.
- **F-3**: Do NOT modify other files beyond `pylint/config/argument.py`.
- **F-4**: Do NOT add deprecation warnings unless the issue explicitly calls for them.
- **F-5**: Do NOT change the function signature of `_regexp_csv_transfomer`.
