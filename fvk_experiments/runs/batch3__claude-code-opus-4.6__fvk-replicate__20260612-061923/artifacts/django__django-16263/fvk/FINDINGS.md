# FINDINGS

## F1: v1 only masks annotations from SELECT, doesn't remove from query

v1 modifies the annotation_select_mask but does not remove annotations from
`self.annotations`. This means:
- JOINs created by the annotation remain in the FROM clause
- GROUP BY entries remain (though overridden to PK when aggregate annotations exist)
- The subquery is still created (because `existing_annotations` check is unchanged)

Impact: The SQL still contains unnecessary JOINs and GROUP BY, which is the main
performance bottleneck identified in the issue.

## F2: alias_refcount is the key to JOIN removal

The compiler's `get_from_clause()` skips JOINs with `alias_refcount[alias] == 0`.
The refcounts are set during query construction (annotation resolution) and are NOT
automatically adjusted when annotations are masked out. To properly remove JOINs:
- Walk removed annotation expressions via `_gen_col_aliases()`
- Decrement alias_refcount for each table alias found
- JOINs with refcount reaching 0 are automatically excluded by the compiler

## F3: group_by must be cleaned when annotations are removed

After `annotate()`, `set_group_by()` populates group_by with:
- Model field Cols from `self.select`
- `Ref(alias, annotation)` for non-aggregate annotations
- `get_group_by_cols()` results for aggregate annotations (usually empty)

When removing annotations, their Ref entries must be removed from group_by.
Non-Ref group_by entries (model field Cols) should be preserved.

## F4: Empty group_by tuple still triggers subquery

`isinstance((), tuple)` is True, so an empty group_by tuple triggers the subquery
path. After removing all annotations and their group_by entries, if only empty
group_by remains, the query should ideally skip the subquery.

## F5: Aggregate filter expressions contain WhereNodes that reference annotations

Aggregate functions with `filter=` parameters (e.g., `Sum('price', filter=Q(anno__gt=5))`)
store the filter as a WhereNode in their expression tree. The `flatten()` method yields
the WhereNode but doesn't walk into it (WhereNode isn't a BaseExpression). The annotation
reference detection must recursively walk WhereNode children.

## F6: exists() also benefits from annotation stripping

The `exists()` method calls `clear_select_clause()` which clears the annotation mask,
but doesn't remove annotations from `self.annotations` or clean up JOINs. This means
unnecessary JOINs remain for exists() queries too.

## F7: The 'not distinct' and 'not combinator' guards are essential

When `distinct=True`, annotations in the SELECT define the DISTINCT set. Removing
them changes query semantics. Similarly for combinator queries (UNION/INTERSECT).
The v1 guards for these cases are correct and must be preserved.
