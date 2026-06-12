# v1 Notes

## Behavioral Change

v1 modifies `Query.get_aggregation()` in `django/db/models/sql/query.py` to strip
unused annotations from the inner subquery's SELECT clause during count/aggregate
operations.

An annotation is considered "used" if it is referenced by:
- The WHERE clause (filters)
- The aggregate expressions being computed
- The SELECT clause
- The GROUP BY clause
- Other annotations that are themselves used (transitive closure)

Annotations that are not referenced by any of these are stripped from the inner
subquery's `annotation_select_mask`, so they are not included in the SELECT clause.
This avoids computing unnecessary aggregate expressions in the subquery.

## Files Modified

- `django/db/models/sql/query.py`
  - Added annotation usage detection logic in `get_aggregation()`
  - Added two static helper methods: `_collect_used_annotations()` and
    `_collect_used_expression_refs()` for walking WHERE trees and expression
    trees to find annotation references via object identity
  - Modified the inner query's `set_annotation_mask()` call to exclude unused
    annotations (only when not DISTINCT and not using set operations)

## Safety Guards

- When `self.distinct` is True, no annotations are stripped (they define the
  DISTINCT set)
- When `self.combinator` is set (UNION/INTERSECT), no annotations are stripped
- `existing_annotations` is NOT filtered — the subquery/GROUP BY logic is unchanged
- `has_existing_aggregate_annotations` still considers ALL existing annotations,
  so the GROUP BY override to PK still happens correctly

## Public Tests Run

- `aggregation` (116 tests): all pass
- `annotations` (116 tests): all pass (partial overlap)
- `queries` (460 tests): all pass
- `expressions` (158 tests): all pass

Total: 850 tests, 0 failures.

## Why v1 Matches the Public Issue

The issue requests stripping annotations not referenced by filters, other
annotations, or ordering from count queries. v1 identifies unused annotations
via object identity tracking through expression trees and removes them from
the subquery SELECT clause, reducing unnecessary computation.
