# Review Findings: v1 Patch for django__django-15957

## 1. Intended Public Behavior Change

Allow `Prefetch()` objects to accept sliced querysets (e.g., `Post.objects.all()[:3]`). Previously, this raised `TypeError: Cannot filter a query once a slice has been taken.` The slice should be applied per-instance in memory.

## 2. Current Behavior in Implicated Code Paths

- `prefetch_one_level()` calls `prefetcher.get_prefetch_queryset(instances, custom_qs)`
- All `get_prefetch_queryset` implementations (reverse FK, M2M, GenericRelation, forward FK, reverse O2O) call `.filter()` on the custom queryset
- `.filter()` on a sliced queryset raises `TypeError` because `_filter_or_exclude` checks `self.query.is_sliced`
- Additionally, `_apply_rel_filters()` (line 2523 in the non-`as_attr` path) also calls `.filter()`, triggering the same error

## 3. Django Version Implications

The fix adds a new capability (sliced Prefetch querysets) that was previously unsupported. This is a feature addition, not a behavior change to existing code. Backward-compatible with Django 4.2.

## 4. Behavior That Must Remain Unchanged — Public APIs

- Non-sliced `Prefetch` querysets must work identically
- `Prefetch` without custom querysets must work identically
- String-based `prefetch_related()` must work identically
- `Prefetch` with `to_attr` (non-sliced) must work identically
- `Prefetch` with `values()`/`values_list()`/`raw()` must still raise `ValueError`

## 5. Behavior That Must Remain Unchanged — Related Code Paths

- `get_prefetch_queryset()` on all descriptor types must return identical results for non-sliced querysets
- `_apply_rel_filters()` must produce identical querysets for non-sliced cases
- `prefetch_related_objects()` loop logic must not change
- Nested prefetches (multi-level lookups) must not change

## 6. Behavior That Must Remain Unchanged — Out-of-Scope Inputs

- Empty querysets passed to `Prefetch` must work
- Querysets with ordering but no slice must work
- Querysets with annotations/aggregations must work
- `select_related` must not be affected

## 7. Behavior That Must Remain Unchanged — Edge Cases

- Prefetch reuse (same `Prefetch` object in multiple querysets) must work
- Serialization via `__getstate__` must work
- `_prefetch_done = True` must still prevent re-fetching
- `_result_cache` assignment must still work correctly

## 8. What v1 Got Right

- **Correct location**: The fix is in `prefetch_one_level()`, which is the single bottleneck for all prefetch operations. This means ALL `get_prefetch_queryset` implementations (reverse FK, M2M, forward FK, reverse O2O, GenericRelation) automatically benefit.
- **Correct slice extraction**: Uses `query.low_mark` and `query.high_mark` to capture the slice, then `_chain()` + `query.clear_limits()` to create an unsliced clone.
- **Per-instance application**: Applies `vals[offset:stop]` per instance, which is the correct semantic (e.g., "3 posts per category", not "3 posts total").
- **Preserved ordering**: Only removes LIMIT, not ORDER BY, so per-instance slicing respects the queryset's ordering.
- **Fixed `_apply_rel_filters`**: Changed to pass `db_queryset` (unsliced) instead of `lookup.queryset` (sliced), preventing the same `.filter()` error.
- **No API changes**: No changes to `get_prefetch_queryset` return signature or `Prefetch` class interface.
- **109/109 existing tests pass**.

## 9. What v1 May Be Missing or Overgeneralizing

### 9a. `_apply_rel_filters` change in non-sliced case (LOW RISK)

v1 always passes `db_queryset` to `_apply_rel_filters`, even when the queryset is not sliced. Analysis shows this is safe: in the non-sliced case, `db_queryset` is the same object reference as `lookup.queryset` (both point to `lookup.get_current_queryset(level)`). However, this is a change to a code path that runs for ALL non-`as_attr` prefetches, not just sliced ones. The risk is extremely low (they're the same object), but it's a broader change than strictly necessary.

### 9b. No `to_attr` enforcement for sliced querysets (LOW RISK)

Without `to_attr`, sliced results are stored in a queryset's `_result_cache`. The queryset object itself doesn't know about the slice, so if a user later inspects the queryset's query (e.g., `str(qs.query)`), it won't reflect the slice. However, since `_result_cache` is set and `_prefetch_done = True`, normal iteration and `.count()` work correctly.

### 9c. Performance: all results fetched then sliced in memory (BY DESIGN)

The fix fetches all related objects and applies the slice in memory. For large datasets with small slices, this is wasteful. However, this is the approach explicitly discussed in the Django ticket and is the only feasible approach without per-group LIMIT SQL support.

### 9d. Slice applied after grouping by instance (CORRECT)

The per-instance results in `rel_obj_cache` preserve the ordering from the SQL query. The slice `vals[offset:stop]` correctly takes the first N items per instance according to the queryset's ordering. This is correct.

## 10. Exact Minimal Changes Justified for v2

v1 is already correct and complete. The only potential improvement is cosmetic/safety:

1. **Consider**: Make `_apply_rel_filters` change conditional on actual slicing. While not strictly necessary (same object in non-sliced case), it reduces the apparent surface area of the change.

2. **Consider**: No other changes are justified. The fix is minimal, correct, and handles all edge cases properly.

## 11. Changes Forbidden Because They Risk Regressions

- Do NOT modify `Prefetch.__init__` to strip slices early — this changes the queryset stored on the object, affecting `__getstate__`, reuse, and the `get_current_queryset()` return value.
- Do NOT modify any `get_prefetch_queryset` implementations — the fix should be centralized in `prefetch_one_level`.
- Do NOT add new return values to `get_prefetch_queryset` — this is a public API.
- Do NOT modify `_filter_or_exclude` to allow filtering sliced querysets — that's a fundamental invariant of Django's ORM.
- Do NOT add SQL-level per-instance limits — this requires subquery support and is far out of scope.
