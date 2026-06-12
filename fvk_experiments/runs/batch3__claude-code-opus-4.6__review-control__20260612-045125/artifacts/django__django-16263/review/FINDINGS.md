# Review Findings: v1 Patch for django__django-16263

## 1. What is the intended public behavior change?

Strip unused annotations from count() and exists() queries. When a queryset has annotations that are not referenced by filters, other annotations, or ordering, those annotations should be excluded from the SQL query to avoid unnecessary GROUP BY, JOINs, and computation overhead.

## 2. Current behavior in implicated code paths

### `get_aggregation()` (count path)
- When annotations exist, a subquery is used with ALL annotations in the SELECT
- Aggregate annotations force GROUP BY on the primary key
- The GROUP BY + JOINs cause significant performance overhead even when the annotations are not needed for the count result

### `exists()` / `has_results()` path
- `exists()` calls `clear_select_clause()` which strips ALL annotations from the SELECT via `set_annotation_mask(())`
- However, JOINs introduced by the annotations **remain in the query** with positive `alias_refcount`
- The compiler's `get_from_clause()` includes JOINs with positive refcount, so unnecessary JOINs persist in the generated SQL
- This means `exists()` generates: `SELECT 1 FROM table JOIN unnecessary_table ON ... LIMIT 1`

## 3. What does the issue imply?

The issue explicitly mentions: "Same can be done for exists()". This means the optimization should cover both `count()` and `exists()`.

## 4-7. Non-regression analysis

### What must remain unchanged:
- Annotations used in filters must be preserved in count queries
- Annotations used by aggregation expressions must be preserved
- DISTINCT queries must preserve their SELECT annotations
- Combined queries (UNION, etc.) must preserve annotations
- GROUP BY tuple queries must preserve their GROUP BY expressions
- Sliced queries must preserve ordering-referenced annotations
- `exists()` on distinct+sliced queries preserves annotations (per the `if not (q.distinct and q.is_sliced)` guard)

### What v1 correctly preserves:
- WHERE clause annotation references (via identity check on annotation objects)
- Ref objects in aggregate expressions
- Annotations in DISTINCT and COMBINATOR queries
- GROUP BY tuple expressions
- Transitive annotation dependencies
- All 100 PASS_TO_PASS regression tests pass

## 8. What v1 gets right

- Correctly identifies unused annotations via `_get_used_annotation_names()`
- Uses identity check on annotation objects in the WHERE clause (correct because `resolve_ref()` returns the same object and QuerySet cloning preserves identity)
- Uses Ref detection for aggregate expressions (correct because aggregate resolution uses `summarize=True` which creates Ref objects)
- Implements transitive closure for annotation dependencies
- Prunes unused JOINs via `_prune_unused_joins()` using alias refcount recalculation
- Correctly handles DISTINCT, COMBINATOR, and GROUP BY edge cases
- All 100 PASS_TO_PASS tests pass (no regressions)
- 2 of 3 FAIL_TO_PASS tests pass

## 9. What v1 is missing

### Critical: `exists()` optimization is not implemented

The issue explicitly mentions: "Same can be done for exists()". The `exists()` method in `Query` already strips annotations from the SELECT via `clear_select_clause()`, but it does NOT prune the JOINs introduced by those annotations. Adding `_prune_unused_joins()` to `exists()` would complete the optimization.

Specifically, in `Query.exists()`:
```python
def exists(self, limit=True):
    q = self.clone()
    if not (q.distinct and q.is_sliced):
        ...
        q.clear_select_clause()
    ...
```

After `clear_select_clause()` clears all annotations, `_prune_unused_joins()` should be called to remove JOINs that are no longer needed by any active part of the query (only the WHERE clause at that point).

This is likely the cause of the 3rd hidden test failure (v1 passes 2/3 FAIL_TO_PASS).

### Minor: `_prune_unused_joins` could also check `order_by`

The `_prune_unused_joins` method checks WHERE, annotation_select, select, and group_by for used aliases. It does not check `order_by`. For sliced queries where ordering is preserved, annotations referenced in order_by should be checked. However, this is likely not the cause of the failing test since ordering is cleared in both `get_aggregation()` and `exists()`.

## 10. Exact minimal changes for v2

Add `q._prune_unused_joins()` to `Query.exists()` after `clear_select_clause()`:

```python
def exists(self, limit=True):
    q = self.clone()
    if not (q.distinct and q.is_sliced):
        if q.group_by is True:
            q.add_fields(...)
            q.set_group_by(allow_aliases=False)
        q.clear_select_clause()
        q._prune_unused_joins()   # <-- ADD THIS
    ...
```

## 11. Changes forbidden because they risk regressions

- Do NOT modify `exists()` behavior for `distinct and is_sliced` queries (annotations are preserved in that path)
- Do NOT strip annotations that are in the WHERE clause (they affect filter correctness)
- Do NOT remove JOINs referenced by the WHERE clause (they affect filter correctness)
- Do NOT change the subquery decision logic beyond the annotation stripping
- Do NOT modify `clear_select_clause()` itself (it's used elsewhere)
