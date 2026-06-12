# SPEC: db_collation propagation to ForeignKey fields

## Intended Behavior Change

When a `CharField` or `TextField` with `db_collation` is used as a primary key (or unique
field) and other models reference it via `ForeignKey` or `OneToOneField`, the FK columns
must inherit the same `db_collation`. This ensures:

1. **Column creation (CREATE TABLE)**: FK columns include the `COLLATE` clause
2. **Column alteration (ALTER TABLE)**: When a PK field's collation changes, FK columns
   are updated to match
3. **Attribute access**: `ForeignKey.db_collation` returns the target field's `db_collation`

## Preconditions

- The target field (the one being referenced) must be a `CharField` or `TextField` with
  `db_collation` set
- The database backend must support collation (`supports_collation_on_charfield` or
  `supports_collation_on_textfield`)

## Postconditions

### P1: ForeignKey.db_collation property
`ForeignKey.db_collation` == `ForeignKey.target_field.db_collation` for all FK fields.
When target has no `db_collation`, returns `None`.

### P2: ForeignKey.db_parameters() includes collation
`ForeignKey.db_parameters(connection)` returns a dict that includes
`"collation": <target_field.db_collation>` when the target field has collation.

### P3: Column SQL includes COLLATE for FK columns
When creating a table with FK columns referencing a field with `db_collation`,
the generated SQL includes the COLLATE clause on the FK column.

### P4: ALTER TABLE propagates collation to FK columns
When altering a PK/unique field to add/change `db_collation`, the FK columns
referencing it are also altered to include the matching collation.

## Non-regression Obligations

### N1: FK columns referencing fields WITHOUT db_collation must be unchanged
`db_parameters()` for FK referencing IntegerField/BigAutoField/etc. must NOT include
a `collation` key, preserving existing behavior.

### N2: Existing schema editor behavior must be preserved
`_alter_column_type_sql` must still be called for FK columns without collation.
The `_alter_field` method's handling of type changes, null changes, default changes,
unique changes, and index changes must be unaffected.

### N3: Migration operations must remain stable
No changes to migration autodetection, serialization, or state should be introduced.

### N4: All existing public tests must pass
179 schema tests, 657 migration tests, 430 model_fields tests.
