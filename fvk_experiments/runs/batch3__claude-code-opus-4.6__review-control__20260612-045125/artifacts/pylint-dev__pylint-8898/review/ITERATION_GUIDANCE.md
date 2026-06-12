# Iteration Guidance: v1 -> v2

## Summary

v1 scored 1/1 FAIL_TO_PASS and 18/18 PASS_TO_PASS (fully resolved). The review found no bugs, no missing edge cases, and no overreach in the v1 patch.

## Recommendation

**Do not change v1.** The patch is minimal, correct, and passes all evaluator tests. Any modification risks introducing regressions without fixing additional bugs.

## If v2 must differ from v1

If there is a compelling reason to iterate (which the review does not find), the only safe improvements would be:

1. **Style**: Minor code style changes within the same function (not recommended — risk > reward)
2. **Documentation**: Improving the docstring of `_regexp_csv_split` (not recommended — the docstring is adequate)

## Things to NOT do in v2

- Do not extend the fix to `_regexp_paths_csv_transfomer` — different type, not mentioned in the issue
- Do not modify `_csv_transformer` or `_check_csv` — shared by many non-regex options
- Do not add escape handling for `\{` — the current behavior is correct and handles this case well enough
- Do not modify any test files — the hidden test_patch handles test changes
- Do not add deprecation warnings — the issue doesn't ask for this
- Do not refactor the brace tracking logic — it's clean and correct as-is

## Regression checklist

- [x] Simple comma-separated regexes still split correctly
- [x] Empty input returns empty list
- [x] Whitespace is stripped
- [x] Empty entries are discarded
- [x] Unmatched braces don't crash
- [x] Multiple quantifiers in separate patterns work (e.g., `a{1,3},b{2,5}`)
- [x] The fix applies to all `regexp_csv` options, not just `bad-names-rgxs`
