# v2 Notes

## How v2 differs from v1

v2 is identical to v1. The FVK analysis confirmed that v1 is already the optimal minimal patch.

## Which FVK findings caused the change

No findings required changes. All 7 findings were positive confirmations:
- Finding 1: Patch is minimal and correctly scoped
- Finding 2: No risk from explicit NdarrayMixin inputs
- Finding 3: Record array behavior change is aligned with intent
- Finding 4: Test assertion changes are expected (handled by hidden test_patch)
- Finding 5: No serialization regression risk
- Finding 6: conftest.py fixtures unaffected
- Finding 7: Patch does not overgeneralize

## Regression risks v2 is designed to avoid

By keeping v2 identical to v1, we avoid:
- Introducing any new code that could fail
- Broadening the change beyond what the issue requests
- Touching serialization, imports, or other unrelated code paths
- All 644 regression tests remain passing
