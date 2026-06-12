# SWE-bench Baseline: django__django-15957

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=211&length=1
- Repo: django/django
- Repo URL: https://github.com/django/django.git
- Instance ID: django__django-15957
- Base commit: f387d024fc75569d2a4a338bfda76cc2f328f627
- Base commit URL: https://github.com/django/django/commit/f387d024fc75569d2a4a338bfda76cc2f328f627
- Version: 4.2
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

`Prefetch` objects raise `TypeError: Cannot filter a query once a slice has been taken` when given a sliced queryset (e.g., `Post.objects.all()[:3]`). This is because the prefetch machinery internally calls `.filter()` on the provided queryset to add relationship constraints, and Django disallows filtering on sliced querysets. Users want to use sliced prefetch querysets to limit the number of related objects loaded per instance (e.g., show 3 example posts per category).

## Patch

- Files changed: `django/db/models/query.py`
- Behavioral change: When a `Prefetch` object receives a sliced queryset, the slice information (low_mark/high_mark) is extracted and stored separately, and the queryset's limits are cleared so that filtering can proceed normally. After prefetch results are grouped by instance, the saved slice is applied per-instance in Python. This means the database query fetches all matching related objects (without the LIMIT), but each instance's results are sliced to the requested range. This is a correct trade-off since SQL cannot express per-group LIMIT without window functions.
- Public tests run: `prefetch_related` (109 tests OK), `prefetch_related.test_prefetch_related_objects` (11 tests OK)
- Why this matches the public issue statement: The issue asks for `Prefetch` objects to work with sliced querysets instead of raising an error. This patch extracts the slice, allows filtering to proceed, and applies the slice per-instance when distributing results — exactly the approach suggested in the issue discussion ("extract it from the provided queryset to make it filterable again and apply it when in-memory joining").
