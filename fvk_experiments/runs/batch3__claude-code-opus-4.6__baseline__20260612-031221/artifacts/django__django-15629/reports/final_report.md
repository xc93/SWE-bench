# SWE-bench Baseline: django__django-15629

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=201&length=1
- Repo: django/django
- Repo URL: https://github.com/django/django.git
- Instance ID: django__django-15629
- Base commit: 694cf458f16b8d340a3195244196980b2dec34fd
- Base commit URL: https://github.com/django/django/commit/694cf458f16b8d340a3195244196980b2dec34fd
- Version: 4.1
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

When a CharField/TextField primary key has `db_collation` set, ForeignKey fields pointing to it do not propagate the collation to the database column. This causes MySQL foreign key constraint errors because the FK column and the referenced PK column have different collations. The generated SQL for FK columns is missing the `COLLATE` clause.

## Patch

- Files changed:
  - `django/db/models/fields/related.py` - Added `db_collation` property to `ForeignKey` that proxies the target field's `db_collation`, and updated `db_parameters()` to include collation in the returned dict.
  - `django/db/backends/base/schema.py` - Updated the related-field update loop in `_alter_field()` to use `_alter_column_collation_sql` (instead of `_alter_column_type_sql`) when the related FK field has a collation, ensuring FK columns get the correct COLLATE clause when the PK's collation changes.

- Behavioral change:
  - ForeignKey fields now inherit `db_collation` from their target field via a property.
  - `ForeignKey.db_parameters()` now includes `"collation"` in the returned dict when the target field has `db_collation` set.
  - When altering a PK that has `db_collation`, related FK columns are now updated with the correct collation via `_alter_column_collation_sql`.

- Public tests run:
  - schema tests: 179 passed, 28 skipped (SQLite limitations)
  - migration tests: 657 passed, 1 skipped
  - invalid_models tests: 272 passed, 13 skipped
  - model_fields tests (charfield, textfield): 18 passed

- Why this matches the public issue statement:
  The issue reports that FK columns don't get the COLLATE clause when pointing to a PK with `db_collation`. The root cause is that `ForeignKey.db_parameters()` didn't include collation information from the target field. The fix adds a `db_collation` property that proxies the target field's collation and includes it in `db_parameters()`, which the schema editor uses when generating column SQL. Additionally, the schema editor's related-field update path now correctly applies collation when updating FK columns during PK alterations.
