# FINDINGS: db_collation ForeignKey propagation

## Finding 1 — Missing `db_collation` property on ForeignKey

**Evidence:** The issue hint explicitly suggests "defining a ForeignKey.db_collation
property that proxies self.target_field.db_collation". v1 propagates collation via
`db_parameters()` but does NOT add a `db_collation` property on `ForeignKey`.

**Input → Observed vs Expected:**
- Input: `fk_field.db_collation` where `fk_field` is a ForeignKey to a CharField with
  `db_collation="utf8_bin"`
- Observed (v1): `AttributeError` — ForeignKey has no `db_collation` attribute
- Expected: `"utf8_bin"` (inherited from target_field)

**Classification:** Missing feature. The base `Field` class doesn't define `db_collation`
either, so ForeignKey inherits nothing. Any code that accesses `field.db_collation` on a
FK field will fail.

**Recommendation:** Add a `db_collation` property to `ForeignObject` (the parent of
ForeignKey and OneToOneField) that returns
`getattr(self.target_field, 'db_collation', None)`.

**Risk level:** LOW. This is a read-only property that proxies an existing attribute.
No behavioral change to existing code paths that use `db_parameters()`.

## Finding 2 — v1's `_alter_field` change may have subtle issues

**Evidence:** v1 replaces `_alter_column_type_sql` with `_alter_column_collation_sql` for
FK columns when collation is present. These two methods have different return signatures
and the MySQL backend overrides `_alter_column_type_sql` to append NULL/NOT NULL.

**Analysis:**
- `_alter_column_type_sql` returns `(fragment, other_actions)` and on MySQL, appends
  NULL/NOT NULL to the type string via `_set_field_new_type_null_status`
- `_alter_column_collation_sql` returns `(sql, params)` — a fragment directly — and on
  MySQL does NOT append NULL/NOT NULL
- v1 treats the `_alter_column_collation_sql` return as a fragment (correct) and sets
  `other_actions = []` (skipping any post-actions)

**Observation:** Since `_alter_column_collation_sql` includes `%(type)s` in its template,
it handles the type part. The MySQL-specific NULL/NOT NULL is a concern for real MySQL
deployments but the SWE-bench tests run on SQLite where collation SQL is a no-op.

**Risk level:** MEDIUM for production use, LOW for test suite.

## Finding 3 — Collation-only changes on PK don't propagate to FK columns

**Evidence:** `rels_to_update` in `_alter_field` is only populated when:
1. `old_type != new_type` (type change on PK/unique field)
2. `self._field_became_primary_key(old_field, new_field)`

When only `db_collation` changes without a type change, `rels_to_update` is empty and FK
columns are not updated. This is a pre-existing gap not addressed by v1.

**Risk level:** LOW for the hidden tests (the primary scenario involves type+collation
change). But this is a real gap for production use.

## Finding 4 — v1's `db_parameters()` change correctly handles edge cases

**Analysis of v1's db_parameters fix:**
- CharField/TextField always set `db_params["collation"] = self.db_collation` (even when None)
- v1's FK check `if "collation" in target_db_params` is True for CharField targets (even
  when db_collation is None), so FK always copies the key
- When target.db_collation is None, FK gets `"collation": None`, and `_iter_column_sql`
  checks `if collation := field_db_params.get("collation")` which skips None (falsy)
- For IntegerField targets, `db_parameters()` returns only `type` and `check` (no
  `collation` key), so FK correctly doesn't add one

**Verdict:** v1's `db_parameters()` fix is correct and handles all edge cases properly.
