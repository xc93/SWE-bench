# v2 Notes

## How v2 Differs from v1

v1 unconditionally changed the error message format to use Python list representation for both required and found columns. v2 makes this conditional:

- **Single required column** (`len(required_columns) == 1`): keeps the original format with single-quoted column names, e.g., `"expected 'time' as the first column but found 'flux'"`. This preserves backward compatibility with existing tests.

- **Multiple required columns** (`len(required_columns) > 1`): uses the new list format, e.g., `"expected ['time', 'flux'] as the first columns but found ['time']"`. This fixes the confusing message from the issue.

## Which Review Findings Caused the Change

1. **Finding**: v1 overgeneralized by changing the format for ALL cases, including single required column, breaking 8+ existing tests that assert exact error message equality (see `test_sampled.py:37-38`, `test_sampled.py:369-396`, `test_binned.py:30-31`).

2. **Finding**: The bug only manifests when there are multiple required columns — in the single-column case, `required_columns[0]` and `self.colnames[0]` always differ (otherwise the check wouldn't fail), so the old message is already clear.

## Regression Risks v2 Avoids

- Preserves exact error message format for single required column case → existing tests continue to pass
- Only modifies the `elif` branch of `_check_required_columns` → no side effects on other code paths
- No changes to the no-columns branch, decorator, or context manager → minimal blast radius
