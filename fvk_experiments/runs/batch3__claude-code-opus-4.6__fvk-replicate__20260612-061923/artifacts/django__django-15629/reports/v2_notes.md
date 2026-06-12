# v2 Notes

## Difference from v1
v2 extends v1 with three additional changes identified through FVK analysis:

1. **`ForeignKey.db_collation` property** — FVK Finding 1 identified that v1 propagated
   collation through `db_parameters()` but not through the `db_collation` attribute directly.
   Code accessing `field.db_collation` on FK fields would get `AttributeError`.

2. **`drop_foreign_keys` condition extended** — FVK Finding 3 identified that collation-only
   changes on PK/unique fields would not trigger FK constraint dropping and rebuilding.
   The condition `old_type != new_type` was broadened to
   `old_type != new_type or old_collation != new_collation`.

3. **SQLite `_alter_field` FK rebuild** — The SQLite schema editor's condition for rebuilding
   related tables with FKs (`new_field.unique and old_type != new_type`) had the same gap.
   Extended to also trigger on collation changes.

## Changes from v1
1. **Added** `ForeignKey.db_collation` property (new in v2)
2. **Added** `drop_foreign_keys` collation awareness in base schema editor (new in v2)
3. **Added** SQLite `_alter_field` FK rebuild collation awareness (new in v2)
4. **Kept** `ForeignKey.db_parameters()` collation propagation (from v1)
5. **Kept** `_alter_field` FK column collation handling in base schema editor (from v1)

## Files Modified
1. `django/db/models/fields/related.py` — Added `db_collation` property and `db_parameters()`
   propagation on `ForeignKey`
2. `django/db/backends/base/schema.py` — Extended `drop_foreign_keys` to consider collation;
   `_alter_field()` handles collation when updating FK columns; moved collation variable
   computation earlier to avoid duplication
3. `django/db/backends/sqlite3/schema.py` — Extended FK table rebuild condition to include
   collation changes

## FVK Findings that drove changes
- **Finding 1 (Missing db_collation property):** Led to adding the property
- **Finding 3 (Collation-only PK changes don't propagate):** Led to extending
  `drop_foreign_keys` and SQLite rebuild conditions

## Public tests passed
- schema: 179 OK
- migrations: 657 OK
- model_fields: 430 OK
