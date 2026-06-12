# Review Findings for v1 Patch (django__django-15629)

## 1. Intended Public Behavior Change

When a CharField/TextField primary key has `db_collation` set, all ForeignKey and OneToOneField columns referencing that PK must be created/altered with the same collation. This prevents MySQL foreign key constraint errors caused by collation mismatch between PK and FK columns.

## 2. Current Behavior in Implicated Code Paths

- `ForeignKey.db_parameters()` returns only `type` and `check`, never `collation`
- Schema editor's `_iter_column_sql()` checks `field_db_params.get("collation")` to add COLLATE clause
- Base schema editor's `_alter_field()` at line 826-833 only triggers FK column updates when `old_type != new_type`
- The `rels_to_update` loop at line 1038-1053 only calls `_alter_column_type_sql()`, never `_alter_column_collation_sql()`
- **SQLite schema editor's `_alter_field()` completely overrides the base class** and has its own FK rebuild logic at line 458 that also only checks `old_type != new_type`

## 3. What v1 Got Right

- Added `db_collation` property to ForeignKey that proxies `self.target_field.db_collation`
- Updated `db_parameters()` to include `collation` key when present
- This correctly handles **column creation**: when a new FK column is created via `column_sql()` → `_iter_column_sql()`, it will now include the COLLATE clause
- All 115 regression tests pass
- 1 of 2 bug tests passes (the creation-path test)

## 4. What v1 is Missing

### Missing Fix A: Base schema editor `_alter_field` doesn't propagate collation changes to FK columns

**Gap A1: `drop_foreign_keys` condition**
When only collation changes (not type), `old_type == new_type`, so `drop_foreign_keys` is False and `rels_to_update` is never populated.

**Gap A2: `rels_to_update` loop only handles type changes**
Even if populated, the loop only calls `_alter_column_type_sql()`, never `_alter_column_collation_sql()`.

### Missing Fix B: SQLite backend `_alter_field` also misses collation changes

The SQLite `_alter_field` method at line 425 completely overrides the base class. It has its own related table rebuild logic at line 458:
```python
if new_field.unique and old_type != new_type:
```
This also only checks type changes, missing collation changes. Since the evaluator likely runs on SQLite, this is why v1 fails the second test.

## 5. What Must Remain Unchanged

- `CharField.db_parameters()` and `TextField.db_parameters()` behavior
- Base `Field.db_parameters()` behavior
- `_alter_field` behavior for non-collation changes
- The `_alter_column_type_sql()` and `_alter_column_collation_sql()` methods themselves
- All existing schema, migration, model_fields tests
- Foreign key constraint drop/recreate logic for type-only changes
- M2M field handling
- SQLite table remake logic for type-only changes

## 6. Risk Assessment

Modifications to `drop_foreign_keys` and the SQLite rebuild condition are medium-risk. The fix must handle:
- Collation-only changes (type stays same)
- Type-only changes (existing behavior, must not regress)
- Both type and collation changes simultaneously
- Collation removal (set to None)
