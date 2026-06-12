# Iteration Guidance: v1 -> v2

## Summary

v1 is correct. It passes all 9 regression tests and the 1 bug-revealing test (resolved: true). The review found no bugs, no missing edge cases, and no overreach.

## Recommendation

**Do not change the patch.** v2 should be identical to v1.

## Rationale

1. The patch is minimal (4 lines in 1 file).
2. Default behavior is preserved by construction (header_rows=None defaults to ["name"], which produces identical indices to the original hardcoded values).
3. The pattern follows existing codebase conventions (FixedWidthTwoLine does the same kind of data.start_line override).
4. All 10 tests pass (9 PASS_TO_PASS + 1 FAIL_TO_PASS).

## Risk assessment for any v2 changes

Any modification to v1 risks introducing regressions:
- Changing how `data.start_line` is computed could break reading.
- Changing how the position line index is computed in `write()` could break writing.
- Adding unnecessary code (e.g., validation, edge-case handling) could introduce new failure modes.
- Changing files beyond `rst.py` is unjustified by the issue scope.

## Conclusion

The safest v2 is no change from v1.
