# ITERATION GUIDANCE: v1 → v2

## v1 Assessment

v1 is correct and minimal. It changes exactly one token (`1` → `right`) on line 245 of `astropy/modeling/separable.py`, fixing the asymmetric treatment of right ndarray operands in `_cstack`.

## v1 Score

- FAIL_TO_PASS: 2/2
- PASS_TO_PASS: 13/13
- Resolved: true

## Recommendation for v2

**v2 should be identical to v1.** The fix is:
1. Minimal — one token change
2. Correct — fixes the exact bug described in the issue
3. Complete — passes all 15 evaluator tests (2 bug + 13 regression)
4. Safe — no collateral changes to unrelated code paths

## Risks of Over-Generalization

Do NOT:
- Add input validation or type checking to `_cstack`
- Refactor the function to use a different matrix construction approach
- Add comments explaining the bug fix
- Change the left-operand branch (it's already correct)
- Touch any other function in `separable.py`
- Add new test files or modify existing test files

Any of these could introduce regressions in the PASS_TO_PASS group without improving the FAIL_TO_PASS score.

## Key Insight

This bug was a simple asymmetric assignment error — the left branch used `= left` while the right branch used `= 1`. The fix makes them symmetric. There is no deeper architectural issue requiring broader changes.
