# Formal Specification: Prefetch objects with slices

## Intent (from public issue)

`Prefetch()` objects should work with sliced querysets. When a user writes:

```python
Category.objects.prefetch_related(Prefetch(
    'post_set',
    queryset=Post.objects.all()[:3],
    to_attr='example_posts',
))
```

Each `Category` instance should have `example_posts` set to a list of at most 3 related `Post` objects.

## Current behavior (base commit)

Raises `TypeError: Cannot filter a query once a slice has been taken.` because `get_prefetch_queryset()` calls `.filter()` on the sliced queryset, and `_filter_or_exclude` rejects filtered-after-sliced querysets.

## Specified behavior

### Postcondition (new behavior)

1. `Prefetch(lookup, queryset=qs[:N], to_attr=attr)` must not raise during construction or prefetch execution.
2. After prefetching, each parent instance's `to_attr` attribute must be a list of at most N related objects (the first N from the queryset's ordering).
3. The per-instance limiting (the "slice") must be applied independently per parent instance — N objects per parent, not N total.
4. The slice must respect the queryset's ordering (`.order_by()` if present).
5. `Prefetch` with sliced queryset and without `to_attr` should also work — the cached queryset's `_result_cache` should contain at most N related objects per parent.

### Preconditions (unchanged behavior)

6. Unsliced `Prefetch` must behave identically to the base commit.
7. All existing `Prefetch` validation must be preserved:
   - `RawQuerySet` raises `ValueError`
   - Non-`ModelIterable` querysets raise `ValueError`
8. All other queryset operations on sliced querysets must continue to raise (`.filter()`, `.exclude()`, etc. on a sliced queryset outside of Prefetch context).
9. The `_apply_rel_filters` code path (used for non-`to_attr` prefetch) must handle sliced querysets correctly.
10. Pickling (`__getstate__`) of Prefetch objects with slices must work.

## Implementation approach (v1)

v1 extracts the slice at `Prefetch.__init__` time:
- Stores slice parameters in `self._slice` as a `slice(low, high)` object
- Clones the queryset and clears its limits so it can be filtered by `get_prefetch_queryset`
- In `prefetch_one_level`, applies the slice per-instance after grouping results by parent

This approach:
- Centralizes slice handling in the `Prefetch` class
- Avoids modifying any `get_prefetch_queryset` implementations (FK, reverse FK, M2M, GenericRelation)
- Avoids modifying `_filter_or_exclude` or `_apply_rel_filters`
- The SQL query fetches all matching related objects (no SQL LIMIT), and the slice is applied per-instance in Python
