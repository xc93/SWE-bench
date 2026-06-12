# v1 Notes

## Behavioral Change

v1 propagates `db_collation` from a primary key field to any ForeignKey (or OneToOneField) that references it. This ensures that when a CharField/TextField PK has `db_collation` set, the FK columns in referencing tables are created/altered with the same collation, preventing MySQL foreign key constraint errors due to collation mismatch.

## Files Modified

- `django/db/models/fields/related.py`: Added `db_collation` property to `ForeignKey` class that proxies to `self.target_field.db_collation`, and updated `db_parameters()` to include the collation in its return dict when present.

## Public Tests Run

- `schema` test suite: 179 tests passed, 28 skipped (all OK)
- `migrations` test suite: 657 tests passed, 1 skipped (all OK)
- `model_fields` test suite: 430 tests passed, 55 skipped (all OK)

## Why v1 Matches the Public Issue

The issue states that `db_collation` on a PK field is not propagated to FK columns, causing MySQL constraint errors. The root cause is that `ForeignKey.db_parameters()` only returns `type` and `check` but never includes `collation`. The schema editor checks `db_params.get("collation")` when generating column SQL and ALTER TABLE statements, so without this key, FK columns lack the collation clause. v1 fixes this by adding a `db_collation` property that reads from the target field and including it in `db_parameters()`.
