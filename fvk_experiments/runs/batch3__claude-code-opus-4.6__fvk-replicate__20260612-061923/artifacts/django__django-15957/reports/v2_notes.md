# v2 Notes

## How v2 differs from v1

v2 is identical to v1. The FVK analysis confirmed that v1 is minimal, correct, and achieves a perfect score. No changes are justified.

## Which FVK findings caused the change

No findings required changes. All 8 findings in `fvk/FINDINGS.md` confirmed v1's approach is correct:
- Finding 1: Slice extraction/application is sound
- Finding 2: Queryset clone preserves all attributes
- Finding 3: Pickling works correctly
- Finding 4: Non-leaf levels handled correctly
- Finding 5: Prefetch reuse is safe
- Finding 6: `_apply_rel_filters` path is unaffected
- Finding 7: No regression risk for unsliced querysets
- Finding 8: API surface changes are minimal and follow conventions

## Regression risks v2 is designed to avoid

v2 (= v1) avoids all regression risks identified in `fvk/PROOF_OBLIGATIONS.md`:
- No modifications to `_filter_or_exclude` (O12)
- No modifications to `get_prefetch_queryset` implementations (O11)
- No behavioral changes for unsliced querysets (O5)
- Preserved validation (O6)
- Preserved pickling (O8)
- Preserved equality/hashing (O10)
