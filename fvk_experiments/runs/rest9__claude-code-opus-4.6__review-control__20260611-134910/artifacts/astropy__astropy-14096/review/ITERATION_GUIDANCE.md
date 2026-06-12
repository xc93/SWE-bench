# Iteration Guidance for v2

## Summary

v1 is correct, minimal, and passes all tests (1/1 FAIL_TO_PASS, 426/426 PASS_TO_PASS). The review found no bugs, no edge case failures, and no regressions.

## Recommendation

**Keep v2 identical to v1.** No behavioral changes are justified.

The only optional refinement is a minor comment wording clarification. This carries no functional risk.

## What NOT to change

1. Do not restructure the fix. The MRO-based descriptor check is the correct, targeted approach.
2. Do not add try/except blocks. The current flow (re-invoke descriptor, let error propagate) is the correct pattern.
3. Do not modify any code outside the `__getattr__` method.
4. Do not change the order of existing checks.
5. Do not refactor surrounding code.

## Risk Assessment

v1 risk level: **very low**. The change adds a fallback check at the end of an error path. It can only activate when:
- Normal attribute lookup failed
- All SkyCoord-specific lookups failed
- The attribute IS a descriptor on the class

This is exactly the bug case described in the issue. All other code paths are untouched.
