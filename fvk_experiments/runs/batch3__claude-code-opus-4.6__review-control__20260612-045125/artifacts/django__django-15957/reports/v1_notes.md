# v1 Notes

## Behavioral Change

v1 allows `Prefetch()` objects to work with sliced querysets. Previously, passing a sliced queryset like `Post.objects.all()[:3]` would raise `TypeError: Cannot filter a query once a slice has been taken.` because `get_prefetch_queryset()` calls `.filter()` on the custom queryset.

The fix extracts the slice parameters from the queryset in `prefetch_one_level()`, clears the limits so filtering can proceed, then applies the slice per-instance when distributing results.

## Files Modified

- `django/db/models/query.py` — `prefetch_one_level()` function only

## Changes Made

1. Before calling `get_prefetch_queryset()`, detect if the custom queryset is sliced. If so, save `low_mark`/`high_mark`, clone the queryset, and clear the limits.
2. After fetching all results and distributing per-instance, apply the saved slice to each instance's result list.
3. In the non-`to_attr` path, pass the unsliced queryset to `_apply_rel_filters()` instead of the original sliced queryset (which would also fail on `.filter()`).

## Public Tests Run

- `prefetch_related` test suite: 109 tests, all pass
- `generic_relations` test suite: 70 tests, all pass  
- `queries` test suite: 461 tests, all pass (11 skipped, 2 expected failures)

## Why This Matches the Public Issue

The issue reports that `Prefetch('post_set', queryset=Post.objects.all()[:3], to_attr='example_posts')` raises an `AssertionError` (TypeError). The fix allows sliced querysets by extracting the slice before filtering and applying it per-instance in memory, which is exactly the approach suggested in the issue discussion: "extract it from the provided queryset to make it filterable again and apply it when in-memory joining."
