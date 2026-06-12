# v2 Notes

## How v2 Differs from v1

v2 is identical to v1. The review found no bugs, missed edge cases, or regressions in v1.

## Review Findings That Informed This Decision

- Finding 8: v1 correctly handles all `get_prefetch_queryset` implementations via centralized fix
- Finding 9a: The `_apply_rel_filters` change uses the same object reference in non-sliced case (no behavioral change)
- Finding 9b-9d: No action needed — by design or correct as implemented
- Finding 10: No changes justified beyond v1
- Finding 11: Multiple forbidden changes identified — none were present in v1

## Regression Risks v2 Avoids

By keeping v2 identical to v1, we avoid:
- Any risk from unnecessary code changes
- Subtle behavioral differences from making `_apply_rel_filters` conditional
- Any new edge cases from adding validation in `Prefetch.__init__`
