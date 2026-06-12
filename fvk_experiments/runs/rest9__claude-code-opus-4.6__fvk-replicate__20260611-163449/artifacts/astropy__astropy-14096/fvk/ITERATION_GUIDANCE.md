# ITERATION GUIDANCE — v1 → v2

## v1 Assessment

v1 scored 1/1 FAIL_TO_PASS and 426/426 PASS_TO_PASS (resolved: true).

The fix is minimal: 6 lines of new code added to `__getattr__` in `sky_coordinate.py`, placed between the last frame lookup and the final `raise AttributeError`. No other files modified.

## FVK Analysis Summary

All proof obligations are satisfied by v1:
- **O1** (bug fix): The descriptor re-invocation propagates the original `AttributeError`
- **O2–O7** (frame lookups): Preserved because the fix runs after all frame lookups
- **O8–O9** (missing attributes): Preserved because non-descriptor attributes fall through to the original raise
- **O10–O11** (initialization): Safe because the descriptor check terminates
- **O12–O13** (__setattr__/__delattr__): Not modified
- **O14–O18** (subclass/edge cases): Handled correctly

## Recommendation for v2

**Keep v1 unchanged.** The fix is:
1. Minimal (6 lines added)
2. Correctly placed (after all frame lookups, before the generic error)
3. Appropriately general (`hasattr(desc, '__get__')` covers all descriptor types)
4. Safe (no recursion risk, no initialization issues)
5. Fully passing (1/1 FAIL_TO_PASS, 426/426 PASS_TO_PASS)

No changes are justified for v2. Any modification risks introducing regressions without improving the already-perfect score.

## Risks of over-iteration

- Adding `isinstance(desc, property)` instead of `hasattr(desc, '__get__')` would be less general and might miss custom descriptors
- Moving the check inside the `if "_sky_coord_frame"` block would fail for descriptors accessed during initialization
- Adding try/except around the re-invocation would mask errors
- Modifying `__setattr__` or `__delattr__` is out of scope and risky
