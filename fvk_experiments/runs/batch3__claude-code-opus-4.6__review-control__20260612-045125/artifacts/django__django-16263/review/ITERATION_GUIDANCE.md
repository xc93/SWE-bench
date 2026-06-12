# Iteration Guidance: v1 → v2

## Primary Change

Add `_prune_unused_joins()` call to `Query.exists()` after `clear_select_clause()` strips annotations. This completes the optimization for the `exists()` path mentioned in the issue.

## Where to change

File: `django/db/models/sql/query.py`, method `exists()` (around line 654)

After `q.clear_select_clause()`, add `q._prune_unused_joins()`. This prunes JOINs that were only needed by annotations that are now stripped.

## Why this change

1. The public issue explicitly says "Same can be done for exists()"
2. `clear_select_clause()` already strips annotations from the SELECT but leaves their JOINs
3. `_prune_unused_joins()` recalculates alias refcounts and sets unused JOINs to refcount 0
4. The compiler's `get_from_clause()` already skips JOINs with refcount 0
5. This is a minimal, safe change: it only affects JOINs that are no longer referenced by any active part of the query

## Safety

- `_prune_unused_joins()` checks WHERE clause for Col references → WHERE JOINs preserved
- `_prune_unused_joins()` checks annotation_select (which is empty after clear) → no false preservation
- `_prune_unused_joins()` checks select and group_by → any remaining references preserved
- JOIN chain tracing ensures parent aliases are also preserved
- The `exists()` guard `if not (q.distinct and q.is_sliced)` means we only prune when annotations are actually stripped
- Existing public tests should continue to pass

## What NOT to change

- Do not modify the `_get_used_annotation_names` logic (it works correctly for count)
- Do not modify the `_prune_unused_joins` logic (it works correctly)
- Do not change the DISTINCT/COMBINATOR/GROUP BY handling
- Do not change the `get_aggregation` logic from v1
- Keep all v1 changes intact
