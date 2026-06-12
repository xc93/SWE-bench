# v2 Notes

## Changes from v1

Two changes based on the code review findings:

### 1. `exists()` JOIN pruning
Added `q._prune_unused_joins()` call in `Query.exists()` after `q.clear_select_clause()`. This prunes JOINs that were only needed by annotations that `clear_select_clause()` already strips from the SELECT. Addresses the issue's note: "Same can be done for exists()".

### 2. External column reference handling in `_prune_unused_joins()`
Changed `_prune_unused_joins()` to use `_gen_cols(active_exprs, include_external=True)` instead of `_gen_col_aliases(active_exprs)`. This ensures that subqueries with `OuterRef` references correctly preserve JOINs in the outer query that they depend on. Without `include_external=True`, `_gen_cols` doesn't call `get_external_cols()` on Subquery expressions, so outer-query JOINs referenced via OuterRef were incorrectly pruned.

## Files modified

- `django/db/models/sql/query.py`:
  - `exists()`: Added `q._prune_unused_joins()` after `q.clear_select_clause()`
  - `_prune_unused_joins()`: Changed to use `_gen_cols(active_exprs, include_external=True)` to find all column references including external ones from subqueries

## Public tests run

- aggregation (116 tests) - all pass
- annotations (82 tests) - all pass (2 skipped)
- queries (468 tests) - all pass (13 skipped, 2 expected failures)
- expressions (184 tests) - all pass (1 skipped)
- lookup, ordering, distinct_on_fields, defer (156 tests) - all pass (11 skipped)
- Total: 1006 tests pass, 0 failures
