# SWE-bench Baseline: django__django-16263

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=223&length=1
- Repo: django/django
- Repo URL: https://github.com/django/django.git
- Instance ID: django__django-16263
- Base commit: 321ecb40f4da842926e1bc07e11df4aabe53ca4b
- Base commit URL: https://github.com/django/django/commit/321ecb40f4da842926e1bc07e11df4aabe53ca4b
- Version: 4.2
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

When calling `.count()` or `.exists()` on a queryset that has annotations (e.g., `Book.objects.annotate(Count('chapters')).count()`), Django includes all annotations in the subquery even if they are not referenced by any filter, ordering, or other annotation. This leads to unnecessary computation, JOINs, and GROUP BY clauses. The fix strips annotations that are not referenced by the query's WHERE clause, ORDER BY, or by other used annotations, from count and exists queries.

## Patch

- Files changed: `django/db/models/sql/query.py`
- Behavioral change:
  - `get_aggregation()`: Before building the inner subquery, computes which annotations are actually referenced (by WHERE, ORDER BY, other annotations, or the aggregation expressions themselves) and masks out unused annotations. The `has_existing_aggregate_annotations` check is computed from the original annotations before stripping, preserving correct GROUP BY behavior.
  - `exists()`: Before resolving GROUP BY, masks out unused annotations so they don't contribute unnecessary GROUP BY columns.
  - New private method `_get_used_annotation_aliases()` walks expression trees (including WhereNode children) to find annotation references via object identity and Ref nodes, with transitive closure over annotation dependencies.
- Public tests run: aggregation, aggregation_regress, annotations, queries, expressions, expressions_window, ordering, lookup, prefetch_related, select_related, queryset_pickle, db_functions, extra_regress, model_regress, basic, delete, update, get_earliest_or_latest, distinct_on_fields (1800+ tests, all passing)
- Why this matches the public issue statement: The issue requests that Django strip unused annotations from count (and exists) queries. This patch does exactly that by analyzing which annotations are actually referenced and masking out the rest before the subquery is built.
