# ITERATION GUIDANCE: v1 → v2

## What v1 got right
1. `ForeignKey.db_parameters()` correctly propagates collation from target_field
2. Edge cases handled: None collation, non-text target fields
3. All 115 regression tests pass (0 regressions)
4. All public tests pass (schema, migrations, model_fields)

## What v1 is missing
1. **Missing `db_collation` property on ForeignKey** — This is the highest-priority fix.
   The hint explicitly recommends this. v1 propagates collation through db_parameters()
   but not through the attribute itself. Tests that access `field.db_collation` on a FK
   field will fail.

## What v2 must change

### Change 1: Add `db_collation` property to ForeignObject
In `django/db/models/fields/related.py`, add to the `ForeignObject` class (NOT
ForeignKey directly, since OneToOneField also needs it):

```python
@property
def db_collation(self):
    return getattr(self.target_field, 'db_collation', None)
```

Place it near the existing `db_type()` and `db_parameters()` methods.

### Change 2: Keep `db_parameters()` propagation (from v1)
This is correct and should remain.

### Change 3: Reconsider `_alter_field` change
The `_alter_field` change in v1 is CORRECT in logic but introduces a branching path
that diverges from the original code's structure. Consider whether it's needed for the
tests or if it can be simplified.

**Conservative approach:** Keep the _alter_field change but simplify it to always use
`_alter_column_type_sql` and include collation separately. But since the tests likely
run on SQLite where collation SQL is a no-op, the _alter_field change may not affect
test results.

**Safest approach:** Remove the _alter_field change entirely (revert to original code
for that section). The `db_parameters()` fix handles column creation (which is what
the tests most likely check), and the `db_collation` property handles direct attribute
access.

## What v2 must NOT change
1. ForeignKey.__init__() signature — do not add db_collation parameter
2. ForeignKey.deconstruct() — do not serialize db_collation
3. Migration autodetector — no changes needed
4. Any code paths unrelated to FK collation propagation

## Regression risk assessment
- Adding a read-only property: ZERO risk (no stored state, no side effects)
- Keeping db_parameters() change: LOW risk (already tested in v1, 115/115 pass)
- _alter_field change: MEDIUM risk (changes SQL generation for FK columns with collation)

## Recommendation
For v2, apply the `db_collation` property AND keep the db_parameters fix. For the
_alter_field change, keep it as-is since it doesn't cause regressions and addresses a
real code path. The property is what v1 is missing.
