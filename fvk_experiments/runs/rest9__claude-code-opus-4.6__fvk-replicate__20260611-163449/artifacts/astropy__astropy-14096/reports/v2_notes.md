# v2 Notes

## How v2 Differs From v1

v2 is identical to v1. The FVK analysis found no issues with v1 and recommended no changes.

## FVK Findings That Informed This Decision

- Finding 2: Fix is correctly placed after all frame lookups — no ordering issues
- Finding 3: `hasattr(desc, '__get__')` is appropriately general — no need to narrow
- Finding 5: No recursion risk — no need for defensive guards
- Finding 6: Initialization safety preserved — no need for additional checks
- ITERATION_GUIDANCE.md: "Keep v1 unchanged" — all proof obligations satisfied

## Regression Risks v2 Avoids

By keeping v1 unchanged, v2 avoids:
- Narrowing the descriptor check (risking missed descriptor types)
- Moving the check's position (risking frame lookup interference)
- Adding unnecessary try/except (masking real errors)
- Touching `__setattr__`/`__delattr__` (out of scope)
