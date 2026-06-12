# v2 Notes

## How v2 differs from v1

v2 is identical to v1. The review found no bugs, missing edge cases, or overreach in the v1 patch.

## Review findings that informed this decision

- v1 correctly tracks brace depth to avoid splitting on commas inside `{}`
- Edge case handling is consistent with the old `_splitstrip` behavior
- The patch is minimal — only modifies `_regexp_csv_transfomer` and adds a helper
- v1 already scores 1/1 FAIL_TO_PASS and 18/18 PASS_TO_PASS

## Regression risks v2 avoids

By keeping v2 identical to v1, we avoid any risk of introducing new regressions. The review confirmed that the v1 patch does not modify any shared utilities or unrelated code paths.
