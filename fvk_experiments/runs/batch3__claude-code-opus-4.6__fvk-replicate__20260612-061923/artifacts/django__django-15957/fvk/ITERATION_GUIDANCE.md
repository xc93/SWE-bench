# Iteration Guidance: v1 → v2

## v1 Assessment

v1 achieves a perfect score (4/4 FAIL_TO_PASS, 89/89 PASS_TO_PASS). The approach is sound and minimal.

## What v1 got right

1. **Centralized slice handling in `Prefetch.__init__`** — extracting the slice at construction time avoids modifying any `get_prefetch_queryset` implementations, `_filter_or_exclude`, or `_apply_rel_filters`.
2. **Per-instance slicing** — applying the slice after grouping results by parent instance gives the semantically correct behavior (N items per parent, not N total).
3. **Clean queryset cloning** — using `_chain()` + `clear_limits()` properly preserves all queryset attributes except the slice.
4. **No behavioral changes for unsliced querysets** — the `if queryset.query.is_sliced` guard ensures zero impact on existing code paths.

## What v1 could improve (minor)

1. **Accessing `queryset.query` in `Prefetch.__init__`** — the `query` property triggers deferred filter application. This should be harmless for freshly-constructed querysets (no deferred filters exist at Prefetch construction time), but it is technically a side effect. Consider accessing `queryset._query` directly if this is a concern.
   - **Risk level: Negligible.** User-provided querysets should not have `_deferred_filter` set.
   - **Decision: Do not change.** The `query` property is the public API and is the correct access pattern.

2. **`get_current_queryset_slice` method** — adds a small amount of API surface. Could instead access `lookup._slice` directly in `prefetch_one_level` with a `getattr(lookup, '_slice', None)` check.
   - **Risk level: None.** The method follows existing naming conventions.
   - **Decision: Keep as-is.** The method provides a clean, level-aware interface matching `get_current_queryset`.

## Forbidden changes for v2

1. **Do not modify `_filter_or_exclude`** — changing the sliced queryset validation would affect all queryset operations, not just Prefetch.
2. **Do not modify `get_prefetch_queryset` implementations** — there are 4+ implementations across related_descriptors.py and contenttypes/fields.py. Modifying each one is error-prone and the centralized approach is better.
3. **Do not add SQL-level LIMIT** — applying LIMIT at the SQL level would give N total results, not N per parent. The per-instance Python slicing is semantically correct.
4. **Do not remove Prefetch validation** — the existing validation for RawQuerySet and non-ModelIterable must be preserved.
5. **Do not change `__eq__` or `__hash__`** — Prefetch equality is based on `prefetch_to`, which should not include slice info.

## Recommendation for v2

**v2 should be identical to v1.** The v1 patch is minimal, correct, and achieves a perfect score. Any changes risk introducing regressions without adding value.

If any change is made, it should be limited to:
- Adding a comment explaining why the slice is extracted at init time (optional, follows existing code style)
- No other changes are justified by the findings
