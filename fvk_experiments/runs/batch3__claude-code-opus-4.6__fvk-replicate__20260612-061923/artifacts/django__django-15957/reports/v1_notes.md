# v1 Notes

## Behavioral Change
v1 allows `Prefetch()` objects to work with sliced querysets. Previously, using a sliced queryset like `Post.objects.all()[:3]` in a `Prefetch()` raised `TypeError: Cannot filter a query once a slice has been taken.`

The fix handles slicing at the `Prefetch` class level: when a sliced queryset is provided, the slice parameters are extracted and stored separately, and the queryset is cloned with limits cleared. During prefetch execution, the stored slice is applied per-instance after grouping results by parent object.

## Files Modified
- `django/db/models/query.py`

## Changes

### 1. `Prefetch.__init__` (class initialization)
- Added `self._slice = None` attribute
- When `queryset` is sliced: extract slice info as `slice(low_mark, high_mark)`, store in `self._slice`, clone the queryset and clear its limits so it can be filtered later by `get_prefetch_queryset`

### 2. `Prefetch.get_current_queryset_slice(level)` (new method)
- Returns the stored `_slice` for the current level, or `None` if not at the matching level

### 3. `prefetch_one_level` (result assignment)
- Retrieves `queryset_slice` via `lookup.get_current_queryset_slice(level)`
- Applies the slice per-instance to `vals` before assignment

## Public Tests Run
- `prefetch_related` full test suite: 109 tests, all passed
- Manual tests: sliced prefetch with `to_attr`, without `to_attr`, with ordering, with filter+slice, with offset slice — all passed

## Why v1 Matches the Issue
The issue reports that `Prefetch('post_set', queryset=Post.objects.all()[:3], to_attr='example_posts')` raises an error. v1 fixes this by extracting the slice at Prefetch construction time so the queryset can be filtered internally, then applying the slice per-instance when assigning results.
