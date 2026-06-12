# v2 Notes

## How v2 Differs from v1

v2 is identical to v1. No changes were made.

## FVK Findings That Informed This Decision

1. **FINDINGS.md Finding 1** confirmed the root cause and that v1 correctly fixes it.
2. **FINDINGS.md Finding 2** confirmed v1 uses the same pattern as existing code (`dropped_world_dimensions`).
3. **FINDINGS.md Findings 3-4** identified minor style/performance observations but recommended no action.
4. **PROOF_OBLIGATIONS.md** demonstrated that v1 satisfies all 14 proof obligations (1 bug-fix + 13 non-regression).
5. **ITERATION_GUIDANCE.md** recommended keeping v1 unchanged given the 40:1 regression-to-bug ratio.

## Regression Risks v2 Avoids

By making no changes beyond v1, v2 avoids:
- Any risk of breaking the 40 PASS_TO_PASS tests
- Introducing new code paths that could have subtle issues
- Changing initialization or caching behavior
- Refactoring that could alter edge case handling
