# v1 Notes

## What behavior v1 changes

v1 strips unused annotations from count/aggregate queries. When `QuerySet.annotate(...).count()` is called and the annotations are not referenced by filters, other annotations, or the aggregate expression, they are removed from the inner subquery's SELECT clause and their JOINs are pruned. This avoids unnecessary GROUP BY and JOINs, dramatically improving performance for annotated count queries.

## Files modified

- `django/db/models/sql/query.py`:
  - Modified `get_aggregation()` to determine which annotations are used and strip unused ones from the annotation mask
  - Added `_get_used_annotation_names()` method to walk WHERE clause and aggregate expressions to find referenced annotations
  - Added `_prune_unused_joins()` method to recalculate alias refcounts and exclude JOINs from stripped annotations

## Public tests run

- `aggregation.tests` (116 tests) - all pass
- `annotations` (82 tests) - all pass (2 skipped)
- `queries` (468 tests) - all pass (13 skipped, 2 expected failures)
- `expressions` (various), `lookup`, `ordering`, `distinct_on_fields`, `defer` (340 tests) - all pass

## Why v1 matches the public issue statement

The issue requests stripping unused annotations from count queries. The example given is:
```python
Book.objects.annotate(Count('chapters')).count()
```

This should produce the same result as `Book.objects.count()` but currently includes unnecessary `Count('chapters')` in the subquery, forcing GROUP BY.

v1 detects that `Count('chapters')` is not referenced by any filter or aggregate, strips it from the inner query, and prunes the associated JOINs. The query becomes a simple `SELECT COUNT(*) FROM books` with no subquery.

The same optimization applies to `.aggregate()` calls with unused annotations.

Annotations that ARE referenced by filters (WHERE/HAVING) or by the aggregate expressions are correctly preserved.

Special cases handled:
- DISTINCT queries: annotations in the SELECT are preserved (they determine distinctness)
- Combinator queries (UNION, etc.): annotations preserved (SELECT must match)
- GROUP BY tuple: expressions in group_by are checked for annotation references
- Transitive closure: if annotation A is used and references annotation B, both are kept
