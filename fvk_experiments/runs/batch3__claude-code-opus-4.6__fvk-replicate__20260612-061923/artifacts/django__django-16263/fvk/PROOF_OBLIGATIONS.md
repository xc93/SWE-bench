# PROOF OBLIGATIONS

## PO1: Annotations used by WHERE must be preserved

If an annotation is referenced in the WHERE clause (filter), removing it would cause
the filter to reference a nonexistent expression, breaking the query.

## PO2: Annotations used by aggregate expressions must be preserved

If an aggregate (like Sum('annotation_name')) references an annotation, that annotation
must remain in the query for the aggregate to compute correctly.

## PO3: Annotations used by aggregate filters must be preserved

Aggregate functions with filter= parameters contain WhereNodes. Annotations referenced
inside these WhereNodes must be preserved.

## PO4: Transitive annotation dependencies must be preserved

If annotation B references annotation A, and B is used, then A must also be preserved.

## PO5: Annotations in SELECT (via values/values_list) must be preserved

When the query uses values()/values_list() to select specific annotation columns,
those annotations must be preserved.

## PO6: Annotations in GROUP BY must be preserved

If an annotation has a Ref in group_by that is genuinely needed for correct grouping
(e.g., creates JOINs that multiply rows), removing it changes the result.

## PO7: DISTINCT queries must preserve all selected annotations

When self.distinct is True, all annotations in annotation_select define the DISTINCT
set. Removing any changes the result.

## PO8: Combinator queries must preserve all annotations

UNION/INTERSECT require matching column sets. Removing annotations would break this.

## PO9: alias_refcount must be correctly adjusted

When removing an annotation, the alias_refcount for its table aliases must be
decremented. Failure to do so leaves unnecessary JOINs in the query.

## PO10: group_by must be correctly cleaned

When removing an annotation, its Ref entry must be removed from group_by. A dangling
Ref would reference a nonexistent alias in the SQL.

## PO11: 100 PASS_TO_PASS tests must continue passing

The fix must not change behavior for any existing query patterns, including:
- Queries with used annotations (filters, aggregates)
- Queries with DISTINCT
- Queries with combinators
- Queries with slicing
- Queries with subquery annotations
- Queries with multivalued relation annotations

## PO12: annotation_select_cache must be invalidated after changes

The `_annotation_select_cache` is populated lazily. After modifying `self.annotations`
or `annotation_select_mask`, the cache must be invalidated.
