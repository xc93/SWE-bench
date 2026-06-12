# v2 Notes

## How v2 Differs from v1

v2 is identical to v1. The review found no bugs, edge case failures, incompleteness, or overreach in the v1 patch.

## Review Findings That Caused the (Non-)Change

The review confirmed:
1. The single-line fix is the complete and correct root cause fix.
2. No other functions in `separable.py` share this bug pattern.
3. The fix cannot cause regressions because for all previously-working inputs, the replaced scalar `1` and the actual matrix values were identical (all-ones).
4. The change is precisely scoped to the reported issue.

## Regression Risks v2 Is Designed to Avoid

By keeping v2 identical to v1, no new regression risk is introduced. The review explicitly verified:
- All 11 existing `test_separable.py` tests pass.
- `_cdot`, `_arith_oper`, `_coord_matrix`, and `_separable` are unmodified and unaffected.
- Edge cases including deep nesting, left/right nesting, and mixed operators all produce correct results.
