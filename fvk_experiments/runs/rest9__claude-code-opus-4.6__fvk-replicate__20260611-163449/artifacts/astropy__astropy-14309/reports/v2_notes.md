# v2 Notes

## How v2 differs from v1

v2 is identical to v1. The FVK analysis confirmed that v1's fix is correct, minimal, and complete. No additional changes are warranted.

## FVK findings that influenced the decision

1. **SPEC.md**: The formal specification of `is_fits` confirms that v1 satisfies all post-conditions and preserves all pre-existing behavior.

2. **FINDINGS.md**: 
   - Finding 1 (the bug) is fully addressed by v1.
   - Finding 2 (votable pattern) is explicitly out of scope — fixing it would risk regressions.
   - Finding 3 confirms v1 is consistent with the registry API contract.
   - Finding 4 confirms no behavioral change for valid inputs.

3. **PROOF_OBLIGATIONS.md**: All 10 proof obligations are satisfied by v1.

4. **ITERATION_GUIDANCE.md**: Explicitly recommends keeping v2 identical to v1, and lists 5 forbidden changes that would risk regressions.

## Regression risks v2 avoids

By keeping v2 identical to v1:
- No risk from fixing out-of-scope votable code
- No risk from unnecessary control flow restructuring
- No risk from modifying the registry base
- No risk from adding try/except blocks that mask errors
