# v2 Notes

## How v2 Differs from v1

v2 is identical to v1. The FVK analysis confirmed that the one-token fix (`= 1` → `= right` on line 245 of `astropy/modeling/separable.py`) is correct, minimal, and complete.

## FVK Findings That Informed This Decision

1. **Finding 1**: The asymmetric `left`/`right` treatment is the sole root cause. The fix makes them symmetric.
2. **Finding 2**: The bug only manifests with nested CompoundModels as the right operand of `&`. The fix correctly targets only this code path.
3. **Finding 3**: The change has no side effects on other operators or code paths.

## Regression Risks v2 Avoids

By keeping the patch identical to v1 (which already passes 13/13 regression tests), v2 avoids:
- Over-generalizing the fix to touch unrelated functions
- Refactoring that could break existing behavior
- Adding unnecessary validation or comments
