# Iteration Guidance: v1 → v2

## Summary

v1 is correct, minimal, and passes all tests (1/1 FAIL_TO_PASS, 141/141 PASS_TO_PASS). The review found no bugs, edge case failures, incompleteness, or overreach in the patch.

## Recommended v2 action

**Keep v2 identical to v1.** There is no review finding that justifies a change.

## What exact minimal changes are justified for v2

None beyond v1. The fix is:
- Guard `args[0]` with `if args:`
- Return `False` when args is empty

This is the standard, minimal, correct fix for an IndexError on an empty sequence.

## What changes are forbidden because they risk regressions

1. Do NOT fix `votable/connect.py:42` — same pattern but different subsystem, not reported in this issue
2. Do NOT restructure the `is_fits` function's control flow (e.g., early returns, reordering branches)
3. Do NOT change the `identify_format` dispatcher in `base.py`
4. Do NOT add type checking or validation to the identifier registration system
5. Do NOT change the function signature of `is_fits`

## Regression checklist

- [x] `is_fits` with fileobj containing FITS signature → still returns True
- [x] `is_fits` with filepath ending in .fits → still returns True
- [x] `is_fits` with args=(HDUList(),) → still returns True (guarded access works)
- [x] `is_fits` with non-FITS filepath and empty args → now returns False (was IndexError)
- [x] All 221 registry tests pass
- [x] All 141 FITS connect tests pass
