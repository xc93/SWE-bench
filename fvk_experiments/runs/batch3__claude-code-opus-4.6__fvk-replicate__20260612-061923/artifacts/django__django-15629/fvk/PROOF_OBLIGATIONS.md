# PROOF OBLIGATIONS

## Bug-fix obligations (must hold after patch)

### O1: ForeignKey.db_collation returns target's collation
For any FK field `f` referencing a CharField/TextField `t` with `db_collation=C`:
- `f.db_collation == C` when C is not None
- `f.db_collation is None` when `t` has no `db_collation` or `t` is not a text field

### O2: ForeignKey.db_parameters includes collation
For any FK field `f` referencing a field `t`:
- `f.db_parameters(conn)["collation"] == t.db_collation` when `t` has `db_collation`
- `"collation" not in f.db_parameters(conn)` when `t` is IntegerField/BigAutoField/etc.

### O3: CREATE TABLE SQL includes COLLATE on FK columns
When creating a table with FK referencing a field with db_collation, the column_sql
output includes the COLLATE clause.

### O4: ALTER TABLE propagates collation to FK columns
When altering a PK/unique field (with type change) and it has collation, FK columns
are altered to include the collation.

## Non-regression obligations (must remain unchanged)

### R1: FK to IntegerField PK unchanged
`ForeignKey.db_parameters()` for FK referencing BigAutoField/IntegerField must return
the same dict as before the patch (no "collation" key).

### R2: _alter_column_type_sql still used for non-collation FK columns
When FK column references a PK without collation, `_alter_column_type_sql` must still
be called (not `_alter_column_collation_sql`).

### R3: Existing schema test suite passes (179 tests)
### R4: Existing migration test suite passes (657 tests)
### R5: Existing model_fields test suite passes (430 tests)

### R6: No changes to migration serialization
ForeignKey.deconstruct() must NOT include `db_collation` (it's inherited, not stored).

### R7: No changes to ForeignKey.__init__
ForeignKey should NOT accept `db_collation` as a constructor argument.

### R8: Property, not stored attribute
The `db_collation` on ForeignKey must be a read-only property, not a stored attribute.
This ensures it always reflects the current target field's collation, not a stale value.
