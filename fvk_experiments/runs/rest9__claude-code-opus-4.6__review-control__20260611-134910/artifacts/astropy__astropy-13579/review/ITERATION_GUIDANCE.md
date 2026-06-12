# Iteration Guidance: v1 → v2

## Assessment

v1 is correct and passes all evaluator tests (1/1 FAIL_TO_PASS, 40/40 PASS_TO_PASS). The core fix — replacing `1.` with the world coordinate at the slice reference position — is the right approach.

## Recommendation: Keep v1 as-is

The v1 patch is minimal, correct, and consistent with existing patterns in the codebase. The only potential improvement is a minor performance optimization (guarding the `world_ref` computation), which:
- Does not change correctness
- Adds minimal code
- Carries near-zero regression risk

**However**, since v1 already achieves a perfect score, any change to v2 carries risk with no correctness upside. The conservative choice is to keep v2 identical to v1.

## If v2 must differ from v1

The safest change would be to guard the `world_ref` computation:

```python
if len(self._world_keep) < self._wcs.world_n_dim:
    world_ref = self._pixel_to_world_values_all(*[0]*len(self._pixel_keep))
```

And in the else branch, keep the same `world_ref[iworld]` usage. This avoids computing the reference when there are no dropped world dimensions (the common case in existing tests).

## What NOT to do

- Do not add broader refactoring
- Do not change any other method
- Do not change the `__init__` or property methods
- Do not attempt to cache the reference values
- Do not change the test infrastructure
