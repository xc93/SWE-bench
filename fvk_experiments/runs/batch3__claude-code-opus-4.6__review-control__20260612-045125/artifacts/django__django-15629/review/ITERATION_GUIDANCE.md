# Iteration Guidance for v2

## Retain from v1

Keep the `db_collation` property and updated `db_parameters()` on ForeignKey — these are correct and necessary for the column-creation path.

## Changes Needed for v2

### Change 1: Expand `drop_foreign_keys` condition in base schema editor

In `django/db/backends/base/schema.py`, add `or old_collation != new_collation` to the `drop_foreign_keys` condition. Move `old_collation`/`new_collation` computation earlier so they're available.

### Change 2: Handle collation changes in the `rels_to_update` loop

When collation changed, call `_alter_column_collation_sql` instead of `_alter_column_type_sql` for related FK columns.

### Change 3: Fix SQLite backend `_alter_field`

In `django/db/backends/sqlite3/schema.py`, the `_alter_field` method has its own FK rebuild condition at line 458. Add the same `or old_collation != new_collation` check. The `old_db_params` and `new_db_params` are already passed as parameters.

## Forbidden Changes

- Do NOT modify `_alter_column_type_sql` or `_alter_column_collation_sql` methods
- Do NOT modify CharField/TextField db_parameters behavior
- Do NOT modify migration autodetector
- Do NOT change how `rels_to_update` is populated for type-only changes
- Do NOT modify the SQLite `_remake_table` method

## Regression Risks

- The `drop_foreign_keys` change must still work for type-only changes
- The SQLite rebuild condition must still trigger for type-only changes
- Non-FK field alterations must not be affected
