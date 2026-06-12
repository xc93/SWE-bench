# SWE-bench Baseline: django__django-15503

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=194&length=1
- Repo: django/django
- Repo URL: https://github.com/django/django.git
- Instance ID: django__django-15503
- Base commit: 859a87d873ce7152af73ab851653b4e1c3ffea4c
- Base commit URL: https://github.com/django/django/commit/859a87d873ce7152af73ab851653b4e1c3ffea4c
- Version: 4.1
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

`has_key`, `has_keys`, and `has_any_keys` JSONField lookups fail to find keys that look like integers (e.g., `'1111'`) on SQLite, MySQL, and Oracle backends. The root cause is that `compile_json_path()` converts integer-looking string keys to array index syntax (`[1111]`) instead of object key syntax (`."1111"`). For `has_key` lookups, the RHS values are always object key names, never array indices.

## Patch

- Files changed: `django/db/models/fields/json.py`
- Behavioral change:
  1. In `HasKeyLookup.as_sql()`, non-KeyTransform RHS keys are now always formatted as JSON object keys (`.\"key\"`) instead of going through `compile_json_path()` which would convert numeric strings to array indices (`[index]`).
  2. `KeyTransformIsNull.as_sqlite()` and `KeyTransformIsNull.as_oracle()` were refactored to use `preprocess_lhs()` + `compile_json_path()` directly instead of delegating to `HasKey`, since `isnull` lookups need the original path traversal behavior (where numeric keys ARE array indices).
- Public tests run: `model_fields.test_jsonfield` - 87 tests, all pass (8 skipped for SQLite-unsupported features)
- Why this matches the public issue statement: The fix ensures that `data__has_key='1111'` generates the JSON path `$."1111"` (object key lookup) instead of `$[1111]` (array index lookup), matching the correct semantics for `has_key` and matching PostgreSQL's behavior.
