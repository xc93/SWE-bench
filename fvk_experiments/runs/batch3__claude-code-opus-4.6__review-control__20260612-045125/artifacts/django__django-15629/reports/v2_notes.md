# v2 Notes

## How v2 Differs from v1

v2 retains all of v1's changes (ForeignKey `db_collation` property and updated `db_parameters()`) and adds changes to three files:

### 1. `django/db/backends/base/schema.py`
- **Expanded `drop_foreign_keys` condition**: Added `or old_collation != new_collation` so that collation changes on a PK/unique field also trigger FK constraint drops and FK column updates.
- **Collation-aware `rels_to_update` loop**: When collation changed, the loop now calls `_alter_column_collation_sql()` instead of `_alter_column_type_sql()` for each related FK column.
- **Moved `old_collation`/`new_collation` computation earlier**: Available for both the FK drop condition and the rels_to_update loop.

### 2. `django/db/backends/sqlite3/schema.py`
- **Expanded related table rebuild condition**: The SQLite `_alter_field` method overrides the base class entirely and has its own logic for rebuilding tables with FK references. Changed `old_type != new_type` to also check `old_collation != new_collation`, so related tables get rebuilt when a PK's collation changes.

## Which Review Findings Caused the Change

- Finding: `drop_foreign_keys` condition missed collation-only changes
- Finding: `rels_to_update` loop only handled type changes
- Discovery (post-initial-review): SQLite backend completely overrides `_alter_field` and has its own FK rebuild condition that also only checked type changes

## Regression Risks v2 Avoids

- All `else` branches preserve existing type-only change behavior
- The `or` conditions mean type-only changes still trigger FK updates
- All 179 schema tests, 657 migration tests, and 430 model_fields tests pass
