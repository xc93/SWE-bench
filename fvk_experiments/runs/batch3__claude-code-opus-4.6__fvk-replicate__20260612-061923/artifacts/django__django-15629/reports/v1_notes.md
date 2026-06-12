# v1 Notes

## Behavioral Change
When a ForeignKey references a field (e.g. CharField PK) with `db_collation`, the FK column now inherits the collation. Previously, the collation was silently dropped on FK columns, causing MySQL constraint errors when adding FK constraints between columns with mismatched collations.

## Files Modified
1. `django/db/models/fields/related.py` — `ForeignKey.db_parameters()` now propagates `collation` from `target_field.db_parameters()`
2. `django/db/backends/base/schema.py` — `_alter_field()` now uses `_alter_column_collation_sql` for FK columns that have a collation, instead of `_alter_column_type_sql`

## Public Tests Run
- `tests/runtests.py schema` — 179 tests, all pass (28 skipped)
- `tests/runtests.py migrations` — 657 tests, all pass (1 skipped)
- `tests/runtests.py model_fields` — 430 tests, all pass (55 skipped)

## Rationale
The public issue describes MySQL foreign key constraint errors when `db_collation` is set on a PK CharField. The root cause is that `ForeignKey.db_parameters()` returns only `type` and `check`, omitting `collation`. The schema editor's `_iter_column_sql` and `_alter_field` both branch on the `collation` key in `db_parameters`, so without it, FK columns are created/altered without collation. The fix propagates collation from the target field and ensures the schema editor uses `_alter_column_collation_sql` for FK columns with collation.
