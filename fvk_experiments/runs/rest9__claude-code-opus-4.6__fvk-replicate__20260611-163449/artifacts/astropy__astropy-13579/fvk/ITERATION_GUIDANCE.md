# ITERATION GUIDANCE — v1 → v2

## Assessment of v1

v1 scores 1/1 FAIL_TO_PASS and 40/40 PASS_TO_PASS (resolved: true).

The patch is:
1. **Correct** — fixes the root cause identified in the issue hint
2. **Minimal** — modifies only the necessary code path (the `else` branch)
3. **Consistent** — uses the same `_pixel_to_world_values_all` pattern as `dropped_world_dimensions`
4. **Non-regressing** — all 40 existing tests pass

## Recommendation for v2

**Keep v1 unchanged.** There is no evidence that any modification would improve the score, and any change risks breaking the 40 PASS_TO_PASS tests.

## Specific Guidance

### What to preserve in v2
- The `_pixel_to_world_values_all(*[0]*len(self._pixel_keep))` call for computing reference world values
- The `any(...)` guard that skips computation when no world dims are dropped
- The `world_ref[iworld]` fill for dropped world dimensions

### What NOT to change
- Do not refactor `world_to_pixel_values` beyond the minimal fix
- Do not add caching for `world_ref` (adds complexity, no functional benefit)
- Do not change `_pixel_to_world_values_all` or `pixel_to_world_values`
- Do not change `__init__`, `dropped_world_dimensions`, or any property
- Do not move the `world_ref` computation into `__init__` or a lazyproperty (changes initialization behavior)
- Do not rename variables or restructure the method

### Regression-heavy tasks: conservative strategy
With 40 regression tests and 1 bug test, the risk calculus strongly favors minimalism:
- A correct v1 with 0 regression failures should NOT be modified
- Any refactoring, cleanup, or "improvement" adds regression risk with no scoring benefit
- The only justified v2 change would be if v1 had a known correctness issue (it doesn't)

## Conclusion

v2 = v1. No changes warranted.
