# Findings Report: v1 patch for django__django-15957

## Finding 1 — v1 correctly extracts and applies slices

**Status: CORRECT**

The v1 approach of extracting the slice at `Prefetch.__init__` time and applying it per-instance in `prefetch_one_level` is sound:
- The cloned queryset has limits cleared, so `get_prefetch_queryset` can filter it.
- The `_slice` is stored as a Python `slice` object for clean application.
- Per-instance slicing happens after grouping by parent, which is the semantically correct behavior.

## Finding 2 — Slice extraction preserves queryset attributes

**Status: CORRECT**

`_chain()` creates a proper clone (via `_clone()` → `query.chain()`), preserving:
- Ordering (`order_by`)
- Filters (existing `.filter()` calls)
- Select-related lookups
- Prefetch-related lookups
- Database routing (`using`)
- Annotations

Only the limits (low_mark, high_mark) are cleared, which is the intended behavior.

## Finding 3 — `__getstate__` handles `_slice` correctly

**Status: CORRECT**

`__getstate__` uses `self.__dict__.copy()`, so `_slice` is automatically included in the pickled state. The queryset stored in the state dict is already unsliced (limits were cleared in `__init__`), so pickling works.

## Finding 4 — `get_current_queryset_slice` correctly handles non-leaf levels

**Status: CORRECT**

`get_current_queryset_slice(level)` only returns the slice when at the matching level (same check as `get_current_queryset`). For intermediate levels in nested prefetch lookups, it returns `None`, so no spurious slicing is applied.

## Finding 5 — Edge case: Prefetch reuse with sliced querysets

**Status: POTENTIAL CONCERN**

When a `Prefetch` object is reused (as mentioned in the `copy.copy` handling in `prefetch_one_level`), the `_slice` attribute is preserved and the queryset is already unsliced. This means:
- First use: works correctly (queryset unsliced, slice applied per-instance)
- Second use: works correctly (same state as first use)

The `copy.copy` of additional_lookups won't affect the `_slice` because additional lookups come from the queryset's own `_prefetch_related_lookups`, not from the Prefetch object's slice.

## Finding 6 — The `_apply_rel_filters` path is unaffected

**Status: CORRECT**

In `prefetch_one_level`, when `as_attr` is False (no `to_attr`), the code:
```python
qs = manager._apply_rel_filters(lookup.queryset)
```
receives the already-unsliced queryset (`lookup.queryset` had its limits cleared in `__init__`). So `_apply_rel_filters` can call `.filter()` without error. The `qs._result_cache = vals` is then set with the already-sliced `vals`.

## Finding 7 — No regression risk for unsliced querysets

**Status: CORRECT**

When the queryset is not sliced:
- `self._slice = None` (default)
- `queryset.query.is_sliced` is False, so the `if` block is skipped
- `self.queryset = queryset` (unchanged)
- In `prefetch_one_level`, `queryset_slice` is `None`, so no slicing is applied
- All paths are identical to the base commit

## Finding 8 — No unnecessary API surface changes

**Status: ACCEPTABLE**

v1 adds one new public method `get_current_queryset_slice(level)` and one attribute `_slice`. The method follows the naming pattern of `get_current_queryset(level)` and `get_current_to_attr(level)`. The `_slice` attribute uses the underscore-prefix convention for internal state.
