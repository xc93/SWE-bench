# SPEC: Strip unused annotations from count/aggregate queries

## Intended Public Behavior Change

When `count()` or `exists()` is called on a queryset with annotations, annotations
that are not referenced by filters (WHERE/HAVING), the aggregate expressions, other
used annotations, the SELECT clause, or GROUP BY should be completely removed from
the aggregation subquery. This includes removing them from the SELECT clause, the
GROUP BY clause, and any JOINs they created.

## Current Behavior

`Query.get_aggregation()` always includes all existing annotations in the inner
subquery when constructing count/aggregate queries. This forces:
- Unnecessary aggregate computations (e.g., `COUNT(chapters.id)`)
- Unnecessary JOINs to related tables
- Unnecessary GROUP BY clauses
- Subquery creation even when no annotations are needed

## Scope

The fix applies to `Query.get_aggregation()` which is called by:
- `QuerySet.count()` via `Query.get_count()`
- `QuerySet.aggregate()` via `Query.get_aggregation()`
- `QuerySet.exists()` (indirectly, via `has_results` → `exists()`)

## What Must Change

1. Identify which annotations are referenced by WHERE, HAVING, aggregates, SELECT,
   GROUP BY, or other referenced annotations (transitive closure)
2. Remove unreferenced annotations from `self.annotations`
3. Unref table aliases used only by removed annotations
4. Remove GROUP BY entries for removed annotations
5. If group_by becomes empty tuple after cleanup, the subquery condition should
   handle this correctly

## What Must NOT Change

- Queries with DISTINCT must preserve all annotations in annotation_select_mask
- Queries with combinators (UNION/INTERSECT) must preserve annotations
- The has_existing_aggregate_annotations check must use the ORIGINAL existing
  annotations (before stripping) to correctly set GROUP BY to PK
- Annotations referenced by WHERE clauses must be preserved
- Annotations referenced by aggregate expressions (including their filters) must
  be preserved
- Annotations referenced by other needed annotations must be preserved
