# Proof Obligations: django__django-15957

## Bug-revealing obligations (FAIL_TO_PASS: 4 tests)

### O1: Basic sliced prefetch with `to_attr`
- `Prefetch('related_set', queryset=Model.objects.all()[:N], to_attr='attr')` must not raise
- Each parent's `attr` must be a list of at most N related objects

### O2: Sliced prefetch preserves ordering
- `Prefetch('related_set', queryset=Model.objects.order_by('-field')[:N], to_attr='attr')` must return the first N objects per the specified ordering

### O3: Sliced prefetch without `to_attr`
- `Prefetch('related_set', queryset=Model.objects.all()[:N])` must not raise
- The cached queryset must have at most N objects per parent in its `_result_cache`

### O4: Sliced prefetch with filter
- `Prefetch('related_set', queryset=Model.objects.filter(...)[:N], to_attr='attr')` must not raise
- The filter must be applied before the slice (SQL-level filter, Python-level slice)

## Non-regression obligations (PASS_TO_PASS: 89 tests)

### O5: Unsliced Prefetch behavior unchanged
- All existing `Prefetch` usage without slices must produce identical results
- No behavioral change when `queryset.query.is_sliced` is False

### O6: Prefetch validation unchanged
- `Prefetch(queryset=RawQuerySet(...))` must still raise `ValueError`
- `Prefetch(queryset=qs.values())` must still raise `ValueError`
- `Prefetch(queryset=qs.values_list())` must still raise `ValueError`

### O7: `_apply_rel_filters` path unchanged for unsliced
- The non-`to_attr` code path that uses `manager._apply_rel_filters(lookup.queryset)` must work identically for unsliced querysets

### O8: Prefetch pickling unchanged
- `__getstate__` must work for both sliced and unsliced Prefetch objects

### O9: Nested prefetch unchanged
- Prefetch lookups with multiple levels (e.g., `author__books`) must work
- `get_current_queryset_slice(level)` must return `None` for non-leaf levels

### O10: Prefetch equality/hashing unchanged
- `__eq__` and `__hash__` must not be affected by `_slice`

### O11: Related manager behavior unchanged
- Forward FK, reverse FK, M2M, and GenericRelation prefetch must all work
- The `get_prefetch_queryset` implementations must receive unsliced querysets

### O12: QuerySet slice behavior unchanged outside Prefetch
- `_filter_or_exclude` must still raise `TypeError` for sliced querysets when called directly (not through Prefetch)
- No changes to `QuerySet.filter()`, `QuerySet.exclude()`, etc.
